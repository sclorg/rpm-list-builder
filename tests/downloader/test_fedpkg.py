from rpmlb.downloader.fedpkg import FedpkgDownloader


def test_command_returns_the_value():
    downloader = FedpkgDownloader()
    assert downloader.command == 'fedpkg'
