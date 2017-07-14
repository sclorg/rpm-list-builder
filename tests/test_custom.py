import os
from unittest import mock

import pytest

import helper
from rpmlb.custom import Custom


@pytest.fixture
def valid_custom():
    """A Custom object with a valid custom file."""
    return Custom(helper.get_valid_custom_file())


def test_init_loads_file(valid_custom):
    assert valid_custom


def test_run_cmds_runs_cmds_on_valid_custom_file(valid_custom):
    random_file_foo = None
    random_file_bar = None
    try:
        random_file_foo = helper.get_random_generated_tmp_file()
        random_file_bar_part = helper.get_random_generated_tmp_file()

        content = {
            'build': [
                'touch {0}'.format(random_file_foo),
                'touch "{0}-$PKG"'.format(random_file_bar_part),
            ]
        }
        type(valid_custom).yaml_content = mock.PropertyMock(
                                          return_value=content)

        valid_custom.run_cmds('build', name='rubygem-bar')

        assert os.path.isfile(random_file_foo)
        random_file_bar = random_file_bar_part + '-rubygem-bar'
        assert os.path.isfile(random_file_bar)
    finally:
        if os.path.isfile(random_file_foo):
            os.remove(random_file_foo)
        if os.path.isfile(random_file_bar):
            os.remove(random_file_bar)


def test_run_cmds_skips_cmds_on_unknown_key(valid_custom):
    random_file_foo = None
    try:
        random_file_foo = helper.get_random_generated_tmp_file()

        content = {
            'build': [
                'touch {0}'.format(random_file_foo),
            ]
        }
        type(valid_custom).yaml_content = mock.PropertyMock(
                                          return_value=content)

        valid_custom.run_cmds('dummy')

        assert not os.path.isfile(random_file_foo)
    finally:
        if os.path.isfile(random_file_foo):
            os.remove(random_file_foo)


def test_yaml_content_returns_content(valid_custom):
    content = valid_custom.yaml_content
    assert content


def test_yaml_content_returns_singleton_object(valid_custom):
    content = valid_custom.yaml_content
    content2 = valid_custom.yaml_content
    assert content is content2
