import logging
import yaml

LOG = logging.getLogger(__name__)


class Recipe(object):
    """A class to describe recipe data."""

    def __init__(self, file_path, scl_id):
        if file_path is None:
            raise ValueError('file_path is required.')
        if scl_id is None:
            raise ValueError('scl_id is required.')

        self._scl_id = scl_id
        self._scl = None

        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader

        with open(file_path, 'r') as stream:
            scl_dict = yaml.load(stream, Loader=Loader)
            self._scl = scl_dict[scl_id]
        self._num_of_package = len(self._scl['packages'])
        max_digit = len(str(self._num_of_package))
        self._num_dir_format = '%0{0}d'.format(str(max_digit))

    def dump(self):
        try:
            from yaml import CDumper as Dumper
        except ImportError:
            from yaml import Dumper
        output = yaml.dump(self._scl, Dumper=Dumper,
                           default_flow_style=False)
        print(output)

    @property
    def scl(self):
        return self._scl

    def num_of_package(self):
        return self._num_of_package

    def num_dir_name(self, count):
        num_dir_name = self._num_dir_format % count
        return num_dir_name

    def each_normalized_package(self):
        packages = self._scl['packages']
        package_dict = {}
        for package in packages:
            # String or hash
            if isinstance(package, str):
                package_dict['name'] = package
            elif isinstance(package, dict):
                keys = list(package.keys())
                name = keys[0]
                if package[name] is None:
                    raise ValueError('Recipe package %s is invalid format.' %
                                     name)
                package_dict = package[name]
                package_dict['name'] = name
            else:
                raise ValueError('package is invalid.')

            yield package_dict

    def verify(self):
        scl = self._scl

        if 'name' not in scl:
            raise ValueError('name is required in the scl.')
        if not scl['name']:
            raise ValueError('name is invalid in the scl.')

        if 'requires' in scl:
            if not isinstance(scl['requires'], list):
                raise ValueError('requires should be a list')

        if 'packages' not in scl:
            raise ValueError('packages is required in the scl.')
        if not scl['packages']:
            raise ValueError('packages is invalid in the scl.')
        if not isinstance(scl['packages'], list):
            raise ValueError('packages should be a list.')
        if len(scl['packages']) <= 0:
            raise ValueError('packages should have a element > 0')
        for package_dict in self.each_normalized_package():
            assert(package_dict['name'])

        return True
