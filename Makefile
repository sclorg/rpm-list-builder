PYTHON=`which python3 2> /dev/null || which python`
INSTALLED_FILES=installed_files.txt

default: test flake8
.PHONY: default

py:
	@echo "Python: $(PYTHON)"
.PHONY: py

clean:
	$(PYTHON) setup.py clean
	rm -rf build dist
.PHONY: clean

venv-install:
	rm -rf "`pwd`/vendor/venv"; \
	virtualenv --python="$(PYTHON)" "`pwd`/vendor/venv"; \
	source vendor/venv/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r test-requirements.txt; \
	deactivate
.PHONY: pip-install

venv-list:
	source vendor/venv/bin/activate; \
	pip list; \
	deactivate
.PHONY: pip-list

test: clean
	tox
.PHONY: test

flake8: clean
	tox -e flake8
.PHONY: flake8

setup-help:
	$(PYTHON) setup.py --help
.PHONY: setup-help

setup-test: clean
	$(PYTHON) setup.py test
.PHONY: setup-test

setup-install: clean
	$(PYTHON) setup.py install --user --prefix= --record "$(INSTALLED_FILES)"
.PHONY: setup-install

setup-uninstall:
	[ ! -f $(INSTALLED_FILES) ] && echo "$(INSTALLED_FILES) does not exist."; \
	cat $(INSTALLED_FILES) | xargs rm -fv
.PHONY: setup-uninstall

sdist:
	$(PYTHON) setup.py sdist
.PHONY: sdist

bdist-rpm:
	$(PYTHON) setup.py bdist --formats=rpm; \
	rpm -qpl ./dist/rhsclbuilder-*.noarch.rpm
.PHONY: bdist-rpm


setup-install: clean
	$(PYTHON) setup.py install --user --prefix= --record "$(INSTALLED_FILES)"
.PHONY: setup-install

setup-uninstall:
	[ ! -f $(INSTALLED_FILES) ] && echo "$(INSTALLED_FILES) does not exist."; \
	cat $(INSTALLED_FILES) | xargs rm -fv
.PHONY: setup-uninstall

sdist:
	$(PYTHON) setup.py sdist
.PHONY: sdist

bdist-rpm:
	$(PYTHON) setup.py bdist --formats=rpm; \
	rpm -qpl ./dist/rhsclbuilder-*.noarch.rpm
.PHONY: bdist-rpm

