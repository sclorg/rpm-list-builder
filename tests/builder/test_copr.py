from unittest import mock

import pytest

from rpmlb.builder.copr import CoprBuilder
from rpmlb.recipe import Recipe
from rpmlb.work import Work


@pytest.fixture
def work(valid_recipe_path):
    """Provide Work instance."""

    valid_recipe = Recipe(str(valid_recipe_path), 'rh-ror50')
    return Work(valid_recipe)


@pytest.fixture
def builder(work):
    pkg_cmd = 'fedpkg'
    copr_repo = 'ror50-test'
    return CoprBuilder(work, pkg_cmd=pkg_cmd, copr_repo=copr_repo)


def test_init(builder):
    assert builder


def test_init_raises_error_without_copr_repo(builder):
    pkg_cmd = 'fedpkg'
    with pytest.raises(ValueError):
        CoprBuilder(work, pkg_cmd=pkg_cmd)


def test_build_passes(builder, work):
    with mock.patch('rpmlb.utils.run_cmd',
                    mock.Mock(return_value=True)) as mock_run_cmd:
        package_dict = {'name': 'a'}
        builder.build(package_dict)
        mock_run_cmd.assert_any_call('rm -v *.rpm', check=False)
        mock_run_cmd.assert_any_call('fedpkg srpm')
        mock_run_cmd.assert_any_call('copr-cli build ror50-test *.rpm')
    assert True
