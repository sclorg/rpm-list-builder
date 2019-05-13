import logging

from .. import utils
from .base import BaseDownloader

LOG = logging.getLogger(__name__)


class BaseRpkgDownloader(BaseDownloader):
    """A downloader class to get a pacakge with package command."""

    @property
    def command(self):
        raise NotImplementedError('Implement this method.')

    def download(self, package_dict, **kwargs):
        if not package_dict:
            raise ValueError('package_dict is required.')
        if 'branch' not in kwargs or not kwargs['branch']:
            raise ValueError('branch is required.')
        branch = kwargs['branch']

        package = package_dict['name']
        cmd = r'''
{command} co {package} && \
cd {package} && \
git checkout {branch} && \
{command} sources
        '''.strip().format(
            command=self.command,
            package=package,
            branch=branch,
        )
        utils.run_cmd(cmd)
