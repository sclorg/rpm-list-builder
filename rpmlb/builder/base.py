import logging
import re
import sys
from contextlib import contextmanager
from pathlib import Path

import retrying

from .. import utils

LOG = logging.getLogger(__name__)


class BaseBuilder:
    """A base class for the package builder."""

    def __init__(self):
        pass

    @staticmethod
    def get_instance(name: str):
        """Instantiate named builder.

        Keyword arguments:
            name: The name of the requested builder.

        Returns:
            Instance of the named builder.
        """

        class_name = 'rpmlb.builder.{0}.{1}Builder'.format(
            name,
            utils.camelize(name)
        )
        instance = utils.get_instance(class_name)

        LOG.debug('Loaded builder with %s', name)
        return instance

    def run(self, work, **kwargs):
        is_resume = kwargs.get('resume', False)
        resume_num = 0
        if is_resume:
            resume_num = kwargs['resume']

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
                if is_resume:
                    num = int(num_name)
                    if num < resume_num:
                        continue

                self.prepare(package_dict)
                self.build_with_retrying(package_dict, **kwargs)
            except Exception:
                message = 'pacakge_dict: {0}, num: {1}, work_dir: {2}'.format(
                    package_dict, num_name, work.working_dir)
                error = RuntimeError(message)
                tb = sys.exc_info()[2]
                error = error.with_traceback(tb)
                raise error

        self.after(work, **kwargs)
        return True

    def before(self, work, **kwargs):
        pass

    def after(self, work, **kwargs):
        pass

    def prepare(self, package_dict):
        if 'name' not in package_dict:
            raise ValueError('package_dict is invalid.')
        spec_file = '{0}.spec'.format(package_dict['name'])
        if 'macros' in package_dict:
            self.edit_spec_file_by_macros(spec_file, package_dict['macros'])
        if 'replaced_macros' in package_dict:
            self.edit_spec_file_by_replaced_macros(
                spec_file, package_dict['replaced_macros'])

    @retrying.retry(stop_max_attempt_number=3)
    def build_with_retrying(self, package_dict, **kwargs):
        self.build(package_dict, **kwargs)

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
            print('# Edited by rpmlb', file=target_file)

            yield source_file, target_file

    def edit_spec_file_by_macros(self, spec_file, macros_dict):
        if not isinstance(macros_dict, dict):
            return ValueError('macros should be dict object.')

        with self.edit_spec_file(spec_file) as (fh_r, fh_w):
            for key in list(macros_dict.keys()):
                value = macros_dict[key]
                if value is None or str(value) == '':
                    raise ValueError('macro is invalid in {0}.'.format(key))
                content = '%global {0} {1}\n'.format(key, value)
                fh_w.write(content)
            fh_w.write('\n')
            fh_w.write(fh_r.read())

    def edit_spec_file_by_replaced_macros(self, spec_file, macros_dict):
        if not isinstance(macros_dict, dict):
            return ValueError('macros should be dict object.')

        with self.edit_spec_file(spec_file) as (fh_r, fh_w):
            for line in fh_r:
                line = line.rstrip()
                for key in list(macros_dict.keys()):
                    value = macros_dict[key]
                    pattern = r'^%global\s+{0}\s+[^\s]+$'.format(key)
                    replaced_str = r'%global {0} {1}'.format(key, value)

                    line = re.sub(pattern, replaced_str, line)
                fh_w.write(line + '\n')
