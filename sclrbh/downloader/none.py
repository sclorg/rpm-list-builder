import logging

from sclrbh.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class NoneDownloader(BaseDownloader):
    """A downloader class to do nothing."""

    def download(self, package_dict, **kwargs):
        pass
