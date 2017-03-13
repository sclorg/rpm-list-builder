import logging
import os
import subprocess

from rhsclbuilder.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class RhpkgDownloader(BaseDownloader):
    """A downloader class to get a pacakge with rhpkg command."""

    def download(self, package_dict, **kwargs):
        if not package_dict:
            raise ValueError('package_dict is required.')
        if 'branch' not in kwargs or not kwargs['branch']:
            raise ValueError('branch is required.')
        branch = kwargs['branch']

        self.do_rhpkg_and_checkout(package_dict, branch)

    def do_rhpkg_and_checkout(self, package_dict, branch):
        if not package_dict:
            raise ValueError('package_dict is required.')
        if not branch:
            raise ValueError('branch is required.')

        package = package_dict['name']

        LOG.debug('rhpkg co %s', package)
        subprocess.check_call(['rhpkg', 'co', package])
        LOG.debug('cd %s', package)
        os.chdir(package)
        LOG.debug('git checkout %s', branch)
        subprocess.check_call(['git', 'checkout', branch])
