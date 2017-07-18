from pathlib import Path

from rpmlb.downloader.local import LocalDownloader


def test_init():
    downloader = LocalDownloader()
    assert downloader


def test_download(tmpdir_factory):

    downloader = LocalDownloader()
    package_dict = {'name': 'a'}

    # Create source files for test.
    src_dir = tmpdir_factory.mktemp('rpmlb-test-src-dir')

    original_spec_path = Path(str(src_dir), 'a', 'a.spec')
    original_spec_path.parent.mkdir(parents=True)
    original_spec_path.touch()

    # "Download" the files
    with tmpdir_factory.mktemp('rpmlb-test-download-dir').as_cwd():
        downloader.download(package_dict, source_directory=str(src_dir))
        spec_path = Path('a', 'a.spec')
        assert spec_path.is_file()
