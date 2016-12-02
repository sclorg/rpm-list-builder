PYTHON=`which python3 2> /dev/null || which python`

default: test flake8
.PHONY: default

py:
	@echo "Python: $(PYTHON)"
.PHONY: py

clean:
	$(PYTHON) setup.py clean
	rm -rf build dist
.PHONY: clean

pip-install:
	virtualenv --python="$(PYTHON)" "`pwd`/vendor/virtualenv"; \
	source vendor/virtualenv/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r test-requirements.txt; \
	deactivate
.PHONY: pip-install

pip-update:
	source vendor/virtualenv/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r test-requirements.txt; \
	deactivate
.PHONY: pip-update

pip-list:
	source vendor/virtualenv/bin/activate; \
	pip list; \
	deactivate
.PHONY: pip-list

test: clean
	tox -e py3
.PHONY: test

flake8: clean
	tox -e flake8
.PHONY: flake8

sdist:
	$(PYTHON) setup.py sdist
.PHONY: sdist

bdist-rpm:
	$(PYTHON) setup.py bdist --formats=rpm; \
	rpm -qpl ./dist/rhsclbuilder-*.noarch.rpm
.PHONY: bdist-rpm

