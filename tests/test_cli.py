"""Test argument parsing"""

import logging
import os
from pathlib import Path
from textwrap import dedent

import click
import pytest
from click.testing import CliRunner

from rpmlb import LOG
from rpmlb.cli import run


@pytest.fixture
def runner():
    r = CliRunner()
    try:
        with r.isolated_filesystem():
            yield r
    finally:
        # Make sure other tests are not affected by the ones with --verbose
        LOG.setLevel(logging.INFO)


@pytest.fixture
def recipe_path(tmpdir):
    """Test recipe file path"""

    with tmpdir.as_cwd():
        path = Path.cwd().resolve() / 'recipe.yml'

        # Fill in valid but empty recipe content
        with path.open(mode='w', encoding='utf-8') as outfile:
            contents = dedent('''\
                test:
                    name: Test recipe
                    requires: []
                    packages:
                        - test
                ''')
            print(contents, file=outfile)

        yield path


@pytest.fixture
def recipe_arguments(recipe_path):
    """Common recipe arguments: Path to the recipe file and recipe name."""

    return [str(recipe_path), 'test']


@pytest.mark.parametrize('option', ('recipe_file', 'recipe_name', 'build',
                                    'download', 'branch', 'source_directory'))
def test_parse_argv_no_options(tmpdir, option):
    """Tests proper default values of the CLI"""

    recipe_file = tmpdir.join('ror.yml')
    recipe_name = 'rh-ror50'

    # Prepare environment
    recipe_file.write('')

    current_dir = os.path.abspath(os.getcwd())

    expected = {
        'recipe_file': str(recipe_file),
        'recipe_name': str(recipe_name),
        'build': 'dummy',
        'download': 'none',
        'branch': None,
        'source_directory': current_dir,
    }

    # Parse the arguments
    with tmpdir.as_cwd():
        argv = list(map(str, [recipe_file, recipe_name]))
        args = run.make_context('rpmlb', argv).params

    assert args[option] == expected[option]


@pytest.mark.parametrize('verbose', (True, False))
def test_log_verbosity(runner, verbose):
    """Ensure that the verbosity is set properly on."""

    # Initial state – if the test fails here, the app has changed
    # and the test needs to be adjusted.
    assert LOG.getEffectiveLevel() == logging.INFO

    recipe = Path('recipe.yml')
    recipe.touch()

    verbose_args = ['--verbose'] if verbose else []
    level = logging.DEBUG if verbose else logging.INFO

    runner.invoke(run, verbose_args + [str(recipe), 'test'])
    assert LOG.getEffectiveLevel() == level


@pytest.fixture(params=('work-directory', 'custom-file'))
def path_kind(request):
    return request.param


def path_options(path_kind):
    """Excepted environment for the path tests"""
    filename = 'custom.yml' if path_kind == 'custom-file' else path_kind

    root = Path.cwd().resolve()
    path = root/filename

    options = ['--' + path_kind, str(path)]

    assert not path.exists()

    return path, options


def test_path_nonexistent(runner, path_kind, recipe_arguments):
    path, options = path_options(path_kind)

    with pytest.raises(click.BadParameter):
        run.make_context('test-{}-nonexistent'.format(path_kind),
                         options + recipe_arguments)


def test_path_expected_and_absolute(runner, path_kind, recipe_arguments):
    path, options = path_options(path_kind)

    if path_kind.endswith('directory'):
        path.mkdir()
    else:
        path.touch(mode=0o600)

    ctx = run.make_context('test-{}-ok'.format(path_kind),
                           options + recipe_arguments)
    result = Path(ctx.params[path_kind.replace('-', '_')])
    assert result == path
    assert result.is_absolute()


def test_path_bad_permissions(runner, path_kind, recipe_arguments):
    path, options = path_options(path_kind)

    if path_kind.endswith('directory'):
        # unwritable directory
        path.mkdir()
        path.chmod(0o500)
    else:
        # unreadable file
        path.touch(mode=0o200)

    with pytest.raises(click.BadParameter):
        run.make_context('test-{}-bad-permissions'.format(path_kind),
                         options + recipe_arguments)


def test_resume_conversion(runner, recipe_arguments):
    """Resume is converted into integer value."""

    options = ['--resume', '42']
    ctx = run.make_context('test-resume-conversion',
                           options + recipe_arguments)

    assert isinstance(ctx.params['resume'], int)


def test_invalid_resume(runner, recipe_arguments):

    options = ['--resume', 'start']

    with pytest.raises(click.BadParameter):
        run.make_context('test-resume-error', options + recipe_arguments)


@pytest.mark.parametrize('option,value', [
    ('branch', 'sclo7-rh-nodejs4-el7'),
    ('mock-config', 'default'),
    ('copr-repo', 'scratch-ror5'),
])
def test_simple_options(runner, recipe_arguments, option, value):
    """Specific option values are passed unprocessed."""

    options = ['--' + option, value]
    ctx = run.make_context('test-{}-passing'.format(option),
                           options + recipe_arguments)

    assert ctx.params[option.replace('-', '_')] == value
