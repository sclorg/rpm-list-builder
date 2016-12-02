import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import rhsclbuilder  # noqa: E402

setup(
    name='rhsclbuilder',
    license='GPLv2+',
    version=rhsclbuilder.__version__,
    description='Package builder for Red Hat Software Collection.',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://gitlab.cee.redhat.com/jaruga/rhscl-builder',
    package_dir={'': 'lib'},
    packages=[
        'rhsclbuilder',
        #'rhsclbuilder.builder',
        'rhsclbuilder.downloader',
        'rhsclbuilder.main',
    ],
    entry_points={
        # 'console_scripts': [
        #     'rhscl-builder=rhsclbuilder.main.cli:main',
        # ]
    },
    setup_requires=[],
    classifiers=[
        # TODO(Add items)
    ],
)
