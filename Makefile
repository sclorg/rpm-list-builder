PYTHON=python3
PIP=pip3
VENV_DIR=venv

default: test-all
.PHONY: default

clean:
	$(PYTHON) setup.py clean
	rm -rf build dist tmp venv
.PHONY: clean

install:
	$(PIP) install --user .
.PHONY: install

uninstall:
	$(PIP) uninstall sclrbh
.PHONY: uninstall

# It takes about 7 mins.
test-all: venv-install-dev venv-test tox venv-integration-test
.PHONY: test-all

venv-install: venv-uninstall
	virtualenv --python="$(PYTHON)" "`pwd`/$(VENV_DIR)"; \
	source $(VENV_DIR)/bin/activate; \
	pip install .; \
	deactivate
.PHONY: venv-install

venv-install-dev: venv-uninstall
	virtualenv --python="$(PYTHON)" "`pwd`/$(VENV_DIR)"; \
	source $(VENV_DIR)/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r test-requirements.txt; \
	pip install --editable .; \
	deactivate
.PHONY: venv-install-dev

venv-uninstall:
	rm -rf "`pwd`/$(VENV_DIR)"
.PHONY: venv-uninstall

venv-list:
	source $(VENV_DIR)/bin/activate; \
	pip list; \
	deactivate
.PHONY: venv-list

venv-test:
	source $(VENV_DIR)/bin/activate; \
	$(PYTHON) -m pytest tests; \
	deactivate
.PHONY: venv-test

venv-integration-test:
	source $(VENV_DIR)/bin/activate; \
	tests/integration/run.sh; \
	deactivate
.PHONY: venv-test-integration

tox:
	tox
.PHONY: tox
