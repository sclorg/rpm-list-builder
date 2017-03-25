import logging
import yaml

LOG = logging.getLogger(__name__)


class Yaml(object):
    """A class to manage YAML data."""

    def __init__(self, file_path):
        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader
        with open(file_path, 'r') as stream:
            self.content = yaml.load(stream, Loader=Loader)

    def dump(self):
        try:
            from yaml import CDumper as Dumper
        except ImportError:
            from yaml import Dumper
        output = yaml.dump(self.content, Dumper=Dumper,
                           default_flow_style=False)
        print(output)
