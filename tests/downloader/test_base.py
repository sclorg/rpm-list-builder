from pathlib import Path
from unittest import mock

import pytest

from rpmlb.downloader.base import BaseDownloader


@pytest.fixture
def downloader():
    downloader = BaseDownloader()
    return downloader


def test_init(downloader):
    assert downloader


def test_run_calls_before_build_after(downloader):
    downloader.before = mock.MagicMock()
    downloader.download = mock.MagicMock(return_value=True)
    downloader.after = mock.MagicMock()

    mock_work = get_mock_work()
    downloader.run(mock_work)
    assert downloader.before.called
    assert downloader.download.called
    assert downloader.after.called


def test_run_returns_true_on_success(downloader):
    downloader.download = lambda *args, **kwargs: None

    mock_work = get_mock_work()
    assert downloader.run(mock_work)


def test_run_does_not_call_before_build_after_with_resume(downloader):
    downloader.before = mock.MagicMock()
    downloader.download = mock.MagicMock(return_value=True)
    downloader.after = mock.MagicMock()

    mock_work = get_mock_work()
    downloader.run(mock_work, resume=2)
    assert not downloader.before.called
    assert not downloader.download.called
    assert not downloader.after.called


def test_run_skip_download(downloader):
    downloader.download = mock.MagicMock(return_value=True)
    downloader._is_download_skipped = lambda *args, **kwargs: True

    mock_work = get_mock_work()
    with pytest.helpers.generate_tmp_path() as tmp_path:
        tmp_path.mkdir()
        with pytest.helpers.pushd(tmp_path):
            downloader.run(mock_work)
            assert not downloader.download.called
            assert Path('a').is_dir()
            assert Path('b').is_dir()


def test_is_download_skipped_raises_error_when_package_dict_none(downloader):
    package_dict = None
    with pytest.raises(ValueError):
        downloader._is_download_skipped(package_dict)


def test_is_download_skipped_returns_false_on_matched_dist(downloader):
    package_dict = {
        'name': 'a',
        'dist': 'fc2[56]',
    }
    kwargs = {
        'dist': 'fc26',
    }
    assert not downloader._is_download_skipped(package_dict, **kwargs)


def test_is_download_skipped_returns_true_on_unmatched_dist(downloader):
    package_dict = {
        'name': 'a',
        'dist': 'fc2[56]',
    }
    kwargs = {
        'dist': 'fc2',
    }
    assert downloader._is_download_skipped(package_dict, **kwargs)


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
