import setuptools

import sclh

setuptools.setup(
    name='sclh',
    license='GPLv2+',
    version=sclh.__version__,
    description='Package builder for Red Hat Software Collection.',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://gitlab.cee.redhat.com/jaruga/rhscl-builder',
    packages=[
        'sclh',
        'sclh.builder',
        'sclh.downloader',
        'sclh.main',
    ],
    install_requires=[
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'rhscl-builder=sclh.main.cli:main',
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    classifiers=[
        # TODO(Add items)
    ],
)
