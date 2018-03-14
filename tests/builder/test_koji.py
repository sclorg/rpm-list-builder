"""Tests for the KojiBuilder"""

import shutil
from collections import namedtuple
from itertools import zip_longest
from logging import DEBUG
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock

import pytest

from rpmlb.builder.koji import KojiBuilder
from rpmlb.logging import configure_logging
from rpmlb.recipe import Recipe
from rpmlb.work import Work


@pytest.fixture(
    params=[
        ('tests/fixtures/specfiles/minimal.spec', 'test.spec'),
        ('tests/fixtures/specfiles/metapackage.spec', 'rh-ror50.spec'),
    ],
    ids=[
        'minimal',
        'metapackage'
    ],
)
def spec_path(request, tmpdir):
    """Provide a SPEC file path according to parameter."""

    # Copy the SPEc to temporary directory
    source = Path(request.param[0])
    target = Path(str(tmpdir), request.param[1])

    shutil.copyfile(str(source), str(target))  # no support for pathlib :(

    with tmpdir.as_cwd():
        yield target


@pytest.fixture
def spec_contents(spec_path):
    """Provide text contents of a minimal spec file"""

    with spec_path.open() as istream:
        return istream.read()


@pytest.fixture
def collection_id():
    """Testing collection identification"""

    return 'rh-ror50'


@pytest.fixture
def work(valid_recipe_path, collection_id):
    """Provide Work instance."""

    valid_recipe = Recipe(str(valid_recipe_path), collection_id)
    return Work(valid_recipe)


@pytest.fixture(params=[
    KojiBuilder.DEFAULT_TARGET_FORMAT,
    'test-target',
    'fedora-{collection}-epel{epel}',
])
def target_format(request):
    """Koji target format"""

    return request.param


@pytest.fixture(params=list(range(6, 8)))
def epel(request):
    """EPEL version number"""

    return request.param


@pytest.fixture
def builder(work, epel):
    """Provide minimal KojiBuilder instance."""

    return KojiBuilder(work, koji_epel=epel, koji_owner='test-owner')


@pytest.fixture(params=[None, 'koji', 'cbs'])
def profile(request):
    """Koji profile name"""

    return request.param


@pytest.fixture(params=[True, False])
def scratch_build(request):
    """Scratch build indicator"""

    return request.param


@pytest.fixture
def cli_parameters(target_format, epel, profile, scratch_build):
    """Builder parameters as coming from the CLI"""

    return {
        'koji_epel': epel,
        'koji_owner': 'test-owner',
        'koji_profile': profile,
        'koji_target_format': target_format,
        'koji_scratch': scratch_build,

        # Extra parameter to assure the builder can take them
        'copr_repo': 'test/example',
    }


@pytest.fixture
def mock_runner(monkeypatch):
    """Mock shell command runner with command recording."""

    runner = Mock(return_value=None)
    monkeypatch.setattr('rpmlb.builder.koji.run_cmd', runner)
    monkeypatch.setattr('rpmlb.builder.koji.run_cmd_with_capture', runner)

    # Also patch _make_srpm which fails if runner has no side effect
    mock_srpm = Mock(return_value=Path('test.src.rpm'))
    monkeypatch.setattr(KojiBuilder, '_make_srpm', mock_srpm)

    return runner


def test_init_sets_attributes(work, cli_parameters):
    """Ensure that the parameters are set to appropriate values."""

    builder = KojiBuilder(work, **cli_parameters)

    assert builder.collection == work._recipe._collection_id
    assert builder.epel == cli_parameters['koji_epel']
    assert builder.owner == cli_parameters['koji_owner']
    assert builder.profile == cli_parameters['koji_profile']
    assert builder.target_format == cli_parameters['koji_target_format']
    assert builder.scratch_build == cli_parameters['koji_scratch']


@pytest.mark.parametrize('required', ['koji_epel', 'koji_owner'])
def test_init_checks_parameters(required, work, cli_parameters):
    """Ensure that required parameters are checked by __init__."""

    del cli_parameters[required]

    with pytest.raises(ValueError):
        KojiBuilder(work, **cli_parameters)


@pytest.mark.parametrize('profile,expected_command', [
    (None, ['koji']),
    ('koji', ['koji', '--profile', 'koji']),
    ('cbs', ['koji', '--profile', 'cbs']),
])
def test_base_command_respect_profile(builder, profile, expected_command):
    """Ensure that the base_command attribute respects profile attribute."""

    builder.profile = profile
    assert builder.base_command == expected_command


def test_default_format_is_used(work, epel):
    """Default format is used when no target format is specified."""

    parameters = {
        'koji_epel': epel, 'koji_owner': 'test-owner',  # required
        'koji_target_format': None,  # explicit None => should use default
    }

    builder = KojiBuilder(work, **parameters)
    assert builder.target_format == KojiBuilder.DEFAULT_TARGET_FORMAT


@pytest.mark.parametrize('collection', ['test', 'rh-ror50'])
def test_target_respects_format(
    builder, target_format, collection, epel
):
    """Ensure that the target is properly constructed from parameters."""

    builder.target_format = target_format
    builder.collection = collection
    builder.epel = epel

    expected_target = target_format.format(collection=collection, epel=epel)
    assert builder.target == expected_target


def test_make_srpm_creates_srpm(builder, spec_path, collection_id, epel):
    """Ensure that make_srpm works as expected"""

    configure_logging(DEBUG)

    arguments = {
        'name': spec_path.stem,
        'collection': collection_id,
        'epel': epel,
    }

    possible_names = {
        # Metapackage
        '{collection}-1-1.el{epel}.src.rpm'.format_map(arguments),
        # Regular package
        '{collection}-{name}-1.0-1.el{epel}.src.rpm'.format_map(
            arguments,
        ),
    }

    srpm_path = builder._make_srpm(arguments['name'])

    assert srpm_path.exists(), srpm_path
    assert srpm_path.name in possible_names


def test_missing_spec_is_reported(tmpdir, builder):
    """make_srpm does not attempt to build nonexistent SPEC file"""

    configure_logging(DEBUG)

    with tmpdir.as_cwd(), pytest.raises(FileNotFoundError):
        builder._make_srpm(name='test')


def test_prepare_adjusts_bootstrap_release(builder, spec_contents):
    """Release is adjusted on bootstrap build."""

    lines = spec_contents.splitlines(keepends=True)
    lines = builder.prepare_extra_steps(lines, {
        'name': 'test',
        'bootstrap_position': 1,
    })

    release_line, = filter(lambda l: l.startswith('Release:'), lines)

    assert '.bs01%{?dist}' in release_line


@pytest.mark.parametrize('scratch,expected_commands', [
    (True, ['koji add-pkg', 'koji build']),
    (False, ['koji add-pkg', 'koji build', 'koji wait-repo']),
])
def test_build_emit_correct_commands(
    monkeypatch, mock_runner, builder, scratch, expected_commands
):
    """Builder emits expected commands on build."""

    # Provide hardcoded destination tag
    monkeypatch.setattr(KojiBuilder, '_destination_tag', 'test_tag_name')

    builder.scratch_build = scratch
    builder.build({'name': 'test'})

    commands = mock_runner.call_args_list
    command_pairs = zip_longest(commands, expected_commands)
    assert all(cmd.startswith(exp) for cmd, exp in command_pairs), commands


def test_destination_tag_parsed_correctly(mock_runner, builder):
    """Assert that the destination tag is correctly extracted from output."""

    # Simulate output of `koji list-targets`
    mock_runner.return_value = namedtuple(
        'MockCommandOutput', ['stdout', 'stderr']
    )(
        stderr=b'',
        stdout=dedent('''\
        Name                Buildroot           Destination
        ----------------------------------------------------------
        test-target         test-target-build   test-tag-candidate
        ''').encode('utf-8')
    )

    builder.target_format = 'test-target'
    assert builder._destination_tag == 'test-tag-candidate'


def test_add_package_respects_owner(monkeypatch, mock_runner, builder):
    """Assert that the owner is used by the _add_package method."""

    monkeypatch.setattr(
        KojiBuilder, '_destination_tag', 'test-destination'
    )

    builder.owner = 'expected-owner'
    builder._add_package(name='test')

    assert mock_runner.call_count == 1

    cmd = mock_runner.call_args[0][0]
    assert '--owner' in cmd
    assert builder.owner in cmd


@pytest.mark.parametrize('package_name,expected', [
    ('rh-ror50', 'rh-ror50'),
    ('ruby', 'rh-ror50-ruby'),
])
def test_full_name_is_resolved_correctly(builder, package_name, expected):
    """Ensure the correct form of full package name."""

    assert builder._full_package_name(package_name) == expected
