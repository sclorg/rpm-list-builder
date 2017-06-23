import pytest

from rpmlb.recipe import Recipe


@pytest.fixture
def ok_recipe():
    return Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')


def test_init(ok_recipe):
    assert ok_recipe


def test_recipe(ok_recipe):
    assert ok_recipe.recipe


def test_recipe_not_found():
    with pytest.raises(KeyError):
        Recipe('tests/fixtures/recipes/ror.yml', 'dummy')


def test_verify_returns_true_on_valid_recipe(ok_recipe):
    assert ok_recipe.verify()


def test_verify_raises_error_on_recipe_without_name(ok_recipe):
    del ok_recipe.recipe['name']
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_raises_error_on_recipe_with_empty_name(ok_recipe):
    ok_recipe.recipe['name'] = ''
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_returns_true_on_recipe_without_requires(ok_recipe):
    del ok_recipe.recipe['requires']
    assert ok_recipe.verify()


def test_verify_raises_error_on_recipe_with_non_list_requires(ok_recipe):
    ok_recipe.recipe['requires'] = 'abc'
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_raises_error_on_recipe_without_packages(ok_recipe):
    del ok_recipe.recipe['packages']
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_raises_error_on_recipe_with_empty_packages(ok_recipe):
    ok_recipe.recipe['packages'] = []
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_raises_error_on_recipe_with_non_list_packages(ok_recipe):
    ok_recipe.recipe['packages'] = 'abc'
    with pytest.raises(ValueError):
        ok_recipe.verify()


def test_verify_raises_error_on_recipe_with_empty_package_name(ok_recipe):
    ok_recipe.recipe['packages'] = [
        'foo',
        ''
    ]
    with pytest.raises(ValueError):
        ok_recipe.verify()
