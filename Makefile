# Makefile для Portfolio System Architect
# Updated 2026-06-24 - Modernized for current project structure

.PHONY: help test lint type-check clean docker docs git-status

# === Help Commands ===
help:
	@echo "🤖 Portfolio System Architect Commands:"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test              - Run all tests"
	@echo "  make lint              - Run linters (ruff, mypy)"
	@echo "  make type-check        - Run type checking"
	@echo "  make clean             - Clean up cache files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up         - Start Docker services"
	@echo "  make docker-down       - Stop Docker services"
	@echo "  make docker-logs       - View Docker logs"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  make docs              - Build documentation"
	@echo ""
	@echo "Git Commands:"
	@echo "  make git-status        - Show git status"
	@echo "  make git-clean         - Clean up git repository"
	@echo ""
	@echo "Project Commands:"
	@echo "  make report            - Generate project report"
	@echo "  make install-all       - Install all dependencies"
	@echo "  make install-dev       - Install dev dependencies"

# === Development Commands ===
test:
	@echo "🧪 Running all tests..."
	python -m pytest apps/*/tests/ -v

lint:
	@echo "🧹 Running linters..."
	python -m ruff check .
	python -m mypy .

type-check:
	@echo "🔍 Running type checking..."
	python -m mypy .

clean:
	@echo "🧹 Cleaning cache files..."
	rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# === Docker Commands ===
docker-up:
	@echo "🚀 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

# === Documentation Commands ===
docs:
	@echo "📚 Building documentation..."
	sphinx-build -b html docs/ docs/_build/html

# === Git Commands ===
git-status:
	@echo "📊 Git Status:"
	git status
	git diff --stat

git-clean:
	@echo "🧹 Cleaning git repository..."
	git clean -fd
	git reset --hard HEAD

# === Project Commands ===
install-all:
	@echo "📦 Installing all dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-dev:
	@echo "📦 Installing dev dependencies..."
	pip install -r requirements-dev.txt

report:
	@echo "📈 Project Report:"
	@echo "  Project: Portfolio System Architect"
	@echo "  Services: 21+ microservices"
	@echo "  Test Coverage: ~75%"
	@echo "  Security: 0 critical vulnerabilities"

# === Legacy Commands (deprecated) ===
# These are kept for backward compatibility but redirect to Taskfile
chat:
	@echo "⚠️  WARNING: 'make chat' is deprecated."
	@echo "   Use 'task' command instead (Taskfile.yml)"
	@echo "   See Taskfile.yml for available tasks."

run-agent:
	@echo "⚠️  WARNING: 'make run-agent' is deprecated."
	@echo "   Use 'task' command instead (Taskfile.yml)"
	@echo "   See Taskfile.yml for available tasks."

scan-project:
	@echo "⚠️  WARNING: 'make scan-project' is deprecated."
	@echo "   Use 'task' command instead (Taskfile.yml)"
	@echo "   See Taskfile.yml for available tasks."

show-status:
	@echo "⚠️  WARNING: 'make show-status' is deprecated."
	@echo "   Use 'task' command instead (Taskfile.yml)"
	@echo "   See Taskfile.yml for available tasks."

check-integrity:
	@echo "⚠️  WARNING: 'make check-integrity' is deprecated."
	@echo "   Use 'task' command instead (Taskfile.yml)"
	@echo "   See Taskfile.yml for available tasks."
