import os
from unittest import mock

from rpmlb.app import Application


def test_init():
    app = Application()
    assert app


def test_run_calls_run_internally():
    app = Application()
    app.run_internally = mock.MagicMock(return_value=True)
    app.run()
    assert app.run_internally.called


def test_run_returns_true_on_success():
    app = Application()
    app.run_internally = lambda *args: None
    assert app.run()


def test_run_returns_false_on_exception():
    app = Application()

    def run_internally(*args):
        raise RuntimeError('test')

    app.run_internally = run_internally
    assert not app.run()


def test_parse_argv_without_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50'])
    assert args_dict
    assert args_dict['recipe_file'] == '/tmp/ror.yml'
    assert args_dict['recipe_id'] == 'rh-ror50'
    assert args_dict['build'] == 'dummy'
    assert args_dict['download'] == 'none'
    assert 'branch' not in args_dict
    assert 'resume' not in args_dict
    current_dir = os.getcwd()
    assert args_dict['source_directory'] == current_dir


def test_parse_argv_with_build_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                                '--build', 'mock'])
    assert args_dict
    assert args_dict['build'] == 'mock'


def test_parse_argv_with_download_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                                '--download', 'rhpkg'])
    assert args_dict
    assert args_dict['download'] == 'rhpkg'


def test_parse_argv_with_branch_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                                '--branch', 'rhscl-2.3-rh-ror42-rhel-7'])
    assert args_dict
    assert args_dict['branch'] == 'rhscl-2.3-rh-ror42-rhel-7'


def test_parse_argv_with_source_directory_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                                '--source-directory', '/tmp/foo'])
    assert args_dict
    assert args_dict['source_directory'] == '/tmp/foo'


def test_parse_argv_with_resume_option_returns_dict():
    app = Application()
    args_dict = app.parse_argv(['prog', '/tmp/ror.yml', 'rh-ror50',
                                '--resume', '02'])
    assert args_dict
    assert args_dict['resume'] == 2
