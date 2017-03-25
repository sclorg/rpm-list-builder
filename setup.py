import setuptools

import sclrbh

setuptools.setup(
    name='sclrbh',
    license='GPLv2+',
    version=sclrbh.__version__,
    description='Software Collection Rebuild Helper',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://gitlab.cee.redhat.com/jaruga/rhscl-builder',
    packages=[
        'sclrbh',
        'sclrbh.builder',
        'sclrbh.downloader',
    ],
    install_requires=[
        'PyYAML',
        'retrying',
    ],
    entry_points={
        'console_scripts': [
            'sclrbh=sclrbh.cli:main',
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    classifiers=[
        # TODO(Add items)
    ],
)
