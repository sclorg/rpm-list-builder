import logging

from rpmlb.custom import Custom
from rpmlb.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class CustomDownloader(BaseDownloader):
    """A custom downloader class."""

    def __init__(self):
        self._yaml_content = None

    def before(self, work, **kwargs):
        custom_file = kwargs['custom_file']
        if not custom_file:
            raise ValueError('custom_file is required.')

        custom = Custom(custom_file)
        custom.run_cmds('before_download')

    def download(self, package_dict, **kwargs):
        custom_file = kwargs['custom_file']
        if not custom_file:
            raise ValueError('custom_file is required.')

        custom = Custom(custom_file)
        custom.run_cmds('download', **package_dict)
