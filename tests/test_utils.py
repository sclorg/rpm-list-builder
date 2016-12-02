import os

from rhsclbuilder import utils


def test_camelize():
    new_word = utils.camelize('foo_bar')
    assert new_word == 'FooBar'


def test_import_class():
    module = utils.import_class('rhsclbuilder.recipe.Recipe')
    assert module


def test_pushd():
    original_dir = os.getcwd()
    with utils.pushd('/tmp'):
        new_dir = os.getcwd()
        assert new_dir == '/tmp'
    current_dir = os.getcwd()
    assert current_dir == original_dir
