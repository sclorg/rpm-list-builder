from unittest.mock import MagicMock

from sclh.downloader.base import BaseDownloader


def test_init():
    downloader = BaseDownloader()
    assert downloader


def test_run():
    downloader = BaseDownloader()
    downloader.download = MagicMock(return_value=True)
    mock_work = MagicMock()
    package_dicts = [
        {'name': 'a'},
        {'name': 'b'},
    ]
    mock_work.each_num_dir.return_value = iter(package_dicts)
    result = downloader.run(mock_work)
    assert result
