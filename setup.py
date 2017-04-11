import setuptools

import rpmlb

setuptools.setup(
    name='rpmlb',
    license='GPLv2+',
    version=rpmlb.__version__,
    description='Software Collection Rebuild Helper',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://gitlab.cee.redhat.com/jaruga/rhscl-builder',
    packages=[
        'rpmlb',
        'rpmlb.builder',
        'rpmlb.downloader',
    ],
    install_requires=[
        'PyYAML',
        'retrying',
    ],
    entry_points={
        'console_scripts': [
            'rpmlb=rpmlb.cli:main',
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    classifiers=[
        # TODO(Add items)
    ],
)
