import setuptools

with open('README.rst') as f:
    readme = f.read().strip()


setuptools.setup(
    name='rpmlb',
    license='GPLv2+',
    use_scm_version=True,
    description='Software Collection Rebuild Helper',
    long_description=readme,
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
        'retry',
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
        'setuptools_scm',
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
