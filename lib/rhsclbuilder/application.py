import argparse
import logging
import os
import tempfile

import rhsclbuilder
from rhsclbuilder.recipe import Recipe
from rhsclbuilder import utils

LOG = logging.getLogger(__name__)


class Application(object):
    """An application class."""

    def __init__(self):
        self._program = 'rhscl-builder'
        self._version = rhsclbuilder.__version__

    def run(self, argv=None):
        LOG.info("Starting %s (%s)", self._program, self._version)
        is_error = False
        try:
            self.run_internally(argv)
        except KeyboardInterrupt as e:
            print('... stopped')
            LOG.error('Caught keyboard interrupt from user')
            LOG.exception(e)
            is_error = True

        raise SystemExit(is_error)

    def run_internally(self, argv):
        args = self.parse_argv(argv)
        # Load recipe
        recipe = Recipe(args.recipe_file)
        # Load downloader
        downloader_name = 'rhsclbuilder.downloader.{0}.{1}Downloader'.format(
            args.downloader,
            utils.camelize(args.downloader)
        )
        downloader = utils.import_class(downloader_name)
        working_dir = tempfile.mkdtemp(prefix='rhscl-builder-')
        LOG.info('Working directory: %s', working_dir)
        downloader.downloaded_directory = working_dir

        # Load builder

        # Run downloader
        downloader.run(recipe)
        # Run builder

    def parse_argv(self, argv=None):
        args = None
        if argv:
            args = argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('recipe_file')
        parser.add_argument('scl_id')
        parser.add_argument('-B', '--builder', default='copr')
        parser.add_argument('-D', '--downloader', default='local')
        parser.add_argument('-b', '--branch')
        current_dir = os.getcwd()
        parser.add_argument('-s', '--source-directory', default=current_dir)
        parsed_args = parser.parse_args(args)
        return parsed_args
