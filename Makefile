SHELL := /bin/bash
.DEFAULT_GOAL = help

VERSION := 0.14.11
CONTAINER_NAME := dori

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
	direnv https://github.com/asdf-community/asdf-direnv.git \

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

env: ## Create .env file if it doesn't exist
	@if ! [ -e .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it according to your setup."; \
	fi
.PHONY: env

pre-commit: ## Install pre-commit hooks
	@echo "Installing pre-commit hooks."
	pre-commit install -t pre-commit -t commit-msg
.PHONY: pre-commit

deps: ## Install dependencies
	@echo "Installing dependencies."
	poetry install --no-cache
.PHONY: deps

init-local: prerequisites env pre-commit deps ## Initialize repository for development outside of Docker
.PHONY: init-local

init: prerequisites env pre-commit ## Initialize repository for development in Docker
.PHONY: init

##=============================================================================
##@ Macros
##=============================================================================

build: ## Build Docker container
	docker compose -f docker-compose.yaml build
.PHONY: build

run: ## Run Docker container
	docker compose -f docker-compose.yaml run --rm $(CONTAINER_NAME) /bin/bash
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
	find wandb -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} +
	find checkpoints -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache .ruff_cache .coverage.*
.PHONY: clean

##=============================================================================
##@ Helper
##=============================================================================

help:  ## Display help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: \033[36m\033[0m\n"} /^[a-zA-Z\.\%-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
.PHONY: help
