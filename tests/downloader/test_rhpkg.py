import sys

from rpmlb.downloader.rhpkg import RhpkgDownloader

if sys.version_info[0] >= 3:
    from unittest import mock
else:
    import mock


def test_init():
    downloader = RhpkgDownloader()
    assert downloader


def test_download():
    downloader = RhpkgDownloader()
    downloader.do_rhpkg_and_checkout = mock.MagicMock(return_value=True)
    package_dict = {'name': 'a'}
    branch = 'private-foo'
    downloader.download(package_dict, branch=branch)
    assert True


""" Comment out for the kerberos auth.
def test_do_rhpkg_and_checkout():
    downloader = RhpkgDownloader()
    package_dict = {'name': 'rubygem-arel'}
    branch = 'rhscl-2.4-rh-ror50-rhel-7'
    with helper.pushd_tmp_dir():
        # TODO: Add check for kerberos auth.
        downloader.do_rhpkg_and_checkout(package_dict, branch)
        spec_file = os.path.join('1', 'rubygem-arel', 'rubygem-arel.spec')
        assert os.path.isfile(spec_file)
        # Show current branch
        # git rev-parse --abbrev-ref HEAD
        # TODO Add assert for output of below command.
        subprocess.check_call(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        assert True
"""
