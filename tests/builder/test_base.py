import sys
from pathlib import Path
from unittest import mock

import pytest

from rpmlb.builder.base import BaseBuilder


@pytest.fixture
def empty_spec_path(tmpdir):
    """Empty spec file path"""

    spec = Path(str(tmpdir), 'test.spec')
    spec.touch()

    yield spec

    if spec.exists():
        spec.unlink()


def test_init():
    builder = BaseBuilder()
    assert builder


def test_run_calls_before_build_after():
    builder = BaseBuilder()
    builder.before = mock.MagicMock()
    builder.build = mock.MagicMock(return_value=True)
    builder.after = mock.MagicMock()

    mock_work = get_mock_work()
    builder.run(mock_work)
    assert builder.before.called
    assert builder.build.called
    assert builder.after.called


def test_run_returns_true_on_success():
    builder = BaseBuilder()
    builder.build = lambda *args, **kwargs: None

    mock_work = get_mock_work()
    assert builder.run(mock_work)


def test_run_exception():
    builder = BaseBuilder()
    builder.build = mock.Mock(side_effect=ValueError('test'))

    mock_work = get_mock_work()
    type(mock_work).working_dir = mock.PropertyMock(return_value='work_dir')

    called = False
    error_message = None
    try:
        builder.run(mock_work)
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
    calls = [
        mock.call({'name': 'a'}),
        mock.call({'name': 'a'}),
        mock.call({'name': 'a'}),
    ]
    builder.build.assert_has_calls(calls)


def test_run_does_not_call_before_calls_build_after_with_resume_option():
    builder = BaseBuilder()
    builder.before = mock.MagicMock()
    builder.build = mock.MagicMock(return_value=True)
    builder.after = mock.MagicMock()

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

    def edit_file(builder, path, indicator='Test edit'):
        """Single edit round"""

        for (src, dst) in builder.edit_spec_file(str(path)):
            print(indicator, file=dst)
            dst.write(src.read())

    def count_markers(path, marker='# Edited by rpmlb'):
        """Count lines containing marker text in file"""

        with path.open() as handle:
            return sum(marker in line for line in handle)

    builder = BaseBuilder()

    for indicator in ('First edit', 'Second edit'):
        edit_file(builder, empty_spec_path, indicator)
        assert empty_spec_path.exists()
        assert count_markers(empty_spec_path) == 1
