import logging

from rpmlb import utils
from rpmlb.yaml import Yaml

LOG = logging.getLogger(__name__)


class Custom(object):
    """A class to manage custom file."""

    def __init__(self, file_path):
        self._file_path = file_path
        self._yaml_content = None

    def run_cmds(self, key, **kwargs):
        env = {}
        # Support environment variable to use PKG as pacakge name in the file.
        if 'name' in kwargs:
            env['PKG'] = kwargs['name']

        for cmd in self.each_yaml_cmd(key):
            utils.run_cmd(cmd, env=env)

    def each_yaml_cmd(self, key):
        cmd_dict = self._get_yaml_content(self._file_path)
        if key not in cmd_dict:
            return
        cmds = cmd_dict[key]
        for cmd in cmds:
            yield cmd

    def _get_yaml_content(self, file_path):
        if self._yaml_content:
            return self._yaml_content
        yaml = Yaml(file_path)
        self._yaml_content = yaml.content
        return self._yaml_content
