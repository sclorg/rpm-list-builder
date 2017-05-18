from unittest import mock

from rpmlb.downloader.base import BaseDownloader


def test_init():
    downloader = BaseDownloader()
    assert downloader


def test_run_calls_before_build_after():
    downloader = BaseDownloader()
    downloader.before = mock.MagicMock()
    downloader.download = mock.MagicMock(return_value=True)
    downloader.after = mock.MagicMock()

    mock_work = get_mock_work()
    downloader.run(mock_work)
    assert downloader.before.called
    assert downloader.download.called
    assert downloader.after.called


def test_run_returns_true_on_success():
    downloader = BaseDownloader()
    downloader.download = lambda *args, **kwargs: None

    mock_work = get_mock_work()
    assert downloader.run(mock_work)


def test_run_does_not_call_before_build_after_with_resume():
    downloader = BaseDownloader()
    downloader.before = mock.MagicMock()
    downloader.download = mock.MagicMock(return_value=True)
    downloader.after = mock.MagicMock()

    mock_work = get_mock_work()
    downloader.run(mock_work, resume=2)
    assert not downloader.before.called
    assert not downloader.download.called
    assert not downloader.after.called


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
    mock_work.each_num_dir.return_value = iter(
        zip(package_dicts, num_names))
    return mock_work
