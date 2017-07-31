import logging
import os
import re

from .. import utils

LOG = logging.getLogger(__name__)


class BaseDownloader:
    """A base class for the package downloader."""

    def __init__(self):
        pass

    @staticmethod
    def get_instance(name: str):
        """Dynamically instantiate named downloader.

        Keyword arguments:
            name: Name of the requested builder.

        Returns:
            Instance of the requested builder.
        """

        class_name = 'rpmlb.downloader.{0}.{1}Downloader'.format(
            name,
            utils.camelize(name)
        )
        instance = utils.get_instance(class_name)

        LOG.debug('Loaded downloader with %s', name)
        return instance

    def run(self, work, **kwargs):
        is_resume = kwargs.get('resume', False)
        if is_resume:
            message = (
                'Skip the download process, '
                'because the resume option was used.'
            )
            LOG.info(message)
            return True

        self.before(work, **kwargs)

        for package_dict, num_name in work.each_num_dir():
            if self._is_download_skipped(package_dict, **kwargs):
                name = package_dict['name']
                LOG.debug('Skip download package: %s', name)
                # Create package directory for build process.
                if not os.path.isdir(name):
                    os.mkdir(name)
                continue

            # TODO(Run it with asynchronous)
            self.download(package_dict, **kwargs)

        self.after(work, **kwargs)
        return True

    def before(self, work, **kwargs):
        pass

    def after(self, work, **kwargs):
        pass

    def download(self, package_dict, **kwargs):
        raise NotImplementedError('Implement this method.')

    def _is_download_skipped(self, package_dict: dict, **kwargs):
        """Return if skip a download for a pacakge.

        Override if needed.

        Keyword arguments:
            package_dict: A dictionary of package metadata.
            kwargs: option arguments.
        """

        if not package_dict:
            raise ValueError('package_dict is required.')

        is_skipped = False

        dist = kwargs.get('dist')
        if dist and 'dist' in package_dict:
            if not re.match(package_dict['dist'], dist):
                is_skipped = True
        return is_skipped
