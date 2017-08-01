import logging

from .. import utils
from ..work import Work
from .base import BaseBuilder

LOG = logging.getLogger(__name__)


class MockBuilder(BaseBuilder):
    """A builder class for Mock."""

    def __init__(self, work: Work, mock_config: str = None, **options):
        """Initialize the builder.

        Keyword arguments:
            work: The overview of the work to do.
            mock_config: Name of the Mock configuration profile to use.
        """

        super().__init__(work, mock_config=mock_config, **options)

        if mock_config is None:
            raise ValueError('mock_config is required.')

        #: Name of the Mock configuration profile to use
        self.mock_config = mock_config

    def before(self, work, **kwargs):
        utils.run_cmd('mock -r {} --scrub=all'.format(self.mock_config))

    def build(self, package_dict, **kwargs):
        utils.run_cmd('rm -v *.rpm', check=False)
        utils.run_cmd('{} srpm'.format(self._pkg_cmd))
        utils.run_cmd('mock -r {} -n *.rpm'.format(self.mock_config))
