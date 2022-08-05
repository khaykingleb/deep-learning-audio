VERSION := 0.0.0

#@ Repository initialization
.PHONY:
	repo-pre-commit
	repo-deps
	repo-local-init

# Install pre-commit in repository
repo-pre-commit:
	pre-commit install
	pre-commit install -t commit-msg

# Install dependencies in repository
repo-deps:
	poetry install

# Configure environment variables in repository
repo-local-init:
	cat .test.env  > .env
