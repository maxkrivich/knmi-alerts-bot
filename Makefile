.PHONY: help

help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Start up the project
	brew install hadolint
	pip install pre-commit poetry ruff
	poetry install
	pre-commit install

lint: ## Run linting
	ruff check

format: ## Run formatting
	ruff check --fix
	ruff format

check-format: ## Check formatting
	ruff format --check

check-mypy: ## Check mypy
	poetry run mypy .

git-hooks: ## Check git hooks
	pre-commit run --all-files

up: ## Start up the project
	docker compose up --build

clean: ## Clean up generated files
	rm -rf docs
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
