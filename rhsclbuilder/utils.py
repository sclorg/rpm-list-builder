from contextlib import contextmanager
import logging
import os
import subprocess

LOG = logging.getLogger(__name__)


def camelize(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


# Get Class object for class_name: foo.bar.Bar
def get_class(class_name):
    components = class_name.split('.')
    module = __import__(components[0])
    for comp in components[1:]:
        module = getattr(module, comp)
    return module


def get_instance(class_name, *args, **kwargs):
    cls = get_class(class_name)
    return cls(args, kwargs)


@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(previous_dir)


def run_cmd(cmd, **kwargs):
    try:
        LOG.debug('CMD: %s', cmd)
        # args = cmd.split()
        check = kwargs['check'] if 'check' in kwargs else True
        # Use shell option to use wildcard "*".
        result = subprocess.run(
            cmd,
            check=check,
            shell=True,
            stderr=subprocess.STDOUT
        )
        return result
    except subprocess.CalledProcessError as e:
        LOG.error(e.cmd)
        LOG.error(e.message)
        LOG.error(e.returncode)
        LOG.error(e.output)
        raise e
