import os
from unittest.mock import MagicMock

from rhsclbuilder.downloader.base import BaseDownloader
from rhsclbuilder.recipe import Recipe
import helper


def test_init():
    downloader = BaseDownloader()
    assert downloader


def test_run():
    for working_dir in helper.create_working_directory():
        downloader = BaseDownloader()
        downloader.download = MagicMock(return_value=True)

        downloader.downloaded_directory = working_dir
        recipe = Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')
        result = downloader.run(recipe)
        assert result
        assert os.path.isdir(working_dir)
        assert os.path.isdir(os.path.join(working_dir, '1'))
        assert os.path.isdir(os.path.join(working_dir, '2'))
