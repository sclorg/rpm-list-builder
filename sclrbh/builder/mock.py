import logging

from sclrbh.builder.base import BaseBuilder
from sclrbh import utils

LOG = logging.getLogger(__name__)


class MockBuilder(BaseBuilder):
    """A builder class for Copr."""

    def before_run(self, work, **kwargs):
        mock_config = kwargs['mock_config']
        if not mock_config:
            raise ValueError('mock_config is required.')

        utils.run_cmd('mock -r %s --scrub=all' % mock_config)

    def build(self, package_dict, **kwargs):
        mock_config = kwargs['mock_config']
        if not mock_config:
            raise ValueError('mock_config is required.')

        utils.run_cmd('rm -v *.rpm', check=False)
        utils.run_cmd('rhpkg srpm')
        utils.run_cmd('mock -r %s -n *.rpm' % mock_config)
