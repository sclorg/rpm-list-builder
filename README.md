# RPM List Builder

RPM List Builder (rpmlb) helps you to build a list of defined RPM packages including Red Hat Software Collection (SCL) continually from the [recipe file](https://github.com/sclorg/rhscl-rebuild-recipes).


## Features

rpmlb ...

* Supports building a list of RPMs and SCL that is a extension of the RPM packages.
* Supports several build types
  * Mock(`mock`)
  * Copr(`copr-cli`)
  * Custom build by config file.
     You can customize the build with `rhpkg`, `fedpkg`, `koji`, `brew`, `dnf` and etc.
* Supports several types to get packages by recipe file.
  * Copy from local directory
  * Download by `rhpkg clone`.
  * Custom download. You can customize the way with `rhpkg`, `fedpkg`, and etc.
* Supports retry feature.
* Supports build by resume from any positon of the recipe file.

## Supported platforms

* Python 3.6 (Recommended), 3.5, 3.4

## Install

### Download

Download files from the git repository.

    $ git clone REPO_URL

Check release tags.

    $ git tag

Check out to release version.

    $ git checkout vX.Y.Z

### Install to virtualenv environment

You probably want to set up application on `virtualenv`.

Run below commmand to install `virtualenv`.
Python3 has `virtualenv` as a standard library.

    $ pip3 install virtualenv

Run below command to install application on virtualenv.

    $ make venv-install

Run below command to check installed command.

    $ source venv/bin/activate
    (venv) $ venv/bin/rpmlb -h
    (venv) $ deactivate

### Install directly by pip

Otherwise run appplication to install the application directly.

    $ pip3 install .

For example for installed python 3.6.1.

    $ sudo /usr/local/python-3.6.1/bin/pip3 install .

    $ pip3 list | grep rpmlb
    rpmlb         1.0.0

    $ which rpmlb
    /usr/local/python-3.6.1/bin/rpmlb

    $ rpmlb -h

## Usage

See [Users Guide](docs/users_guide.md).

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
