PROJECT_NAME := $(shell python setup.py --name)
PROJECT_VERSION := $(shell python setup.py --version)

BOLD := \033[1m
RESET := \033[0m

default: help

.PHONY : help
help:  ## Show this help
	@echo "$(BOLD)Isshub Makefile$(RESET)"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -h ':\s\+##' Makefile | column -tn -s# | awk -F ":" '{ print "  $(BOLD)" $$1 "$(RESET)" $$2 }'

.PHONY: install
install:  ## Install the project in the current environment, with its dependencies
	@echo "$(BOLD)Installing $(PROJECT_NAME) $(PROJECT_VERSION)$(RESET)"
	@pip install .

.PHONY: dev
dev:  ## Install the project in the current environment, with its dependencies, including the ones needed in a development environment
	@echo "$(BOLD)Installing $(PROJECT_NAME) $(PROJECT_VERSION) in dev mode$(RESET)"
	@pip install -e .[dev,tests,lint,docs]
	@$(MAKE) full-clean

.PHONY: dev-upgrade
dev-upgrade:  ## Upgrade all default+dev dependencies defined in setup.cfg
	@pip install --upgrade pip
	@pip install --upgrade `python -c 'import setuptools; o = setuptools.config.read_configuration("setup.cfg")["options"]; print(" ".join(o["install_requires"] + o["extras_require"]["dev"] + o["extras_require"]["tests"] + o["extras_require"]["lint"] + o["extras_require"]["docs"]))'`
	@pip install -e .
	@$(MAKE) full-clean

.PHONY: dist
dist:  ## Build the package
dist: clean
	@echo "$(BOLD)Building package$(RESET)"
	@python setup.py sdist bdist_wheel

.PHONY: clean
clean:  ## Clean python build related directories and files
	@echo "$(BOLD)Cleaning$(RESET)"
	@rm -rf build dist $(PROJECT_NAME).egg-info

.PHONY: full-clean
full-clean:  ## Like "clean" but with clean-doc and will clean some other generated directories or files
full-clean: clean
	@echo "$(BOLD)Full cleaning$(RESET)"
	find ./ -type d  \( -name '__pycache__' -or -name '.pytest_cache' -or -name '.mypy_cache'  \) -print0 | xargs -tr0 rm -r
	-$(MAKE) clean-doc

.PHONY: doc docs
doc / docs: ## Build the documentation
docs: doc  # we allow "doc" and "docs"
doc:  clean-doc
	@echo "$(BOLD)Building documentation$(RESET)"
	@cd docs && $(MAKE) html

.PHONY: doc-strict docs-strict
doc-strict / docs-strict:  ## Build the documentation but fail if a warning
docs-strict: doc-strict  # we allow "doc-strict" and "docs-strict"
doc-strict:  clean-doc
	@echo "$(BOLD)Building documentation (strict)$(RESET)"
	@cd docs && sphinx-build -W -b html . _build

.PHONY: clean-doc clean-docs
clean-doc / clean-docs:  ## Clean the documentation directories
clean-docs: clean-doc  # we allow "clean-doc" and "clean-docs"
clean-doc:
	@echo "$(BOLD)Cleaning documentation directories$(RESET)"
	@rm -rf docs/source docs/git
	@cd docs && $(MAKE) clean

.PHONY: tests test
test / tests:  ## Run tests for the isshub project.
test: tests  # we allow "test" and "tests"
tests:
	@echo "$(BOLD)Running tests$(RESET)"
	@## we ignore error 5 from pytest meaning there is no test to run
	@pytest || ( ERR=$$?; if [ $${ERR} -eq 5 ]; then (exit 0); else (exit $${ERR}); fi )

.PHONY: tests-nocov
test-nocov / tests-nocov:  ## Run tests for the isshub project without coverage.
test-nocov: tests-nocov  # we allow "test-nocov" and "tests-nocov"
tests-nocov:
	@echo "$(BOLD)Running tests (without coverage)$(RESET)"
	@## we ignore error 5 from pytest meaning there is no test to run
	@pytest --no-cov || ( ERR=$$?; if [ $${ERR} -eq 5 ]; then (exit 0); else (exit $${ERR}); fi )

.PHONY: lint
lint:  ## Run all linters (check-isort, check-black, mypy, flake8, pylint)
lint: check-isort check-black flake8 pylint mypy

.PHONY: check checks
check / checks:  ## Run all checkers (lint, tests)
check: checks
checks: lint tests check-commit

.PHONY: mypy
mypy:  ## Run the mypy tool
	@echo "$(BOLD)Running mypy$(RESET)"
	@mypy .

.PHONY: check-isort
check-isort:  ## Run the isort tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking isort(RESET)"
	@isort --check-only 2>&1

.PHONY: check-black
check-black:  ## Run the black tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking black$(RESET)"
	@black --target-version py38 --check  . 2>&1

.PHONY: flake8
flake8:  ## Run the flake8 tool
	@echo "$(BOLD)Running flake8$(RESET)"
	@flake8 --format=abspath

.PHONY: pylint
pylint:  ## Run the pylint tool
	@echo "$(BOLD)Running pylint$(RESET)"
	@pylint isshub

.PHONY: pretty
pretty:  ## Run all code beautifiers (isort, black)
pretty: isort black

.PHONY: isort
isort:  ## Run the isort tool and update files that need to
	@echo "$(BOLD)Running isort$(RESET)"
	@isort --atomic --apply

.PHONY: black
black:  ## Run the black tool and update files that need to
	@echo "$(BOLD)Running black$(RESET)"
	@black --target-version py38 .

.PHONY: check-commit
check-commit: ## Check the validaity of the last commit message
	@echo "$(BOLD)Checking last commit message$(RESET)"
	@ci/check_commit_message.py -vl
