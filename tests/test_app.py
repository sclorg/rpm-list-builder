"""Test argument parsing"""

import os

from rpmlb.cli import run


def test_parse_argv_no_options(tmpdir):
    """Tests proper default values of the CLI"""

    RECIPE_FILE = tmpdir.join('ror.yml')
    RECIPE_NAME = 'rh-ror50'

    # Prepare environment
    RECIPE_FILE.write('')

    # Parse the arguments
    with tmpdir.as_cwd():
        argv = list(map(str, [RECIPE_FILE, RECIPE_NAME]))
        args = run.make_context('rpmlb', argv).params

    current_dir = os.path.abspath(os.getcwd())

    assert args['recipe_file'] == str(RECIPE_FILE), 'Wrong recipe file path'
    assert args['recipe_name'] == str(RECIPE_NAME), 'Wrong recipe name'
    assert args['build'] == 'dummy', 'Wrong builder name'
    assert args['download'] == 'none', 'Wrong downloader name'
    assert args['branch'] is None, 'Superfluous branch'
    assert args['source_directory'] == current_dir
