import logging
import os
import re
from retrying import retry

# from rhsclbuilder import utils

LOG = logging.getLogger(__name__)


class BaseBuilder(object):
    """A base class for the package builder."""

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls, name):
        # TODO: Use reflection.
        # class_name = 'rhsclbuilder.builder.{0}.{1}Builder'.format(
        #     name,
        #     utils.camelize(name)
        # )
        # return utils.get_instance(class_name)
        instance = None
        if name == 'mock':
            from rhsclbuilder.builder.mock import MockBuilder
            instance = MockBuilder()
        elif name == 'copr':
            from rhsclbuilder.builder.copr import CoprBuilder
            instance = CoprBuilder()
        elif name == 'custom':
            from rhsclbuilder.builder.custom import CustomBuilder
            instance = CustomBuilder()
        elif name == 'dummy':
            from rhsclbuilder.builder.dummy import DummyBuilder
            instance = DummyBuilder()
        else:
            raise ValueError('name is invalid.')
        return instance

    def run(self, work, **kwargs):
        self.before_run(work, **kwargs)

        is_resume = 'resume' in kwargs and kwargs['resume']
        resume_num = 0
        if is_resume:
            resume_num = kwargs['resume']

        for package_dict, num_dir_name in work.each_package_dir():
            if is_resume:
                num = int(num_dir_name)
                if num < resume_num:
                    continue

            self.prepare(package_dict)
            self.build(package_dict, **kwargs)

        self.after_run(work, **kwargs)

    def before_run(self, work, **kwargs):
        pass

    def after_run(self, work, **kwargs):
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

    @retry(stop_max_attempt_number=3)
    def build(self, package_dict, **kwargs):
        raise NotImplementedError('Implement this method.')

    def edit_spec_file(self, spec_file):
        spec_file_origin = '{0}.orig'.format(spec_file)
        os.rename(spec_file, spec_file_origin)
        fh_r = None
        fh_w = None
        try:
            fh_r = open(spec_file_origin, 'r')
            fh_w = open(spec_file, 'w')
            fh_w.write('# Edited by rhscl-builder\n')
            yield(fh_r, fh_w)
        finally:
            if fh_w:
                fh_w.close()
            if fh_r:
                fh_r.close()

    def edit_spec_file_by_macros(self, spec_file, macros_dict):
        if not isinstance(macros_dict, dict):
            return ValueError('macros should be dict object.')

        for fh_r, fh_w in self.edit_spec_file(spec_file):
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

        for fh_r, fh_w in self.edit_spec_file(spec_file):
            for line in fh_r:
                line = line.rstrip()
                for key in list(macros_dict.keys()):
                    value = macros_dict[key]
                    pattern = r'^%global\s+{0}\s+[^\s]+$'.format(key)
                    replaced_str = r'%global {0} {1}'.format(key, value)

                    line = re.sub(pattern, replaced_str, line)
                fh_w.write(line + '\n')
