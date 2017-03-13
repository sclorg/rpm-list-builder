import argparse
import logging
import os

import rhsclbuilder
from rhsclbuilder.recipe import Recipe
from rhsclbuilder.builder.base import BaseBuilder
from rhsclbuilder.downloader.base import BaseDownloader
from rhsclbuilder.work import Work

LOG = logging.getLogger(__name__)
RECIPE_URL = 'https://github.com/sclorg/rhscl-rebuild-recipes'


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
        work = None

        try:
            args = self.parse_argv(argv)

            # Load recipe
            recipe = Recipe(args.recipe_file, args.scl_id)
            work = Work(recipe)
            # Load downloader
            downloader = BaseDownloader.get_instance(args.downloader)
            # Load builder
            builder = BaseBuilder.get_instance(args.builder)

            # Run downloader
            LOG.info('Downloading...')
            downloader.run(
                work,
                source_directory=args.source_directory,
                branch=args.branch
            )

            # Run builder
            LOG.info('Building...')
            builder.run(
                work,
                copr_repo=args.copr_repo
            )
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
        parser.add_argument(
            '-B', '--builder',
            default='copr',
            help='Set builder. The value is copr. Default: copr'
        )
        parser.add_argument(
            '-D', '--downloader',
            default='local',
            help='Set downloader. The values are local, rhpkg. Default: local',
        )
        parser.add_argument(
            '-b', '--branch',
            help='Git branch used in SCL package if downloader is rhpkg.',
        )
        current_dir = os.getcwd()
        help_message = 'Package source directory used ' + \
            'if downloader is local. Default is current directory.'
        parser.add_argument(
            '-s', '--source-directory',
            default=current_dir,
            help=help_message,
        )
        parser.add_argument(
            '-C', '--copr-repo',
            help='Copr repo used if builder is copr',
        )
        parsed_args = parser.parse_args(args)
        return parsed_args
