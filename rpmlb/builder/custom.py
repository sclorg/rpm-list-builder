import logging

from ..custom import Custom
from ..work import Work
from .base import BaseBuilder

LOG = logging.getLogger(__name__)


class CustomBuilder(BaseBuilder):
    """A custom builder class."""

    def __init__(self, work: Work, custom_file: str = None, **options):
        """Initialize the builder.

        Keyword arguments:
            work: The overview of the work to do.
            custom_file: Path to the custom file.
        """

        super().__init__(work, custom_file=custom_file, **options)

        if custom_file is None:
            raise ValueError('custom_file is required.')

        #: Custom commands runner to use
        self.custom_runner = Custom(custom_file)

    def before(self, work, **kwargs):
        self.custom_runner.run_cmds('before_build')

    def build(self, package_dict, **kwargs):
        self.custom_runner.run_cmds('build', **package_dict)
