import os

from rpmlb.app import Application


def test_init():
    app = Application()
    assert app


def test_parse_argv_no_options():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50'])
    assert args
    assert args.recipe_file == '/tmp/ror.yml'
    assert args.recipe_id == 'rh-ror50'
    assert args.build == 'dummy'
    assert args.download == 'none'
    assert args.branch is None
    current_dir = os.getcwd()
    assert args.source_directory == current_dir


def test_parse_argv_build():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '--build', 'mock'])
    assert args
    assert args.build == 'mock'


def test_parse_argv_download():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '--download', 'rhpkg'])
    assert args
    assert args.download == 'rhpkg'


def test_parse_branch():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '--branch', 'rhscl-2.3-rh-ror42-rhel-7'])
    assert args
    assert args.branch == 'rhscl-2.3-rh-ror42-rhel-7'


def test_parse_source_directory():
    app = Application()
    args = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                           '--source-directory', '/tmp/foo'])
    assert args
    assert args.source_directory == '/tmp/foo'
