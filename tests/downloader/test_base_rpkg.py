from unittest import mock

import pytest

from rpmlb.downloader.base_rpkg import BaseRpkgDownloader


@pytest.fixture
def downloader():
    return BaseRpkgDownloader()


@pytest.fixture
def mock_downloader(downloader, monkeypatch):
    monkeypatch.setattr(type(downloader), 'command',
                        mock.PropertyMock(return_value='testpkg'))

    return downloader


def test_init(downloader):
    assert downloader


def test_command_raises_not_implemented_error(downloader):
    with pytest.raises(NotImplementedError):
        downloader.command


def test_download_passes_on_valid_arguments(mock_downloader):
    package_dict = {'name': 'a'}
    branch = 'private-foo'
    with mock.patch('rpmlb.utils.run_cmd',
                    mock.Mock(return_value=True)) as mock_run_cmd:
        mock_downloader.download(package_dict, branch=branch)
        cmd = r'''
testpkg co a && \
cd a && \
git checkout private-foo
        '''.strip()
        mock_run_cmd.assert_called_once_with(cmd)
    assert True


def test_download_raises_error_on_without_package_dict(downloader):
    package_dict = None
    branch = 'private-foo'
    with mock.patch('rpmlb.utils.run_cmd', mock.Mock(return_value=True)):
        with pytest.raises(ValueError):
            downloader.download(package_dict, branch=branch)


def test_download_raises_error_on_without_branch(downloader):
    package_dict = {'name': 'a'}
    with pytest.raises(ValueError):
        downloader.download(package_dict)
