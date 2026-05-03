# Makefile for Portfolio System Architect
# Provides common development commands

.PHONY: help install dev test lint format clean docker-up docker-down docker-build docker-logs update-badge

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies (create virtual environment if missing)"
	@echo "  make dev            Start development environment (Docker Compose)"
	@echo "  make test           Run unit and integration tests with coverage"
	@echo "  make lint           Run linters (ruff, black, mypy)"
	@echo "  make format         Format code with black and isort"
	@echo "  make clean          Remove temporary files and caches"
	@echo "  make docker-up      Start all services with Docker Compose"
	@echo "  make docker-down    Stop all services"
	@echo "  make docker-build   Build Docker images"
	@echo "  make docker-logs    Follow logs from all services"
	@echo "  make pre-commit     Run pre-commit hooks on all files"
	@echo "  make update-badge   Update coverage badge in README (auto-runs tests)"

# Detect Python and virtual environment
PYTHON ?= python3
VENV ?= .venv
VENV_BIN = $(VENV)/bin
VENV_ACTIVATE = . $(VENV_BIN)/activate

# Check if virtual environment exists
VENV_EXISTS := $(shell test -d $(VENV) && echo yes)

install:
ifeq ($(VENV_EXISTS),yes)
	@echo "Virtual environment already exists."
else
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
endif
	@echo "Installing dependencies..."
	$(VENV_ACTIVATE) && pip install --upgrade pip
	$(VENV_ACTIVATE) && pip install -r requirements-dev.txt
	$(VENV_ACTIVATE) && pip install -e .
	@echo "Installing pre-commit hooks..."
	$(VENV_ACTIVATE) && pre-commit install

dev: docker-up
	@echo "Development environment started. Access services:"
	@echo "  - Traefik Dashboard: http://localhost:8080"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

test:
	$(VENV_ACTIVATE) && python -m pytest --cov=apps --cov=src --cov-report=html --cov-report=term-missing -m "not slow"

lint:
	$(VENV_ACTIVATE) && ruff check .
	$(VENV_ACTIVATE) && black --check .
	$(VENV_ACTIVATE) && mypy apps src

format:
	$(VENV_ACTIVATE) && black .
	$(VENV_ACTIVATE) && isort .

clean:
	rm -rf .pytest_cache .coverage coverage_html .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

docker-up:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

docker-down:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down

docker-build:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml build

docker-logs:
	docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml logs -f

pre-commit:
	$(VENV_ACTIVATE) && pre-commit run --all-files

# Additional targets for CI/CD
ci: lint test
	@echo "CI pipeline passed"

# Generate documentation locally
docs:
	$(VENV_ACTIVATE) && mkdocs serve

# Update coverage badge in README
update-badge:
	@echo "Updating coverage badge..."
	@python scripts/update-coverage-badge.py
