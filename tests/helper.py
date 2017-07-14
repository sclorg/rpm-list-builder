import os
import random
import shutil
import tempfile
from contextlib import contextmanager

TMP_FILE_PREFIX = 'rpmlb-tmp-'
RANDOM_BITS = 32


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(previous_dir)


@contextmanager
def pushd_tmp_dir():
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp(prefix=TMP_FILE_PREFIX)
        with pushd(tmp_dir):
            yield
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)


def get_random_generated_tmp_file():
    random_bits = random.getrandbits(RANDOM_BITS)
    random_hash = '%x' % random_bits
    tmp_file = os.path.join(tempfile.gettempdir(),
                            TMP_FILE_PREFIX + random_hash)
    return tmp_file


def remove_if_is_file(file):
    if os.path.isfile(file):
        os.remove(file)


def get_valid_recipe_file():
    return 'tests/fixtures/recipes/ror.yml'


def get_valid_custom_file():
    return 'tests/fixtures/custom/echo.yml'
