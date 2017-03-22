import logging

from sclh.builder.base import BaseBuilder

LOG = logging.getLogger(__name__)


class DummyBuilder(BaseBuilder):
    """A builder class for Copr."""

    def build(self, package_dict, **kwargs):
        LOG.info('dummy build %s', package_dict['name'])
