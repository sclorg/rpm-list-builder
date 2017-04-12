import os
import tempfile

from rpmlb.downloader.local import LocalDownloader
import helper


def test_init():
    downloader = LocalDownloader()
    assert downloader


def test_download():
    downloader = LocalDownloader()
    package_dict = {'name': 'a'}
    # Create source files for test.
    src_dir = tempfile.mkdtemp(prefix='rpmlb-test-src-')
    with helper.pushd(src_dir):
        os.makedirs('a')
        helper.touch(os.path.join('a', 'a.spec'))

    with helper.pushd_tmp_dir():
        downloader.download(package_dict, source_directory=src_dir)
        spec_file = os.path.join('a', 'a.spec')
        assert os.path.isfile(spec_file)
