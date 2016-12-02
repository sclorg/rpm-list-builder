from contextlib import contextmanager
import os


def camelize(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


# class_name: foo.bar.Bar
def import_class(class_name):
    components = class_name.split('.')
    module = __import__(components[0])
    for comp in components[1:]:
        module = getattr(module, comp)
    return module


@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(previous_dir)
