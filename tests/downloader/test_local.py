import os
import shutil
import tempfile

from rhsclbuilder.downloader.local import LocalDownloader
from rhsclbuilder.recipe import Recipe
import helper


def test_init():
    downloader = LocalDownloader()
    assert downloader


def test_download():
    downloader = LocalDownloader()
    # Create test data
    previous_dir = os.getcwd()
    src_dir = tempfile.mkdtemp(prefix='rhscl-builder-test-src-')
    recipe = Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')
    try:
        # Change directory
        os.chdir(src_dir)
        # Create test directory and file there
        os.makedirs('rh-ror50')
        os.makedirs('rubygem-arel')
        helper.touch(os.path.join('rh-ror50', 'a.txt'))
        helper.touch(os.path.join('rubygem-arel', 'b.txt'))

        for working_dir in helper.create_working_directory():
            downloader.downloaded_directory = working_dir
            downloader.run(recipe, source_directory=src_dir)
    finally:
        os.chdir(previous_dir)
        if src_dir:
            shutil.rmtree(src_dir)
