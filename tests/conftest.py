"""Test configuration for py.test."""

import os
import random
import sys
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Union

import pytest

pytest_plugins = ['helpers_namespace']

sys.path.append(os.path.join(os.path.dirname(__file__)))


# Fixture configuration

#: Number of bits in generated random numbers
RANDOM_BITS = 32
#: Common prefix of generated temporary files
TMP_FILE_PREFIX = 'rpmlb-tmp-'


# Helper functions

@pytest.helpers.register
@contextmanager
def pushd(target_dir: Union[str, Path]):
    """Change current directory to target_dir."""

    current_dir = os.getcwd()
    if isinstance(target_dir, Path):
        target_dir = str(target_dir)

    try:
        os.chdir(target_dir)
        yield
    finally:
        os.chdir(current_dir)


@pytest.helpers.register
def remove_if_is_file(path: Union[str, Path]):
    """Remove file if it exists."""

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_file():
        path.unlink()


@pytest.helpers.register
@contextmanager
def generate_tmp_path():
    """Generate randomly named temporary path.

    The file is removed at the exit from the context, if it exists.
    """

    tmp_path = Path(tempfile.gettempdir(), '{prefix}{suffix:x}'.format(
        prefix=TMP_FILE_PREFIX,
        suffix=random.getrandbits(RANDOM_BITS),
    ))

    try:
        yield tmp_path
    finally:
        remove_if_is_file(tmp_path)


@pytest.helpers.register
@contextmanager
def generate_tmp_path_list(count: int):
    """Generate multiple temporary paths.

    All files are removed at the exit from the context, if they exist.

    Keyword arguments:
        count: Number of paths to generate.
    """

    with ExitStack() as stack:
        tmp_path_list = [
            stack.enter_context(generate_tmp_path()) for __ in range(count)
        ]

        yield tmp_path_list


# Fixtures

@pytest.fixture
def random_file_path():
    """Provide path to a random temporary file."""

    with generate_tmp_path() as path:
        yield path


@pytest.fixture(scope='session')
def valid_recipe_path():
    """Provide path to a valid recipe file."""

    return Path('tests/fixtures/recipes/ror.yml')


@pytest.fixture(scope='session')
def valid_custom_file_path():
    """Provide path to a valid custom file."""

    return Path('tests/fixtures/custom/echo.yml')
