import importlib
import logging
import os
import subprocess
import sys
from contextlib import contextmanager

LOG = logging.getLogger(__name__)


def p(text):
    print(repr(text))


def camelize(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def get_class(class_name: str, package: str = __package__):
    """Dynamically import class from a module.

    Keyword arguments:
        class_name: The class/attribute name in standard import form.
        package: Name of the package to import from (for relative imports).

    Returns:
        type: The requested class.
    """

    mod_name, class_name = class_name.rsplit(sep='.', maxsplit=1)
    module = importlib.import_module(mod_name, package)
    return getattr(module, class_name)


def get_instance(class_name: str, *args, **kwargs):
    """Dynamically instantiate a class.

    Keyword arguments:
        class_name: Absolute or relative import name of the class.
        *args: Positional arguments for the class __init__.
        **kwargs: Keyword arguments for the class __init__.

    Return:
        Instance of the specified class.
    """

    cls = get_class(class_name)
    return cls(*args, **kwargs)


@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    try:
        new_ab_dir = None
        if not os.path.isabs(new_dir):
            new_ab_dir = os.path.join(previous_dir, new_dir)
        else:
            new_ab_dir = new_dir
        # Use absolute path to show it on FileNotFoundError message.
        os.chdir(new_ab_dir)
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

        env = os.environ.copy()
        env['LC_ALL'] = 'C.utf-8'  # better to parse English output
        if 'env' in kwargs:
            env.update(kwargs['env'])
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


class CompletedProcess:
    """A error class to manage the result of command
    Use it instead of subprocess.CompletedProcess/CalledProcessError
    for old Pytyons (<= 3.4).
    """

    def __init__(self, cmd, returncode, stdout, stderr):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
