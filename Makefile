VERSION := 0.5.0

.PHONY:
	repo-pre-commit
	repo-deps
	repo-env-init
	repo-init
	jupyter
	mypy

# Install pre-commit in repository
repo-pre-commit:
	pre-commit install
	pre-commit install -t commit-msg

# Install dependencies in repository
repo-deps:
	poetry install

# Configure environment variables in repository
repo-env-init:
	cat .test.env  > .env

# Initialize repository
repo-init:
	repo-pre-commit repo-deps repo-env-init

# Run jupyter lab
jupyter:
	poetry run jupyter lab

# Run mypy type checker
mypy:
	poetry run mypy
