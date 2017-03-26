# SCL Rebuild Helper

SCL Rebuild Helper (sclrbh) helps you to build packages for Red Hat Software Collection from the [recipe files](https://github.com/sclorg/rhscl-rebuild-recipes).


## Features

sclrbh ...

* Supports several builds: Mock(`mock`), Copr(`copr-cli`) and custom build. You can customize the build way by config file to use `koji`, `brew`, `dnf` and etc.
* Supports the way to get packages by recipe file.
  * Copy from local directory
  * Download by `rhpkg clone`.
* Supports retry feature.
* Supports build by resume from any positon of the recipe file.

## Supported platforms

* Python 3 (Recommended)
* Python 2.7

## Install

### Install to virtualenv environment

You probably want to set up application on `virtualenv`.

Run below commmand to install `virtualenv`.
Python3 has `virtualenv` as a standard library.

    $ pip3 install virtualenv

Run below command to install application on virtualenv.

    $ make venv-install

Run below command to check installed command.

    $ source venv/bin/activate
    (venv) $ venv/bin/sclrbh -h
    (venv) $ deactivate

### Install directly by pip

Otherwise run appplication to install the application directly.

    $ pip3 install .


## Contributing

### Running the test suite.

If you have not installed `virtualenv`, install `virtualenv`.

    $ pip3 install virtualenv

#### Minimal unit test

Create virtualenv environment for test.

    $ make venv-install-dev

Run the minimal unit test by pytest.

    $ make venv-test

#### Tox test

    $ pip3 install tox
    $ make tox

#### Integration test

This test may take a time for 5-10 mins.

    $ make venv-integration-test

#### All test

Run below command to run all the test that was mentioned above.

    $ make test-all


## License

GPL-2.0
