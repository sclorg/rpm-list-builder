import setuptools

import rhsclbuilder

setuptools.setup(
    name='rhsclbuilder',
    license='GPLv2+',
    version=rhsclbuilder.__version__,
    description='Package builder for Red Hat Software Collection.',
    author='Jun Aruga',
    author_email='jaruga@redhat.com',
    url='https://gitlab.cee.redhat.com/jaruga/rhscl-builder',
    packages=[
        'rhsclbuilder',
        'rhsclbuilder.builder',
        'rhsclbuilder.downloader',
        'rhsclbuilder.main',
    ],
    install_requires=[
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'rhscl-builder=rhsclbuilder.main.cli:main',
        ]
    },
    setup_requires=[
        'pytest-runner',
    ],
    classifiers=[
        # TODO(Add items)
    ],
)
