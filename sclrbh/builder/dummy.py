import logging

from sclrbh.builder.base import BaseBuilder

LOG = logging.getLogger(__name__)


class DummyBuilder(BaseBuilder):
    """A dummy builder class."""

    def build(self, package_dict, **kwargs):
        LOG.info('dummy build %s', package_dict['name'])
