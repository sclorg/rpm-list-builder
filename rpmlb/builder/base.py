import logging
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping, Match

from retry.api import retry_call

from .. import utils
from ..work import Work
from ..yaml import Yaml

LOG = logging.getLogger(__name__)


#: Regular expression for finding macro definitions
MACRO_REGEX = re.compile(
    r'''^
    %global\s+                   # beginning of definition
    (?P<name>[^\s]+)\s+          # one-word name
    (?P<value>(?:.|(?<=\\)\n)+)  # value including spaces and escaped newlines
    $''',
    flags=re.MULTILINE | re.VERBOSE,
)


class BaseBuilder:
    """A base class for the package builder."""

    def __init__(self, work: Work, **options):
        """Initialize the builder to a valid state.

        Keyword arguments:
            work: Overview of the work to do.
            options: Command line options for the builder to process.
        """
        if 'pkg_cmd' not in options:
            raise ValueError('pkg_cmd is required.')
        self._pkg_cmd = options['pkg_cmd']

    @staticmethod
    def get_instance(name: str, work: Work, **options):
        """Instantiate named builder.

        Keyword arguments:
            name: The name of the requested builder.
            work: Overview of the work to do.
            options: Command line options for the builder to process.

        Returns:
            Instance of the named builder.
        """

        class_name = 'rpmlb.builder.{0}.{1}Builder'.format(
            name,
            utils.camelize(name)
        )
        instance = utils.get_instance(class_name, work, **options)

        LOG.debug('Loaded builder with %s', name)
        return instance

    def run(self, work, **kwargs):
        is_resume = kwargs.get('resume', False)

        if is_resume:
            message = (
                'Skip the process before build, '
                'because the resume option was used.'
            )
            LOG.info(message)
        else:
            self.before(work, **kwargs)

        for package_dict, num_name in work.each_package_dir():
            try:
                if self._is_build_skipped(package_dict, num_name,
                                          is_resume, **kwargs):
                    continue

                self.prepare(package_dict, **kwargs)

                # Repeat the call in case of failure
                retry_count = kwargs.get('retry', 0)
                retry_call(
                    self.build, fargs=(package_dict,), fkwargs=kwargs,
                    tries=retry_count+1,  # 0 tries == no call
                )

            except Exception:
                message = 'pacakge_dict: {0}, num: {1}, work_dir: {2}'.format(
                    package_dict, num_name, work.working_dir)
                error = RuntimeError(message)
                tb = sys.exc_info()[2]
                error = error.with_traceback(tb)
                raise error

        self.after(work, **kwargs)
        return True

    def before(self, work: Work, **options):
        """One-time build setup.

        This method is intended for setting up the whole build process,
        and it is skipped when using the resume.
        For preparation/initialization of the builder itself, use `__init__`.

        Keyword arguments:
            work: Overview of the work to do.
            options: Command line option for the builder to process.
        """

    def after(self, work: Work, **options):
        """Final build clean-up.

        This method is intended for cleaning up after successful build,
        and it is called once all the work is completed.

        Keyword arguments:
            work: Overview of the work that has been done.
            options: Command line option for the builder to process.
        """

    def prepare(self, package_dict: Mapping[str, Any], **options):
        """Prepare single package for a build.

        Keyword arguments:
            package_dict: A dictionary of package metadata.
            options: Command line option for the builder to process.
        """

        if 'name' not in package_dict:
            raise ValueError('package_dict is invalid.')

        spec_file_path = Path('{name}.spec'.format_map(package_dict))

        with self.edit_spec_file(spec_file_path) as (source_file, target_file):
            content_stream = iter(source_file)  # Start modifications

            if 'replaced_macros' in package_dict:
                content_stream = self.replace_macros(
                    content_stream,
                    package_dict['replaced_macros'],
                )

            if 'macros' in package_dict:
                content_stream = self.add_macros(
                    content_stream,
                    package_dict['macros'],
                )

            # Perform any extra edits needed by derived builder
            content_stream = self.prepare_extra_steps(
                content_stream,
                package_dict,
            )

            target_file.write(''.join(content_stream))  # End modifications

        if 'cmd' in package_dict:
            env = {}
            dist = options.get('dist')
            if dist:
                env['DIST'] = dist
            Yaml.run_cmd_element(package_dict['cmd'], env=env)

    def build(self, package_dict, **kwargs):
        raise NotImplementedError('Implement this method.')

    @staticmethod
    @contextmanager
    def edit_spec_file(target_path: Path):
        """Safely edit a SPEC file in-place.

        The target is backed up as '{target}.orig' if needed.

        Keyword arguments:
            target_path: The modified SPEC file path.

        Returns:
            Context manager providing open handles
            for input and output file.
        """

        # Ensure path type
        if not isinstance(target_path, Path):
            target_path = Path(target_path)

        # Back up the original
        source_path = target_path.with_suffix('.spec.orig')
        if not source_path.exists():
            target_path.rename(source_path)

        # Provide the handles
        with source_path.open(mode='r') as source_file, \
                target_path.open(mode='w') as target_file:
            yield source_file, target_file

            # Ensure that all unprocessed source contents
            # are written to the target
            target_file.write(source_file.read())

    @staticmethod
    def add_macros(source: Iterator[str], macros: Mapping[str, str]):
        """Add macro definitions to the source stream.

        Keyword arguments:
            source: The source file iterator.
            macros: Mapping of macro name to macro definition
                    for all macros to add.

        Yields:
            Lines of the modified file.
        """

        # Prepend all definitions before the stream
        for name, value in macros.items():
            yield '%global {name} {value}\n'.format(name=name, value=value)

        # Pass the rest of the file
        yield from source

    @staticmethod
    def replace_macros(source: Iterator[str], macros: Mapping[str, str]):
        """Replace macros in the source stream with new values.

        Keyword arguments:
            source: The source file iterator.
            macros: Mapping of macro name to macro definition
                    for all macros to be replaced.

        Yields:
            Lines of the modified file.
        """

        def replacement(match: Match) -> str:
            """Macro replacement logic"""

            macro_name = match.group('name')
            macro_value = macros.get(macro_name, match.group('value'))
            return '%global {} {}'.format(macro_name, macro_value)

        # Need whole file contents for matching multi-line macros
        contents = ''.join(source)

        # Substitute all macros
        contents = MACRO_REGEX.sub(replacement, contents)

        # Pass the modified lines
        yield from contents.splitlines(keepends=True)

    def prepare_extra_steps(
        self,
        source: Iterator[str],
        package_metadata: Mapping[str, Any]
    ):
        """Builder-specific package preparation.

        Override if needed.

        Keyword arguments:
            source: The source file iterator.
            package_metadata: The metadata of the prepared package,
                as passed to prepare().
        """

        yield from source  # pass for generators

    def _is_build_skipped(self, package_dict: dict, num_name: str,
                          is_resume: bool, **kwargs):
        """Return if skip a build for a pacakge.

        Override if needed.

        Keyword arguments:
            package_dict: A dictionary of package metadata.
            num_name: A package's order number string.
            is_redume: if redume or not.
            kwargs: option arguments.
        """

        if not package_dict:
            raise ValueError('package_dict is required.')
        if not num_name:
            raise ValueError('num_name is required.')

        resume_num = 0
        if is_resume:
            resume_num = kwargs['resume']
        dist = kwargs.get('dist')

        is_skipped = False
        if is_resume:
            num = int(num_name)
            if num < resume_num:
                is_skipped = True
        elif dist and 'dist' in package_dict:
            pattern = re.compile(package_dict['dist'])
            if not pattern.match(dist):
                is_skipped = True
        return is_skipped
