RPM List Builder
================

|Travis Build Status|

.. |Travis Build Status| image:: https://travis-ci.org/sclorg/rpm-list-builder.svg?branch=master
   :target: https://travis-ci.org/sclorg/rpm-list-builder

RPM List Builder (``rpmlb``) helps you to build a list of defined RPM
packages including Red Hat Software Collection (SCL) continually from
`a recipe file <https://github.com/sclorg/rhscl-rebuild-recipes>`__.

Features
--------

RPM List Builder ...

- Supports building a list of RPMs and SCL that is a extension of the
  RPM packages.
- Supports several build types

  - Mock (``mock``)
  - Copr (``copr-cli``)
  - Custom build by config file. You can customize the build with
    ``fedpkg``, ``rhpkg``, ``koji``, ``brew`` and etc.

- Supports several types to get packages by recipe file.

  - Copy from local directory
  - Download by ``fedpkg clone`` and ``rhpkg clone``.
  - Custom download. You can customize the way with ``fedpkg``, ``rhpkg``,
    and etc.

- Supports retry feature.
- Supports build by resume from any positon of the recipe file.

Supported platforms
-------------------

- Python 3.6 (Recommended), 3.5, 3.4

Install
-------

::

    $ pip3 install rpmlb

or

::

    $ git clone REPO_URL
    $ cd rpm-list-builder
    $ pip3 install .

Usage
-----

To show help.

::

    $ rpmlb -h

Basic usage.

::

    $ rpmlb \
      --download DOWNLOAD_TYPE \
      --build BUILD_TYPE \
      RECIPE_FILE \
      COLLECTION_ID

See `Users Guide <https://github.com/sclorg/rpm-list-builder/blob/master/docs/users_guide.md>`_ for detail.

Contributing
------------

Running test
^^^^^^^^^^^^

::

    $ pip3 install tox
    $ tox

License
-------

GPL-2.0
