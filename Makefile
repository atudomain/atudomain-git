all: info clean test docs dist upload release
.PHONY: all docs upload info dist

PACKAGE_NAME := $(shell python3 setup.py --name)
PACKAGE_VERSION := $(shell python3 setup.py --version)
PYTHON_PATH := $(shell which python3)
PLATFORM := $(shell uname -s | awk '{print tolower($$0)}')
ifeq ($(PLATFORM), darwin)
	DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
else
	DIR := $(shell dirname $(realpath $(MAKEFILE_LIST)))
endif
PYTHON_VERSION := $(shell python3 -c "import sys; print('py%s%s' % sys.version_info[0:2] + ('-conda' if 'conda' in sys.version or 'Continuum' in sys.version else ''))")
ifneq (,$(findstring conda, $(PYTHON_VERSION)))
	CONDA := $(CONDA_DEFAULT_ENV)
endif

PREFIX :=
ifndef GIT_BRANCH
GIT_BRANCH=$(shell git branch | sed -n '/\* /s///p')
endif

info:
	@echo "INFO:	Building $(PACKAGE_NAME):$(PACKAGE_VERSION) on $(GIT_BRANCH) branch"
	@echo "INFO:	Python $(PYTHON_VERSION) from '$(PREFIX)' [$(CONDA)]"

clean:
	@find . -name "*.pyc" -delete
	@rm -rf dist docs/build build atudomain_git.egg-info .eggs .pytest_cache

package:
	python3 setup.py sdist bdist_wheel build_sphinx

install:
	$(PREFIX)python3 -m pip install .

uninstall:
	$(PREFIX)python3 -m pip uninstall -y $(PACKAGE_NAME)

dist:
	$(PREFIX)python3 setup.py sdist bdist_wheel

test:
	@echo "INFO:	test"
	pytest

docs:
	@echo "INFO:	Building the docs"
	$(PREFIX)python3 setup.py build_sphinx

release-patch:
	bumpversion patch
	git push origin master --follow-tags

release-minor:
	bumpversion minor
	git push origin master --follow-tags

release-major:
	bumpversion major
	git push origin master --follow-tags

upload:
	rm -f dist/*
ifeq ($(GIT_BRANCH),master)
	@echo "INFO:	Upload package to pypi.python.org"
	$(PREFIX)python3 setup.py sdist bdist_wheel
	$(PREFIX)twine upload dist/*
else
	@echo "INFO:	Not on master branch."
endif
