#@ Variables
SHELL := /usr/bin/env bash
VERSION := 0.11.5

#@ Repo initialization
.PHONY: repo-pre-commit repo-deps repo-env repo-init

 # Install pre-commit in repository
repo-pre-commit:
	pre-commit install
	pre-commit install -t commit-msg

# Install dependencies in repository
repo-deps:
	poetry install

# Configure environment variables in repository
repo-env:
	cat .test.env  > .env
	echo "dotenv" > .envrc

# Initialize repository
repo-init: repo-pre-commit repo-deps repo-env-init

#@ Research
.PHONY:	jupyter

# Run jupyter lab
jupyter:
	poetry run jupyter lab

#@ Checks
.PHONY:	mypy

# Run type checker
mypy:
	poetry run mypy

#@ Datasets
.PHONY:	get_lj_speech get_all_datasets

# Download LJ Speech for ASR
get_lj_speech:
	chmod +x ./scripts/datasets.sh
	sh ./scripts/datasets.sh get_lj_speech_dataset \
		resources/datasets/asr https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2

get_all_libri_speech:
	chmod +x ./scripts/datasets.sh
	for dataset in dev-clean dev-other test-clean test-other train-clean-100 train-clean-360 train-other-500; \
	do \
		sh ./scripts/datasets.sh get_libri_speech_dataset resources/datasets/asr $$dataset; \
	done

# Download all datasets
get_all_datasets: get_lj_speech get_all_libri_speech

#@ Cleaning
.PHONY: clean_logs clean_all

# Delete all log files
clean_logs:
	rm logs/*

# Delete all "junk" files
clean_all: clean_logs
