import os

from sclh.application import Application


def test_init():
    app = Application()
    assert app


def test_parse_argv_no_options():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50'])
    assert args
    assert args.recipe_file == '/tmp/ror.yml'
    assert args.scl_id == 'rh-ror50'
    assert args.builder == 'dummy'
    assert args.downloader == 'local'
    assert args.branch is None
    current_dir = os.getcwd()
    assert args.source_directory == current_dir


def test_parse_argv_builder():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '-B', 'mock'])
    assert args
    assert args.builder == 'mock'


def test_parse_argv_downloader():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '-D', 'rhpkg'])
    assert args
    assert args.downloader == 'rhpkg'


def test_parse_branch():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '-b', 'rhscl-2.3-rh-ror42-rhel-7'])
    assert args
    assert args.branch == 'rhscl-2.3-rh-ror42-rhel-7'


def test_parse_source_directory():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '-s', '/tmp/foo'])
    assert args
    assert args.source_directory == '/tmp/foo'
