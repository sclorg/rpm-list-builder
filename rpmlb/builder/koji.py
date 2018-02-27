"""Builder interface for the Koji build service."""

import logging
import re
from pathlib import Path
from typing import Iterator, Optional, Sequence

from ..utils import run_cmd, run_cmd_with_capture
from ..work import Work
from .base import BaseBuilder

LOG = logging.getLogger(__name__)


class KojiBuilder(BaseBuilder):
    """Builder interface for the Koji build service."""

    DEFAULT_TARGET_FORMAT = 'sclo{epel}-{collection}-rh-el{epel}'

    def __init__(
        self,
        work: Work,
        *,
        koji_scratch: bool = False,
        koji_epel: int = None,
        koji_target_format: str = None,
        koji_owner: str = None,
        koji_profile: Optional[str] = None,
        **extra_options
    ):
        """Initialize the builder.

        Keyword arguments:
            work: Overview of the work to do.
            koji_scratch: Indicates if the --scratch build option
                should be used.
            koji_epel: Version number of the EPEL to build for.
            koji_target_format: Format string for the target to build into.
            koji_owner: The user name of the owner of packages
                newly added to a build tag.
            koji_profile: Name of the configuration profile to use.
        """

        # Validity checks
        if koji_epel is None:
            raise ValueError('koji_epel parameter is required.')
        if koji_owner is None:
            raise ValueError('koji_owner parameter is required.')

        #: The collection to build
        self.collection = work._recipe._collection_id

        #: EPEL version to build for
        self.epel = koji_epel

        #: Format string for the build target
        self.target_format = koji_target_format or self.DEFAULT_TARGET_FORMAT

        #: Owner of packages added by this builder into a tag
        self.owner = koji_owner

        #: The configuration profile to use
        self.profile = koji_profile

        #: Scratch build indicator
        self.scratch_build = koji_scratch

        # Private target destination cache
        self._destination_tag_cache = {}

    @property
    def base_command(self) -> Sequence[str]:
        """Basis of the command for build service interaction."""

        binary = 'koji'

        if self.profile is None:
            return [binary]
        else:
            return [binary, '--profile', self.profile]

    @property
    def target(self) -> str:
        """The koji target to build into."""

        return self.target_format.format(
            collection=self.collection,
            epel=self.epel,
        )

    @staticmethod
    def adjust_bootstrap_release(
        source: Iterator[str],
        position: Optional[int]
    ):
        """Adjust Release value for bootstrapping, if necessary.

        Keyword arguments:
            source: The source file iterator.
            position: The position in the bootstrap sequence.

        Yields:
            Modified lines.
        """

        # Pass source if not bootstrapping
        if position is None:
            return source

        dist_original = re.compile(r'%\{?\??dist\}?')
        dist_replaced = r'.bs{:02}\g<0>'.format(position)

        for line in source:
            if line.startswith('Release:'):
                line = dist_original.sub(dist_replaced, line)

            yield line

    def prepare_extra_steps(self, source, package_dict):
        """Koji-specific SPEC adjustments."""

        # Add .bsXX to release tag on bootstrap
        contents = self.adjust_bootstrap_release(
            source=source,
            position=package_dict['bootstrap_position'],
        )

        return contents

    def build(self, package_dict, **kwargs):
        """Build a package using Koji instance"""

        base_name = package_dict['name']
        full_name = self._full_package_name(base_name, self.collection)
        srpm_path = self._make_srpm(
            name=base_name,
            collection=self.collection,
            epel=self.epel,
        )

        self._add_package(full_name)
        self._submit_build(srpm_path)
        self._wait_for_repo()

    @staticmethod
    def _full_package_name(base_name: str, collection: str) -> str:
        """Determine what the full name of the package should be
        after applying the collection prefix.

        Keyword arguments:
            base_name: Name of the package, without the collection part.
            collection: Name/identification of the package's collection.

        Returns:
            Canonical full name.
        """

        # The metapackage
        if base_name == collection:
            return base_name
        else:
            return '-'.join((collection, base_name))

    @staticmethod
    def _make_srpm(base_name: str, collection: str, epel: int) -> Path:
        """Create SRPM of the specified name in current directory.

        Keyword arguments:
            base_name: Name of the package to create,
                without collection prefix.
            collection: Name/identification of the package's collection.
            epel: The EPEL version to build for.

        Returns:
            Path to the created SRPM.
        """

        spec_path = Path('.'.join((base_name, 'spec')))
        if not spec_path.exists():
            raise FileNotFoundError(spec_path)

        # Mimic rpkg behaviour
        directory_kinds = 'source', 'spec', 'build', 'srcrpm', 'rpm', 'top'
        cwd = Path.cwd()

        # directories
        define_list = [
            '_{kind}dir {cwd}'.format(kind=k, cwd=cwd) for k in directory_kinds
        ]
        # dist tag
        define_list.append('dist .el{epel}'.format(epel=epel))
        # collection name – needed to generate prefixed package
        define_list.append('scl {collection}'.format(collection=collection))

        # Assemble the command
        command = ['rpmbuild']
        command += ['--define="{d}"'.format(d=d) for d in define_list]
        command += ['-bs', str(spec_path)]

        run_cmd_with_capture(' '.join(command))

        srpm_glob = '{full_name}-*.src.rpm'.format(
            full_name=KojiBuilder._full_package_name(base_name, collection),
        )
        srpm_path, = cwd.glob(srpm_glob)
        return srpm_path

    @property
    def _destination_tag(self) -> str:
        """Queries the destination tag for a current target."""

        # Destination tag is dependent on target name and profile
        # Note: extract to generic utility decorator?
        cache_key = self.profile, self.target

        cached = self._destination_tag_cache.get(cache_key, None)
        if cached is not None:
            return cached

        query = ['list-targets', '--name={self.target}'.format(self=self)]

        # FIXME: ugly parsing of koji output
        raw_output = run_cmd_with_capture(' '.join(self.base_command + query))
        target_line = raw_output.stdout.splitlines()[2]
        destination_tag = target_line.split()[-1].decode('utf-8')

        LOG.debug('Destination tag: {}'.format(destination_tag))

        self._destination_tag_cache[cache_key] = destination_tag
        return destination_tag

    def _add_package(self, name: str) -> None:
        """Add package to the destination tag for the target.

        Keyword arguments:
            name: Name of the package to add.
        """

        # Command is safely ignored if the package is in the tag already
        command = [
            'add-pkg',
            '--owner={owner}'.format(owner=self.owner),
            self._destination_tag,
            name,
        ]
        run_cmd(' '.join(self.base_command + command))

    def _submit_build(self, srpm_path: Path) -> None:
        """Submit build to the build service.

        Keyword arguments:
            srpm_path: Path to the SRPM to build.
            scratch_build: If true, build with scratch option
        """

        command = self.base_command + ['build']

        if self.scratch_build:
            command.append('--scratch')

        arguments = [self.target, str(srpm_path)]

        run_cmd(' '.join(command + arguments))

    def _wait_for_repo(self) -> None:
        """Wait for the package to appear in build repository."""

        # Packages are not submitted to repository on scratch builds
        if self.scratch_build:
            return

        command = self.base_command + ['wait-repo', '--target', self.target]
        run_cmd(' '.join(command))
