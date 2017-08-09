import logging
from collections import Counter
from itertools import starmap
from typing import Iterator, Mapping, Union

import click

from rpmlb.yaml import Yaml

LOG = logging.getLogger(__name__)


class Recipe:
    """A class to describe recipe data."""

    ERROR_REQUIRED = '{} is required.'
    ERROR_EMPTY = '{} is empty.'
    ERROR_TYPE = '{} should be a {}.'
    ERROR_INVALID = '{} is invalid.'
    ERROR_UNKNOWN = '{} is an unknown element.'
    TYPE_DISP_MAP = {
        'str': 'string',
        'list': 'sequences',
        'dict': 'mappings',
    }

    def __init__(self, file_path, collection_id):
        if not file_path:
            raise ValueError('file_path is required.')
        if not collection_id:
            raise ValueError('collection_id is required.')

        self._collection_id = collection_id

        yaml = Yaml(file_path)
        LOG.debug('Loaded recipe: %s', file_path)
        recipe_dict = yaml.content
        self.recipe = recipe_dict[collection_id]
        self.num_of_package = len(self.recipe['packages'])

    def each_normalized_package(self):
        """Present recipe packages in normalized form.

        Yields:
            Dictionary with the package's data.

        Common keys in the yielded dictionary:
            - name: The package's name
            - bootstrap_position: Numerical position in the bootstrapping
                sequence, or None if no bootstrap is necessary.
            - macros, replaced_macros: Mapping of macro name to (new)
                macro body.
        """

        packages = self.recipe['packages']
        bootstrap_map = self._count_bootstrap_sequences()

        for package in packages:
            name = self._package_name(package)
            bootstrap_position = next(bootstrap_map[name], None)

            package_dict = {
                'name': name,
                'bootstrap_position': bootstrap_position,
            }

            if isinstance(package, Mapping):
                # package should be one-item dictionary
                metadata, = package.values()
                package_dict.update(metadata)

            yield package_dict

    def verify(self):
        error_messages = self._verify_recipe()
        if error_messages:
            raise RecipeError(error_messages)

        return True

    def _verify_recipe(self) -> list:
        error_messages = []
        recipe = self.recipe

        if 'packages' not in recipe:
            message = self._format_error_required('packages')
            error_messages.append(message)

        for key in recipe:
            is_known_key = False
            if key == 'name':
                is_known_key = True
                if not recipe[key]:
                    message = self._format_error_empty(key)
                    error_messages.append(message)
                if not isinstance(recipe[key], str):
                    message = self._format_error_type(key, str)
                    error_messages.append(message)
            if key == 'requires':
                is_known_key = True
                if not recipe[key]:
                    message = self._format_error_empty(key)
                    error_messages.append(message)
                if not isinstance(recipe[key], list):
                    message = self._format_error_type(key, list)
                    error_messages.append(message)
            if key == 'packages':
                is_known_key = True
                is_packages_valid = True
                if not recipe[key]:
                    is_packages_valid = False
                    message = self._format_error_empty(key)
                    error_messages.append(message)
                if not isinstance(recipe[key], list):
                    is_packages_valid = False
                    message = self._format_error_type(key, list)
                    error_messages.append(message)
                if is_packages_valid:
                    # Check the detail of packages element.
                    error_messages = self._verify_packages_and_append(
                        error_messages, recipe[key]
                    )
            if not is_known_key:
                message = self._format_error_unknown(key)
                error_messages.append(message)
        return error_messages

    def _verify_packages_and_append(self, messages: list,
                                    packages: list) -> list:
        if messages is None:
            raise ValueError('messages is required.')
        if not packages:
            raise ValueError('packages is required.')
        error_messages = messages.copy()
        disp_packages_format = 'packages[{}] {}'

        for index, package in enumerate(packages):
            disp_num = index + 1

            if isinstance(package, str):
                disp_package = disp_packages_format.format(disp_num, package)
                if not package:
                    message = self._format_error_empty(disp_package)
                    error_messages.append(message)
            elif isinstance(package, dict):
                name = list(package.keys())[0]
                disp_package = disp_packages_format.format(disp_num, name)

                if len(package) != 1:
                    message = self._format_error_invalid(disp_package)
                    error_messages.append(message)
                else:
                    package_metadata = package[name]
                    error_messages = self._verify_packages_metadata_and_append(
                        error_messages, package_metadata, disp_package,
                    )
            else:
                disp_package = disp_packages_format.format(disp_num, package)

                message = self._format_error_type(disp_package, (str, dict))
                error_messages.append(message)
        return error_messages

    def _verify_packages_metadata_and_append(self, messages: list,
                                             metadata: dict,
                                             disp_package: str) -> list:
        if messages is None:
            raise ValueError('messages is required.')
        if not metadata:
            raise ValueError('metadata is required.')
        if not disp_package:
            raise ValueError('disp_package is required.')
        error_messages = messages.copy()

        for key in metadata.keys():
            disp_name = '{} {}'.format(disp_package, key)
            is_known_key = False
            if key in {'macros', 'replaced_macros'}:
                is_known_key = True
                if not metadata[key]:
                    message = self._format_error_empty(disp_name)
                    error_messages.append(message)
                if not isinstance(metadata[key], dict):
                    message = self._format_error_type(disp_name, dict)
                    error_messages.append(message)
            if key == 'cmd':
                is_known_key = True
                if not metadata[key]:
                    message = self._format_error_empty(disp_name)
                    error_messages.append(message)
                if not isinstance(metadata[key], (str, list)):
                    message = self._format_error_type(disp_name, (str, list))
                    error_messages.append(message)
            if key == 'dist':
                is_known_key = True
                if not metadata[key]:
                    message = self._format_error_empty(disp_name)
                    error_messages.append(message)
                if not isinstance(metadata[key], str):
                    message = self._format_error_type(disp_name, str)
                    error_messages.append(message)
            if not is_known_key:
                message = self._format_error_unknown(disp_name)
                error_messages.append(message)

        return error_messages

    def _format_error_required(self, name):
        return self.ERROR_REQUIRED.format(name)

    def _format_error_empty(self, name):
        return self.ERROR_EMPTY.format(name)

    def _format_error_type(self, name, types: Union[type, tuple]):
        disp_type = None
        if type(types) == type:
            type_classes = tuple([types])
        else:
            type_classes = types

        def make_type_disp(cls):
            return self.TYPE_DISP_MAP[cls.__name__]

        class_strs = list(map(make_type_disp, type_classes))
        disp_type = ' or '.join(class_strs)

        return self.ERROR_TYPE.format(name, disp_type)

    def _format_error_invalid(self, name):
        return self.ERROR_INVALID.format(name)

    def _format_error_unknown(self, name):
        return self.ERROR_UNKNOWN.format(name)

    def _package_name(self, package: Union[str, dict]) -> str:
        """Extract package name.

        Keyword arguments:
            package: Raw package data to analyze.
                It should be either string or one-item dictionary.

        Returns:
            Name of the package.

        Raises:
            ValueError: Invalid package type.
        """

        if isinstance(package, str):  # The name itself
            return package

        elif isinstance(package, dict):
            # package should be one-item dictionary
            if len(package) != 1:
                message = self._format_error_invalid(package)
                raise ValueError(message)

            # The name is the only key
            name, = package.keys()
            return name

        else:
            message = self._format_error_type(package, (str, dict))
            raise ValueError(message)

    def _count_bootstrap_sequences(self) -> Mapping[str, Iterator[int]]:
        """Count package instances and produce bootstrap sequences.

        Returns:
            Mapping of package number to iterator of bootstrap numbers.
        """

        name_list = map(self._package_name, self.recipe['packages'])
        count_map = Counter(name_list)

        def make_sequence(name: str, count: int):
            """Count package instances except the last one; start from 1"""

            sequence = range(1, count)
            return name, iter(sequence)

        # Create a dictionary from (name, sequence) tuples
        sequence_map = dict(starmap(make_sequence, count_map.items()))

        return sequence_map


class RecipeError(click.ClickException):
    """A class to manage validation error for recipe data."""

    def __init__(self, messages: list):
        super().__init__(messages)
        self.messages = messages

    def format_message(self):
        return '\n'.join(['Recipe file is invalid.'] + self.messages)
