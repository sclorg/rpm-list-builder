import logging
import os
import shutil

from rpmlb.downloader.base import BaseDownloader

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

        def ignore_symlinks(directory, files):
            ignored_files = []
            for f in files:
                full_path = os.path.join(directory, f)
                if os.path.islink(full_path):
                    ignored_files.append(f)
            return ignored_files

        # Skip symbolic file when copying because the file is risky.
        shutil.copytree(
            src_package_dir,
            dst_package_dir,
            ignore=ignore_symlinks,
            symlinks=True
        )
