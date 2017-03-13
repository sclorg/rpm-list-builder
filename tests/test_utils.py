import os

from rhsclbuilder import utils


def test_camelize():
    new_word = utils.camelize('foo_bar')
    assert new_word == 'FooBar'


def test_get_class():
    cls = utils.get_class('rhsclbuilder.recipe.Recipe')
    assert cls
    cls = utils.get_class(
        'rhsclbuilder.downloader.local.LocalDownloader'
    )
    assert cls


def test_pushd():
    original_dir = os.getcwd()
    with utils.pushd('/tmp'):
        new_dir = os.getcwd()
        assert new_dir == '/tmp'
    current_dir = os.getcwd()
    assert current_dir == original_dir
