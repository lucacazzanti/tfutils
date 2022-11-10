## boilerplate Makefile

.PHONY: clean clean-test clean-pyc clean-build docs lint

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 tfutils

test: ## run tests quickly with the default Python
	pytest

## test-all: ## run tests on every Python version with tox
##	tox

## coverage: ## check code coverage quickly with the default Python
##	coverage run --source tfutils  -m pytest
##	coverage report -m
##	coverage html

uninstall:
	pip uninstall tfutils

dev-install:  ## install the package with dev capability to the active environment's site-packages
	pip install -e .

install: ## install  the package to the active environment's site-packages
	pip install .
