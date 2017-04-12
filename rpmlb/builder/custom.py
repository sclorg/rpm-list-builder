import logging

from rpmlb.builder.base import BaseBuilder
from rpmlb.custom import Custom

LOG = logging.getLogger(__name__)


class CustomBuilder(BaseBuilder):
    """A custom builder class."""

    def __init__(self):
        self._yaml_content = None

    def before(self, work, **kwargs):
        custom_file = kwargs['custom_file']
        if not custom_file:
            raise ValueError('custom_file is required.')

        custom = Custom(custom_file)
        custom.run_cmds('before_build')

    def build(self, package_dict, **kwargs):
        custom_file = kwargs['custom_file']
        if not custom_file:
            raise ValueError('custom_file is required.')

        custom = Custom(custom_file)
        custom.run_cmds('build', **package_dict)
