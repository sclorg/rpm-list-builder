import logging
import os
import shutil

from sclh.downloader.base import BaseDownloader

LOG = logging.getLogger(__name__)


class LocalDownloader(BaseDownloader):
    """A downloader class to copy a pacakge from source directory."""

    def __init__(self):
        pass

    def download(self, package_dict, **kwargs):
        if not package_dict:
            raise ValueError('package_dict is required.')
        if 'source_directory' not in kwargs or not kwargs['source_directory']:
            raise ValueError('source directory is required.')
        src_dir = kwargs['source_directory']
        package = package_dict['name']
        src_package_dir = os.path.join(src_dir, package)
        dst_package_dir = os.path.join(os.getcwd(), package)
        LOG.debug('Copying %s to %s .', src_package_dir, dst_package_dir)
        # Set symlinks as True to Avoid to create new files from simbolic link.
        # Because it might be cost.
        # TODO: Skip symbolic file when copying. The file is risky.
        shutil.copytree(src_package_dir, dst_package_dir, symlinks=True)
