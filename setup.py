import setuptools

import rpmlb

setuptools.setup(
    name='rpmlb',
    license='GPLv2+',
    version=rpmlb.__version__,
    description='Software Collection Rebuild Helper',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://github.com/sclorg/rpm-list-builder',
    packages=[
        'rpmlb',
        'rpmlb.builder',
        'rpmlb.downloader',
    ],
    install_requires=[
        'PyYAML',
        'retrying',
        'click',
        'typing;python_version<"3.5"',
    ],
    entry_points={
        'console_scripts': [
            'rpmlb=rpmlb.cli:run',
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    classifiers=[
        'License :: OSI Approved :: '
        'GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
