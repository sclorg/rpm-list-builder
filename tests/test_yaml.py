import os

import pytest

import helper
from rpmlb.yaml import Yaml


@pytest.fixture
def valid_yaml():
    """A Yaml object with a valid YAML file."""
    return Yaml(helper.get_valid_recipe_file())


def test_init_loads_file(valid_yaml):
    assert valid_yaml


def test_init_raises_error_on_not_existing_file():
    with pytest.raises(FileNotFoundError):
        Yaml('foo/dummy.yml')


def test_dump_prints_output(capsys, valid_yaml):
    valid_yaml.dump()
    stdout, stderr = capsys.readouterr()
    assert 'rh-ror50:' in stdout


def test_run_cmds_runs_cmd_by_cmd_element_type_string():
    # Test with generated file.
    # Because we can not test using stdout with capsys fixture,
    # the capsys does not capture stdout from subprocess in run_cmds.
    random_file = helper.get_random_generated_tmp_file()
    try:
        cmd_element = "touch {0}".format(random_file)
        Yaml.run_cmd_element(cmd_element)
        assert os.path.isfile(random_file)
    finally:
        helper.remove_if_is_file(random_file)


def test_run_cmds_runs_cmds_by_cmd_element_type_list():
    random_file_foo = helper.get_random_generated_tmp_file()
    random_file_bar_part = helper.get_random_generated_tmp_file()
    random_file_bar = random_file_bar_part + '-bar'
    try:

        cmd_element = [
            'touch {0}'.format(random_file_foo),
            'touch "{0}-$BAR"'.format(random_file_bar_part),
        ]
        env = {
            'BAR': 'bar'
        }
        Yaml.run_cmd_element(cmd_element, env=env)

        assert os.path.isfile(random_file_foo)
        assert os.path.isfile(random_file_bar)
    finally:
        helper.remove_if_is_file(random_file_foo)
        helper.remove_if_is_file(random_file_bar)


def test_run_cmds_raises_error_on_cmd_element_type_dict():
    cmd_element = {
        'a': 'b'
    }
    with pytest.raises(ValueError):
        Yaml.run_cmd_element(cmd_element)
