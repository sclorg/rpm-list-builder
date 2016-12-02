import logging
import os

from rhsclbuilder.utils import pushd

LOG = logging.getLogger(__name__)


class BaseDownloader(object):
    """A base class for the package downloader."""

    def __init__(self):
        self._downloaded_directory = None
        return None

    @property
    def downloaded_directory(self):
        return self._downloaded_directory

    @downloaded_directory.setter
    def downloaded_directory(self, value):
        self._downloaded_directory = value

    def run(self, recipe, **kwargs):
        downloaded_dir = self.downloaded_directory
        if not downloaded_dir:
            ValueError('downloaded_directory is not set.')
        with pushd(downloaded_dir):
            count = 1
            for package_dict in recipe.each_normalized_package():
                package = package_dict['name']
                # TODO(Run it with asynchronous)
                num_dir_name = recipe.num_dir_name(count)
                os.makedirs(num_dir_name)
                with pushd(num_dir_name):
                    self.download(package, **kwargs)
                count += 1
        return True

    def download(self, package, **kwargs):
        raise NotImplementedError('Implement this method.')
