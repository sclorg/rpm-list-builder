from contextlib import contextmanager
import logging
import os
import subprocess

LOG = logging.getLogger(__name__)


def p(text):
    print(repr(text))


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


def run_cmd_with_capture(cmd, **kwargs):
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE
    return run_cmd(cmd, **kwargs)


def run_cmd(cmd, **kwargs):
    try:
        LOG.debug('CMD: %s', cmd)
        if 'check' not in kwargs:
            kwargs['check'] = True
        # Use shell option to use wildcard "*".
        kwargs['shell'] = True

        result = subprocess.run(cmd, **kwargs)
        p(result)
        return result
    except subprocess.CalledProcessError as e:
        LOG.error('CMD: %s', e.cmd)
        LOG.error('Return Code: %s', e.returncode)
        LOG.error('Stdout: %s', e.stdout.decode('utf-8').split('\n'))
        LOG.error('Stderr: %s', e.stderr.decode('utf-8').split('\n'))
        raise e
