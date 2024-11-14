SHELL := /bin/bash
.DEFAULT_GOAL = help

VERSION := 0.14.11

# export VERSION := $(shell grep -m 1 version pyproject.toml | grep -e '\d.\d.\d' -o)

# Load environment variables from .env
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

##=============================================================================
##@ Repo Initialization
##=============================================================================

PLUGINS := \
	opentofu https://github.com/defenseunicorns/asdf-opentofu.git \
	python https://github.com/asdf-community/asdf-python.git \
	pre-commit https://github.com/jonathanmorley/asdf-pre-commit.git \
	poetry https://github.com/asdf-community/asdf-poetry.git \
	uv https://github.com/b1-luettje/asdf-uv.git \
	direnv https://github.com/asdf-community/asdf-direnv.git

prerequisites: ## Install prerequisite tools
	@echo "Checking and installing required plugins."
	@echo "$(PLUGINS)" | tr ' ' '\n' | paste - - | while read -r plugin url; do \
		if asdf plugin-list | grep -q $$plugin; then \
			echo "Plugin '$$plugin' is already installed."; \
		else \
			echo "Adding plugin '$$plugin'."; \
			asdf plugin-add $$plugin $$url; \
		fi; \
	done
	@echo  "Installing specified versions."
	asdf install
	@echo  "Currently installed versions:"
	asdf current
.PHONY: prerequisites

pre-commit: ## Install pre-commit hooks
	@echo "Installing pre-commit hooks."
	pre-commit install -t pre-commit -t commit-msg
.PHONY: pre-commit

deps: ## Install dependencies
	@echo "Installing dependencies."
	poetry install --no-cache
.PHONY: deps

init: prerequisites pre-commit ## Initialize repository for development in Docker
.PHONY: init

init-local: prerequisites pre-commit deps ## Initialize repository for development outside of Docker
.PHONY: init-local

##=============================================================================
##@ Macros
##=============================================================================

run: ## Run Docker container
	docker compose -f docker-compose.yaml up --build
.PHONY: run

test: ## Run tests
	poetry run pytest
.PHONY: test

##=============================================================================
##@ Miscellaneous
##=============================================================================

create-secrets-baseline:  ## Create secrets baseline file
	poetry run detect-secrets scan > .secrets.baseline
.PHONY: create-secrets-baseline

audit-secrets-baseline:  ## Check updated .secrets.baseline file
	poetry run detect-secrets audit .secrets.baseline
	git commit .secrets.baseline --no-verify -m "build(security): update secrets.baseline"
.PHONY: audit-secrets-baseline

update-pre-commit-hooks:  ## Update pre-commit hooks
	pre-commit autoupdate
.PHONY: update-pre-commit-hooks

clean: ## Clean up
	find logs/ -type f ! -name '.gitkeep' -delete
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache .ruff_cache .coverage.*
.PHONY: clean

##=============================================================================
##@ Helper
##=============================================================================

help:  ## Display help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: \033[36m\033[0m\n"} /^[a-zA-Z\.\%-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
.PHONY: help
