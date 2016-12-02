import logging
import os
import shutil

from rhsclbuilder.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class LocalDownloader(BaseDownloader):
    """A downloader class to copy a pacakge from source directory."""

    def __init__(self):
        return None

    def download(self, package, **kwargs):
        if not package:
            raise ValueError('package is required.')
        if 'source_directory' not in kwargs or not kwargs['source_directory']:
            raise ValueError('source directory is required.')
        src_dir = kwargs['source_directory']
        src_package_dir = os.path.join(src_dir, package)
        dst_package_dir = os.path.join(os.getcwd(), package)
        LOG.debug('Copying %s to %s.', src_package_dir, dst_package_dir)
        shutil.copytree(src_package_dir, dst_package_dir)
