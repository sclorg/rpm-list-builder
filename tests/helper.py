from contextlib import contextmanager
import os
import shutil
import tempfile


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
        tmp_dir = tempfile.mkdtemp(prefix='rpmlb-tmp-')
        with pushd(tmp_dir):
            yield
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
