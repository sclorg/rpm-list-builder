import os
import shutil
import tempfile


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def create_working_directory():
    working_dir = None
    try:
        working_dir = tempfile.mkdtemp(prefix='rhscl-builder-test-')
        yield working_dir
    finally:
        if os.path.isdir(working_dir):
            shutil.rmtree(working_dir)
