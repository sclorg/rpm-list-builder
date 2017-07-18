import pytest

from rpmlb.yaml import Yaml


@pytest.fixture
def valid_yaml(valid_recipe_path):
    """A Yaml object with a valid YAML file."""
    return Yaml(str(valid_recipe_path))


def test_init_loads_file(valid_yaml):
    assert valid_yaml


def test_init_raises_error_on_not_existing_file():
    with pytest.raises(FileNotFoundError):
        Yaml('foo/dummy.yml')


def test_dump_prints_output(capsys, valid_yaml):
    valid_yaml.dump()
    stdout, stderr = capsys.readouterr()
    assert 'rh-ror50:' in stdout


def test_run_cmds_runs_cmd_by_cmd_element_type_string(random_file_path):
    # Test with generated file.
    # Because we can not test using stdout with capsys fixture,
    # the capsys does not capture stdout from subprocess in run_cmds.
    cmd_element = "touch {0!s}".format(random_file_path)
    Yaml.run_cmd_element(cmd_element)
    assert random_file_path.is_file()


def test_run_cmds_runs_cmds_by_cmd_element_type_list():
    with pytest.helpers.generate_tmp_path_list(2) as tmp_files:
        random_file_foo, random_file_bar_part = tmp_files
        random_file_bar = random_file_bar_part.with_name(
            random_file_bar_part.name + '-bar'
        )

        cmd_element = [
            'touch {0}'.format(random_file_foo),
            'touch "{0}-$BAR"'.format(random_file_bar_part),
        ]
        env = {
            'BAR': 'bar'
        }
        Yaml.run_cmd_element(cmd_element, env=env)

        assert random_file_foo.is_file()
        assert random_file_bar.is_file()


def test_run_cmds_raises_error_on_cmd_element_type_dict():
    cmd_element = {
        'a': 'b'
    }
    with pytest.raises(ValueError):
        Yaml.run_cmd_element(cmd_element)
