import re
import sys
from collections import Counter
from pathlib import Path
from unittest import mock

import pytest

from rpmlb.builder.base import MACRO_REGEX, BaseBuilder
from rpmlb.recipe import Recipe
from rpmlb.work import Work


@pytest.fixture
def empty_spec_path(tmpdir):
    """Empty spec file path"""

    spec = Path(str(tmpdir), 'test.spec')
    spec.touch()

    with tmpdir.as_cwd():
        yield spec

    if spec.exists():
        spec.unlink()


@pytest.fixture
def prepared_macros():
    """Prepared testing spec macros"""

    macro_dict = {
        # Simple macro value
        'test_macro_a': r'value',
        # Macros with white space in the body
        'test_macro_b': r'with spaces in value',
        # Multi-line macro
        'test_macro_c': r'''multi \
            line''',
    }

    return macro_dict


@pytest.fixture
def macro_spec_path(empty_spec_path, prepared_macros):
    """Path to a spec file containing some macro definitions"""

    with empty_spec_path.open(mode='w') as out_file:
        for name, value in prepared_macros.items():
            print('%global {} {}'.format(name, value), file=out_file)

        print('BuildRequires foo', file=out_file)
        print('BuildRequires bar', file=out_file)
        print('BuildRequires dist', file=out_file)

    return empty_spec_path


@pytest.fixture
def builder(valid_recipe_path):
    """Provide initialized BaseBuilder."""

    recipe = Recipe(str(valid_recipe_path), 'rh-ror50')
    work = Work(recipe)
    builder = BaseBuilder(work, pkg_cmd='testpkg')
    return builder


def test_init(builder):
    assert builder


def test_init_raises_error_without_pkg_cmd_option(valid_recipe_path):
    recipe = Recipe(str(valid_recipe_path), 'rh-ror50')
    work = Work(recipe)
    with pytest.raises(ValueError):
        BaseBuilder(work)


def test_run_calls_before_build_after(builder):
    builder.before = mock.MagicMock()
    builder.build = mock.MagicMock(return_value=True)
    builder.after = mock.MagicMock()
    builder.prepare = mock.MagicMock()

    mock_work = get_mock_work()
    builder.run(mock_work)
    assert builder.before.called
    assert builder.build.called
    assert builder.after.called


def test_run_returns_true_on_success(builder):
    builder.build = lambda *args, **kwargs: None
    builder.prepare = mock.MagicMock()

    mock_work = get_mock_work()
    assert builder.run(mock_work)


def test_run_exception(builder):
    builder.build = mock.Mock(side_effect=ValueError('test'))
    builder.prepare = mock.MagicMock()

    mock_work = get_mock_work()
    type(mock_work).working_dir = mock.PropertyMock(return_value='work_dir')

    called = False
    error_message = None
    try:
        builder.run(mock_work, retry=3)
    except RuntimeError as e:
        called = True
        error_message = str(e)
    assert called
    expected_error_message = (
        "pacakge_dict: {'name': 'a'}, "
        "num: 1, work_dir: work_dir"
    )
    assert error_message == expected_error_message
    if sys.version_info >= (3, 6):
        builder.build.assert_called()
    # bulid should be called 3 times for retry setting.
    calls = [mock.call({'name': 'a'}, retry=3)] * 4
    builder.build.assert_has_calls(calls)
    assert builder.build.call_count == len(calls)


def test_run_does_not_call_before_calls_build_after_with_resume_option(builder):  # noqa: E501
    builder.before = mock.MagicMock()
    builder.build = mock.MagicMock(return_value=True)
    builder.after = mock.MagicMock()
    builder.prepare = mock.MagicMock()

    mock_work = get_mock_work()
    builder.run(mock_work, resume=2)
    assert not builder.before.called
    assert builder.build.called
    assert builder.after.called


def get_mock_work():
    mock_work = mock.MagicMock()
    package_dicts = [
        {'name': 'a'},
        {'name': 'b'},
    ]
    num_names = [
        '1',
        '2',
    ]
    mock_work.each_package_dir.return_value = iter(
        zip(package_dicts, num_names))
    return mock_work


def test_double_edit(empty_spec_path):
    """Original spec file is not modified twice"""

    def edit_file(path, indicator='Test edit'):
        """Single edit round"""

        with BaseBuilder.edit_spec_file(str(path)) as (src, dst):
            print(indicator, file=dst)
            dst.write(src.read())

    for indicator in ('First edit', 'Second edit'):
        edit_file(empty_spec_path, indicator)
        assert empty_spec_path.exists()


def test_macros_are_added_correctly(macro_spec_path, prepared_macros):
    """Macros are safely added without messing with current file contents."""

    new_macro_dict = {
        'bootstrap': 1,
        'with_bootstrap': 1,
    }

    with BaseBuilder.edit_spec_file(macro_spec_path) as (original, modified):
        content_stream = BaseBuilder.add_macros(original, new_macro_dict)
        modified.write(''.join(content_stream))

    with macro_spec_path.open() as spec_file:
        spec_contents = spec_file.read()

    # Count the macro occurrences
    matches = MACRO_REGEX.finditer(spec_contents)
    macro_counts = Counter(match.group('name') for match in matches)

    # Each expected macro is present exactly once
    assert all(cnt == 1 for cnt in macro_counts.values()), macro_counts

    expected_macro_names = new_macro_dict.keys() | prepared_macros.keys()
    present_macro_names = macro_counts.keys()
    assert expected_macro_names == present_macro_names, present_macro_names


def test_macros_are_replaced_correctly(macro_spec_path, prepared_macros):
    """Macros are correctly replaced."""

    replaced_macro_dict = dict.fromkeys(prepared_macros, 'REPLACED')

    with BaseBuilder.edit_spec_file(macro_spec_path) as (original, modified):
        content_stream = BaseBuilder.replace_macros(
            original,
            replaced_macro_dict,
        )
        modified.write(''.join(content_stream))

    with macro_spec_path.open() as spec_file:
        spec_contents = spec_file.read()

    result_macros = dict(MACRO_REGEX.findall(spec_contents))

    # All expected macros have their contents replaced
    assert all(val == 'REPLACED' for val in result_macros.values()), \
        result_macros  # show the macro values when debugging


def test_prepare_runs_all_preparations(
    builder, macro_spec_path, prepared_macros,
):
    """All preparations are done as expected

    1. `replace_macros` are replaced
    2. New macros are added
    3. Any builder extra steps are executed
    4. Commands in cmd element are executed
    """

    spec_file_name = macro_spec_path.name
    package_metadata = {
        'name': macro_spec_path.stem,
        'macros': dict(a='macro a', b='macro b'),
        'replaced_macros': dict.fromkeys(prepared_macros, 'REPLACED'),
        'cmd': [
            'sed -i "/^BuildRequires foo$/ s/^/#/" {0}'.format(spec_file_name),
            'sed -i "/^BuildRequires bar$/ s/^/#/" {0}'.format(spec_file_name),
            r'''if [[ "${{DIST}}" =~ centos ]]; then
                 sed -i "/^BuildRequires dist$/ s/dist/${{DIST}}/" {0}
             fi
            '''.format(spec_file_name),
        ],
    }

    builder.prepare_extra_steps = mock.MagicMock(
        wraps=builder.prepare_extra_steps,
    )

    builder.prepare(package_metadata, dist='centos7')

    with macro_spec_path.open() as spec_file:
        spec_contents = spec_file.read()

    macros = dict(MACRO_REGEX.findall(spec_contents))

    # Adding is performed
    assert all(macros[name] == package_metadata['macros'][name]
               for name in package_metadata['macros'])
    # Replacement is performed
    assert all(macros[name] == 'REPLACED'
               for name in package_metadata['replaced_macros'])
    # Extra preparation steps are performed
    assert builder.prepare_extra_steps.called

    assert re.search('^#BuildRequires foo$',
                     spec_contents, flags=re.MULTILINE)
    assert re.search('^#BuildRequires bar$',
                     spec_contents, flags=re.MULTILINE)
    assert re.search('^BuildRequires centos7$',
                     spec_contents, flags=re.MULTILINE)


def test_is_build_skipped_raises_error_when_package_dict_is_none(builder):
    package_dict = None
    num_name = '1'
    is_redume = False
    with pytest.raises(ValueError):
        builder._is_build_skipped(package_dict, num_name, is_redume)


def test_is_build_skipped_raises_error_when_num_name_is_none(builder):
    package_dict = {'name': 'a'}
    num_name = None
    is_redume = False
    with pytest.raises(ValueError):
        builder._is_build_skipped(package_dict, num_name, is_redume)


def test_is_build_skipped_returns_false_on_matched_dist(builder):
    package_dict = {
        'name': 'a',
        'dist': 'fc2[56]',
    }
    num_name = '1'
    is_redume = False
    kwargs = {
        'dist': 'fc26',
    }
    assert not builder._is_build_skipped(
        package_dict, num_name, is_redume, **kwargs)


def test_is_build_skipped_returns_true_on_unmatched_dist(builder):
    package_dict = {
        'name': 'a',
        'dist': 'fc2[56]',
    }
    num_name = '1'
    is_redume = False
    kwargs = {
        'dist': 'fc2',
    }
    assert builder._is_build_skipped(
        package_dict, num_name, is_redume, **kwargs)
