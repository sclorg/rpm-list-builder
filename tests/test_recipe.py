from collections import defaultdict
from collections.abc import Mapping

import pytest

from rpmlb.recipe import Recipe


@pytest.fixture
def ok_recipe():
    return Recipe('tests/fixtures/recipes/ror.yml', 'rh-ror50')


@pytest.fixture
def invalid_pkg_type():
    """Package entry of invalid type"""

    return float('nan')  # anything but str or Mapping


@pytest.fixture
def invalid_pkg_content():
    """Package entry with an invalid content"""

    return {'pkg-a': {}, 'pkg-b': {}}


@pytest.fixture
def invalid_recipe(ok_recipe, invalid_pkg_type, invalid_pkg_content):
    """Recipe with invalid package contents"""

    ok_recipe.recipe['packages'] += [
        invalid_pkg_content,
        invalid_pkg_type,
    ]

    return ok_recipe


@pytest.fixture
def bootstrap_recipe(ok_recipe):
    """Recipe with multiple package instances that need bootstrapping"""

    ok_recipe.recipe['packages'] += [
        'pkg-a', 'pkg-b',
        'pkg-a', 'pkg-b',
        'pkg-a', 'pkg-b',
    ]

    return ok_recipe


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


def test_package_name_type_checks():
    """Invalid package types are reported."""

    invalid_type = float('nan')

    with pytest.raises(ValueError):
        Recipe._package_name(invalid_type)

    invalid_contents = {'pkg-a': {}, 'pkg-b': {}}

    with pytest.raises(ValueError):
        Recipe._package_name(invalid_contents)


def test_package_normalization_type_checks(invalid_recipe):
    """Invalid packages are reported when normalizing."""

    with pytest.raises(ValueError):
        list(invalid_recipe.each_normalized_package())


def test_normalized_packages_have_expected_format(ok_recipe):
    """After normalization, all packages have expected format."""

    def valid_item(package: Mapping, key: str, types: tuple):
        """Check validity of a package metadata item."""

        exists = key in package
        value = package.get(key, None)
        valid_type = isinstance(value, types)

        return exists and valid_type

    all_packages = list(ok_recipe.each_normalized_package())
    packages_with_macros = [pkg for pkg in all_packages if 'macros' in pkg]
    packages_with_replaced_macros = [
        pkg for pkg in all_packages if 'replaced_macros' in pkg
    ]

    # Each package has a name
    assert all('name' in pkg for pkg in all_packages), all_packages

    # Each package has bootstrap position of correct type
    key_types = 'bootstrap_position', (type(None), int)
    assert all(valid_item(pkg, *key_types) for pkg in all_packages), \
        all_packages

    # Each macros value is a mapping
    key_types = 'macros', (Mapping,)
    assert all(valid_item(pkg, *key_types) for pkg in packages_with_macros), \
        packages_with_macros

    # Each replaced_macros value is a mapping
    key_types = 'replaced_macros', (Mapping,)
    assert all(
        valid_item(pkg, *key_types)
        for pkg in packages_with_replaced_macros
    ), packages_with_replaced_macros


def test_bootstrap_sequence_increments_correctly(bootstrap_recipe):
    """Packages that needs bootstrapping are correctly marked as such."""

    sequences = defaultdict(list)
    for pkg in bootstrap_recipe.each_normalized_package():
        sequences[pkg['name']].append(pkg['bootstrap_position'])

    assert sequences['pkg-a'] == [1, 2, None], sequences['pkg-a']
