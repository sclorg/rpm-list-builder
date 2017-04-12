import sys
from rpmlb.builder.base import BaseBuilder

if sys.version_info[0] >= 3:
    from unittest import mock
else:
    import mock


def test_init():
    builder = BaseBuilder()
    assert builder


def test_run():
    builder = BaseBuilder()
    builder.build = mock.MagicMock(return_value=True)

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

    result = builder.run(mock_work)
    assert result


def test_run_exception():
    builder = BaseBuilder()
    builder.build = mock.Mock(side_effect=ValueError('test'))

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
