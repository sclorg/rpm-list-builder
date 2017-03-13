import logging

# from rhsclbuilder import utils

LOG = logging.getLogger(__name__)


class BaseDownloader(object):
    """A base class for the package downloader."""

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls, name):
        # TODO: Use reflection.
        # class_name = 'rhsclbuilder.downloader.{0}.{1}Downloader'.format(
        #     name,
        #     utils.camelize(name)
        # )
        # return utils.get_instance(class_name)
        instance = None
        if name == 'local':
            from rhsclbuilder.downloader.local import LocalDownloader
            instance = LocalDownloader()
        elif name == 'rhpkg':
            from rhsclbuilder.downloader.rhpkg import RhpkgDownloader
            instance = RhpkgDownloader()
        else:
            raise ValueError('name is invalid.')
        return instance

    def run(self, work, **kwargs):
        for package_dict in work.each_num_dir():
            # TODO(Run it with asynchronous)
            self.download(package_dict, **kwargs)
        return True

    def download(self, package_dict, **kwargs):
        raise NotImplementedError('Implement this method.')
