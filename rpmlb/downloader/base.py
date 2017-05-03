import logging

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
