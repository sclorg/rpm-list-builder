import pytest
from unittest.mock import MagicMock

from rhsclbuilder.downloader.rhpkg import RhpkgDownloader
from rhsclbuilder.recipe import Recipe
import helper


def test_init():
    downloader = RhpkgDownloader()
    assert downloader


def test_download_branch():
    downloader = RhpkgDownloader()
    recipe = Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')
    downloader.do_rhpkg_and_checkout = MagicMock(return_value=True)
    for working_dir in helper.create_working_directory():
        downloader.downloaded_directory = working_dir
        downloader.run(recipe, branch='rhscl-foo')


def test_download_no_branch():
    downloader = RhpkgDownloader()
    recipe = Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')
    downloader.do_rhpkg_and_checkout = MagicMock(return_value=True)
    for working_dir in helper.create_working_directory():
        downloader.downloaded_directory = working_dir
        with pytest.raises(ValueError):
            downloader.run(recipe)
