import logging

# from rpmlb import utils

LOG = logging.getLogger(__name__)


class BaseDownloader(object):
    """A base class for the package downloader."""

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls, name):
        # TODO: Use reflection.
        # class_name = 'rpmlb.downloader.{0}.{1}Downloader'.format(
        #     name,
        #     utils.camelize(name)
        # )
        # return utils.get_instance(class_name)
        instance = None
        if name == 'local':
            from rpmlb.downloader.local import LocalDownloader
            instance = LocalDownloader()
        elif name == 'rhpkg':
            from rpmlb.downloader.rhpkg import RhpkgDownloader
            instance = RhpkgDownloader()
        elif name == 'none':
            from rpmlb.downloader.none import NoneDownloader
            instance = NoneDownloader()
        elif name == 'custom':
            from rpmlb.downloader.custom import CustomDownloader
            instance = CustomDownloader()
        else:
            raise ValueError('name is invalid.')
        LOG.debug('Loaded downloader with %s', name)
        return instance

    def run(self, work, **kwargs):
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
