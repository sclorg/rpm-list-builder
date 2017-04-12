from contextlib import contextmanager
import logging
import os
import subprocess
import sys

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
    returncode = None
    stdout = ''
    stderr = ''
    proc = None
    try:
        check = True
        if 'check' in kwargs:
            check = kwargs['check']
            kwargs.pop('check', None)
        # Use shell option to use wildcard "*".
        kwargs['shell'] = True

        LOG.debug('CMD: %s, kwargs: %s', cmd, repr(kwargs))
        if 'env' in kwargs:
            # Keep current environment variables
            env = os.environ
            for key, value in list(kwargs['env'].items()):
                env[key] = value
            kwargs['env'] = env

        proc = subprocess.Popen(cmd, **kwargs)
        stdout, stderr = proc.communicate()
        returncode = proc.returncode
        if check and returncode != 0:
            LOG.error('CMD: [%s] failed at [%s]', cmd, os.getcwd())
            LOG.error('Return Code: %s', returncode)
            if stdout is not None:
                LOG.error('Stdout: %s', stdout)
            if stderr is not None:
                LOG.error('Stderr: %s', stderr)

            kwargs_dict = {}
            kwargs_dict['output'] = stdout
            if sys.version_info >= (3, 5):
                kwargs_dict['stderr'] = stderr
            raise subprocess.CalledProcessError(
                returncode, cmd, **kwargs_dict
            )
        return CompletedProcess(cmd, returncode, stdout, stderr)
    except Exception as e:
        try:
            proc.kill()
        except:
            pass
        raise e


class CompletedProcess(object):
    """A error class to manage the result of command
    Use it instead of subprocess.CompletedProcess/CalledProcessError
    for old Pytyons (<= 3.4).
    """

    def __init__(self, cmd, returncode, stdout, stderr):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
