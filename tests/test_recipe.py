import pytest

from sclh.recipe import Recipe


@pytest.fixture
def ok_recipe():
    return Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')


def test_init(ok_recipe):
    assert ok_recipe


def test_scl(ok_recipe):
    assert ok_recipe.scl


def test_scl_not_found():
    with pytest.raises(KeyError):
        Recipe('tests/fixtures/recipes/ror.yml', 'dummy')


def test_verify(ok_recipe):
    assert ok_recipe.verify
