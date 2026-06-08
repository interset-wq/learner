.PHONY: help install migrate dev build seed superuser clean docker-build docker-up docker-down test

PYTHON = uv run python
PNPM = pnpm

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	uv sync
	$(PNPM) install

migrate: ## Run database migrations
	$(PYTHON) manage.py migrate

dev: ## Start development servers (Tailwind watch + Django)
	$(PNPM) dev &
	$(PYTHON) manage.py runserver

build: ## Build Tailwind CSS for production
	$(PNPM) build

seed: ## Generate fake data (admin/admin123, librarian1/staff123)
	$(PYTHON) create_fake_data.py

superuser: ## Create a superuser
	$(PYTHON) manage.py createsuperuser

setup: install migrate seed build ## Full setup: install, migrate, seed, build

run: ## Run Django development server
	$(PYTHON) manage.py runserver

shell: ## Open Django shell
	$(PYTHON) manage.py shell

check: ## Run Django system checks
	$(PYTHON) manage.py check

test: ## Run all tests
	$(PYTHON) manage.py test

lint: ## Run pre-commit on all files
	uv run pre-commit run --all-files

clean: ## Remove Python caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache node_modules

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d

docker-down: ## Stop Docker containers
	docker compose down

docker-seed: ## Seed data inside Docker container
	docker compose exec web $(PYTHON) create_fake_data.py

docker-shell: ## Open shell inside Docker container
	docker compose exec web $(PYTHON) manage.py shell

docker-logs: ## View Docker container logs
	docker compose logs -f
