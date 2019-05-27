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
	@pip install -e .[dev,docs]
	@$(MAKE) full-clean

.PHONY: dev-upgrade
dev-upgrade:  ## Upgrade all default+dev dependencies defined in setup.cfg
	@pip install --upgrade `python -c 'import setuptools; o = setuptools.config.read_configuration("setup.cfg")["options"]; print(" ".join(o["install_requires"] + o["extras_require"]["dev"] + o["extras_require"]["docs"]))'`
	@pip install -e .
	@$(MAKE) full-clean

.PHONY: dist
dist:  ## Build the package
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
	find ./ -type d -name '__pycache__' -print0 | xargs -tr0 rm -r
	-$(MAKE) clean-doc

.PHONY: doc docs
docs: doc  # we allow "doc" and "docs"
doc:  clean-doc ## Build the documentation
	@echo "$(BOLD)Building documentation$(RESET)"
	@cd docs && $(MAKE) html

.PHONY: clean-docs
clean-docs: clean-doc  # we allow "clean-doc" and "clean-docs"
clean-doc:  ## Clean the documentation directories
	@echo "$(BOLD)Cleaning documentation directories$(RESET)"
	@rm -rf docs/source
	@cd docs && $(MAKE) clean