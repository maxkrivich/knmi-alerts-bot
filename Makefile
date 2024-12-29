.PHONY: help

help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Start up the project
	pip install pre-commit poetry ruff
	poetry install
	pre-commit install

lint: ## Run linting
	ruff check

format: ## Run formatting
	ruff format

check-format: ## Check formatting
	ruff format --check

check-mypy: ## Check mypy
	poetry run mypy .

git-hooks: ## Check git hooks
	pre-commit run --all-files

up: ## Start up the project
	docker compose up -d
