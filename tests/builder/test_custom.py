from pathlib import Path
from subprocess import STDOUT, check_output

# These tests use subprocess directly due to weird interactions with test_cli
# that lead to the command output being unreliable when using click.CliRunner.

_TEST_DIR = Path(__file__).parent.parent
_CUSTOM_HOOK_DIR = _TEST_DIR / "fixtures" / "custom"
_CUSTOM_HOOKS = _CUSTOM_HOOK_DIR / "echo.yml"
_EXAMPLE_RECIPE = _TEST_DIR / "fixtures" / "recipes" / "echo_recipe.yml"

# The custom echo backend is fast enough & simple enough that we just run a
# full end-to-end integration test as the custom builder's unit tests
#
# Both the download & build hooks need to be run, or the latter fail due to
# the missing package directories

_cli_command = [
    "rpmlb", "--custom-file", str(_CUSTOM_HOOKS),
    "--download", "custom", "--build", "custom",
    str(_EXAMPLE_RECIPE), "echo-packages",
]


def test_custom_build_hooks():
    """Test that `--build custom` works as expected"""
    output = check_output(_cli_command, universal_newlines=True, stderr=STDOUT)
    lines = output.strip().splitlines()
    # Only a unit test, so we don't explicitly check hook order,
    # just the expected implicit environment variable declarations
    hook_dir_line = "Using hook dir: {}".format(_CUSTOM_HOOK_DIR)
    package_1_build_line = "Building PKG: a-package"
    package_2_build_line = "Building PKG: another-package"
    assert hook_dir_line in lines
    assert package_1_build_line in lines
    assert package_2_build_line in lines
