VERSION := 0.0.1

.PHONY:
	repo-pre-commit
	repo-deps
	repo-local-init
	jupyter

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

jupyter:
	poetry run jupyter lab
