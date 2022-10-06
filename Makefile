SHELL := /bin/bash
VERSION := 0.14.11

##==================================================================================================
##@ Helper

help: ## Display help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: \033[36m\033[0m\n"} /^[a-zA-Z\.\%-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
.PHONY: help

##==================================================================================================
##@ Repo initialization

repo-pre-commit: ## Install pre-commit
	pre-commit install
	pre-commit install -t commit-msg
.PHONY: repo-pre-commit

repo-deps: ## Install dependencies
	poetry install
.PHONY: repo-deps

repo-env: ## Configure environment variables
	cat .test.env  > .env
	echo "dotenv" > .envrc
.PHONY: repo-env

repo-init: repo-pre-commit repo-deps repo-env ## Initialize repository by executing above commands
.PHONY: repo-init

##==================================================================================================
##@ AWS

.ONESHELL:
aws-instance-connect: ## Connect to EC2 (e.g. make aws-instance-connect INSTANCE_USER_NAME=ubuntu)
	public_ip=$(shell cd terraform && terraform output -raw instance_public_ip)
	user_name=${INSTANCE_USER_NAME}
	ssh -i terraform/ssh/deep-learning-for-audio.pem $$user_name@$$public_ip
.PHONY: aws-instance-connect

aws-datasets-pull: ## Pull some datasets from S3 bucket
	poetry run dvc pull
.PHONY: aws-datasets-pull

##==================================================================================================
##@ Docker

docker-build: ## Build container
	docker build -t deep-learning-for-audio .
.PHONY: docker-build

docker-run: ## Run container
	docker run -dte WANDB_API_KEY=${WANDB_API_KEY} deep-learning-for-audio
.PHONY: docker-run

##==================================================================================================
##@ Datasets

datasets-rights: ## Grant execution rights to scripts/datasets.sh
	chmod +x ./scripts/datasets.sh
.PHONY: datasets-rights

datasets-lj: datasets-rights ## Download LJSpeech dataset
	sh ./scripts/datasets.sh download_lj_speech \
		resources/datasets/asr \
		https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2
.PHONY: datasets-lj

.ONESHELL:
datasets-libri.%: datasets-rights  ## Download specified LibriSpeech dataset (e.g. make datasets-libri.dev-clean)
	dataset=$(shell echo $@ | awk -F. '{print $$2}')
	sh ./scripts/datasets.sh download_libri_speech \
		resources/datasets/asr \
		$$dataset
.PHONY: datasets-libri.%

.ONESHELL:
datasets-libri.all: datasets-rights  ## Download all LibriSpeech datasets
	for dataset in dev-clean \
				   dev-other \
				   test-clean \
				   test-other \
				   train-clean-100 \
				   train-clean-360 \
				   train-other-500
	do
		sh ./scripts/datasets.sh download_libri_speech \
			resources/datasets/asr \
			$$dataset
	done
.PHONY: datasets-libri.all

##==================================================================================================
##@ Research

jupyter: ## Run jupyter lab
	poetry run jupyter lab
.PHONY:	jupyter

##==================================================================================================
##@ Checks

mypy: ## Run type checker
	poetry run mypy
.PHONY:	mypy

##==================================================================================================
##@ Secrets

create-detect-secrets-baseline:  ## Create .secrets.baseline file
	poetry run detect-secrets scan > .secrets.baseline
.PHONY: create-detect-secrets-baseline

##==================================================================================================
##@ Cleaning

clean-logs: ## Delete log files
	rm -rf logs/* wandb/*
.PHONY: clean-logs

clean-general: ## Delete general files
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	find . | grep -E ".trash" | xargs rm -rf
	rm -f .coverage
.PHONY: clean-general

clean-all: clean-logs clean-general ## Delete all "junk" files
.PHONY: clean-all

##==================================================================================================
##@ Miscellaneous
update-pre-commit-hooks:
	pre-commit autoupdate
