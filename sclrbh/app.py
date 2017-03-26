import argparse
import logging
import os

import sclrbh
from sclrbh.recipe import Recipe
from sclrbh.builder.base import BaseBuilder
from sclrbh.downloader.base import BaseDownloader
from sclrbh.work import Work

LOG = logging.getLogger(__name__)
RECIPE_URL = 'https://github.com/sclorg/rhscl-rebuild-recipes'


class Application(object):
    """An application class."""

    def __init__(self):
        self._program = 'sclrbh'
        self._version = sclrbh.__version__

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
        work = None

        try:
            args = self.parse_argv(argv)

            # Load recipe
            recipe = Recipe(args.recipe_file, args.scl_id)

            args_dict = vars(args)
            work = Work(recipe, **args_dict)
            # Load downloader
            downloader = BaseDownloader.get_instance(args.download)
            # Load builder
            builder = BaseBuilder.get_instance(args.build)

            # Run downloader
            LOG.info('Downloading...')
            downloader.run(work, **args_dict)

            # Run builder
            LOG.info('Building...')
            builder.run(work, **args_dict)
            LOG.info('Done successfully.')
        except Exception as e:
            # work.close
            raise e
        finally:
            # work.close
            pass

    def parse_argv(self, argv=None):
        args = None
        if argv:
            args = argv[1:]
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'recipe_file',
            help='Recipe file like yml file in {0}'.format(RECIPE_URL)
        )
        parser.add_argument(
            'scl_id',
            help='ID in a recipe file. such as "python33", "rh-ror50"'
        )
        # General options
        help_message = (
            'Set download type. '
            'Value: {local, rhpkg, none}. Default: none'
        )
        parser.add_argument(
            '-D', '--download',
            default='none',
            help=help_message,
        )
        help_message = (
            'Set build type. '
            'Value: {mock, copr, dummy, custom}. Default: dummy'
        )
        parser.add_argument(
            '-B', '--build',
            default='dummy',
            help=help_message,
        )
        help_message = (
            'Change work-directory to DIR. '
            'Default is using creatd tmp directory.'
        )
        parser.add_argument(
            '-C', '--work-directory',
            help=help_message,
        )
        # Downloader options
        parser.add_argument(
            '-b', '--branch',
            help='Git branch used in SCL package if downloader is rhpkg.',
        )
        current_dir = os.getcwd()
        help_message = (
            'Package source directory used '
            'if downloader is local. Default is current directory.'
        )
        parser.add_argument(
            '-s', '--source-directory',
            default=current_dir,
            help=help_message,
        )
        # Builder options
        parser.add_argument(
            '-r', '--resume',
            type=int,
            help='Resume to build from the pacakge number',
        )
        parser.add_argument(
            '-M', '--mock-config',
            help='Mock config used if builder is mock',
        )
        parser.add_argument(
            '-c', '--copr-repo',
            help='Copr repo used if builder is copr',
        )
        parser.add_argument(
            '--custom-file',
            help='Custom script file used if builder is custom',
        )
        parsed_args = parser.parse_args(args)
        return parsed_args
