SHELL := /bin/bash
VERSION := 0.14.9

##@ Helper
.PHONY: help

help: ## Display help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Repo initialization
.PHONY: repo-pre-commit repo-deps repo-env repo-init

repo-pre-commit: ## Install pre-commit in the repository
	pre-commit install
	pre-commit install -t commit-msg

repo-deps: ## Install dependencies in the repository
	poetry install

repo-env: ## Configure environment variables in the repository
	cat .test.env  > .env
	echo "dotenv" > .envrc

repo-init: repo-pre-commit repo-deps repo-env-init ## Initialize the repository

##@ AWS
.PHONY: aws-instance-connect

.ONESHELL:
aws-instance-connect: ## Connect to the AWS EC2 instance (execute as e.g. make aws-instance-connect INSTANCE_USER_NAME=ubuntu)
	public_ip=$(shell cd terraform && terraform output -raw instance_public_ip)
	user_name=${INSTANCE_USER_NAME}
	ssh -i terraform/ssh/deep-learning-for-audio.pem $$user_name@$$public_ip


##@ Docker
.PHONY: docker-build docker-run

docker-build: ## Build the container
	docker build -t deep-learning-for-audio .

docker-run: ## Run the container
	docker run -dte WANDB_API_KEY=${WANDB_API_KEY} deep-learning-for-audio


##@ Datasets
.PHONY:	datasets-rights datasets-lj datasets-libri.% datasets-libri.all datasets-pull

datasets-rights: ## Give execution rights to datasets.sh
	chmod +x ./scripts/datasets.sh

datasets-lj: datasets-rights ## Download the LJSpeech dataset
	sh ./scripts/datasets.sh download_lj_speech \
		resources/datasets/asr \
		https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2

.ONESHELL:
datasets-libri.%: datasets-rights  ## Download the specific LibriSpeech dataset (e.g. datasets-libri.dev-clean)
	dataset=$(shell echo $@ | awk -F. '{print $$2}')
	sh ./scripts/datasets.sh download_libri_speech \
		resources/datasets/asr \
		$$datasets

.ONESHELL:
datasets-libri.all: datasets-rights ## Download all LibriSpeech datasets
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

datasets-pull: ## Pull data from AWS S3 bucket
	poetry run dvc pull


##@ Research
.PHONY:	jupyter

jupyter: ## Run jupyter lab
	poetry run jupyter lab


##@ Checks
.PHONY:	mypy

mypy: ## Run type checker
	poetry run mypy


##@ Cleaning
.PHONY: clean-logs clean-general clean-all

clean-logs: ## Delete log files
	rm logs/* wandb/*

clean-general: ## Delete general files
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	find . | grep -E ".trash" | xargs rm -rf
	rm -f .coverage

clean-all: clean_logs clean_general ## Delete all "junk" files
