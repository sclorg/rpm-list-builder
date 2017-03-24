from unittest.mock import MagicMock

from rhsclbuilder.downloader.base import BaseDownloader


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
    num_dir_names = [
        '1',
        '2',
    ]
    mock_work.each_num_dir.return_value = iter(
        zip(package_dicts, num_dir_names))
    result = downloader.run(mock_work)
    assert result
