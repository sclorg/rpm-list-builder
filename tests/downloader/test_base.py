import sys

from rpmlb.downloader.base import BaseDownloader

if sys.version_info[0] >= 3:
    from unittest import mock
else:
    import mock


def test_init():
    downloader = BaseDownloader()
    assert downloader


def test_run():
    downloader = BaseDownloader()
    downloader.download = mock.MagicMock(return_value=True)
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
    result = downloader.run(mock_work)
    assert result
