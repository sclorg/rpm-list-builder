from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import call

from rpmlb.builder.base import BaseBuilder


def test_init():
    builder = BaseBuilder()
    assert builder


def test_run():
    builder = BaseBuilder()
    builder.build = MagicMock(return_value=True)

    mock_work = MagicMock()
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

    result = builder.run(mock_work)
    assert result


def test_run_exception():
    builder = BaseBuilder()
    builder.build = Mock(side_effect=ValueError('test'))

    mock_work = MagicMock()
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

    called = False
    error_message = None
    try:
        builder.run(mock_work)
    except RuntimeError as e:
        called = True
        error_message = str(e)
    assert called
    assert error_message == "pacakge_dict: {'name': 'a'}, num: 1"
    builder.build.assert_called()
    # bulid should be called 3 times for retry setting.
    calls = [
        call({'name': 'a'}),
        call({'name': 'a'}),
        call({'name': 'a'}),
    ]
    builder.build.assert_has_calls(calls)
