from rpmlb.downloader.rhpkg import RhpkgDownloader


def test_command_returns_the_value():
    downloader = RhpkgDownloader()
    assert downloader.command == 'rhpkg'
