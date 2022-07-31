#@ Repository initialization
.PHONY: repo-pre-commit repo-deps repo-local-init

# Install pre-commit in repository
repo-pre-commit:
	pre-commit install -t pre-commit -t commit-msg

# Install dependencies in repository
repo-deps:
	poetry install --extras "dev research"

# Configure environment variables in repository
repo-local-init:
	cat .test.env  > .env
