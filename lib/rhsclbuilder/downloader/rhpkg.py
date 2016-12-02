import logging
import os
import subprocess

from rhsclbuilder.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class RhpkgDownloader(BaseDownloader):
    """A downloader class to get a pacakge with rhpkg command."""

    def download(self, package, **kwargs):
        if not package:
            raise ValueError('package is required.')
        if 'branch' not in kwargs or not kwargs['branch']:
            raise ValueError('branch is required.')
        branch = kwargs['branch']

        self.do_rhpkg_and_checkout(branch)

    def do_rhpkg_and_checkout(self, branch):
        if not branch:
            raise ValueError('branch is required.')

        LOG.debug('rhpkg co %s', self.package)
        subprocess.check_call(['rhpkg', 'co', self.package])
        LOG.debug('cd %s', self.package)
        os.chdir(self.package)
        LOG.debug('git checkout %s', branch)
        subprocess.check_call(['git', 'checkout', branch])
