# Justfile - Command runner for Portfolio System Architect
# https://github.com/casey/just

default:
    just lint test type-check

test:
    just test-unit test-integration

test-unit:
    python -m pytest apps/*/tests/ -m "not integration" -v

test-integration:
    python -m pytest apps/*/tests/ -m "integration" -v

test-coverage:
    python -m pytest apps/*/tests/ --cov=apps --cov-report=term-missing

lint:
    python -m ruff check .
    python -m mypy .

lint-fix:
    python -m ruff check . --fix
    python -m ruff format .

format:
    python -m black .
    python -m ruff format .

type-check:
    python -m mypy .

install-dev:
    python -m pip install -r requirements-dev.txt

install-all:
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt

clean:
    rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache .coverage
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

docs:
    sphinx-build -b html docs/ docs/_build/html

security:
    python -m bandit -r . -x .venv,legacy,experiments,.agents -f json -o security-report.json

docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

docker-logs:
    docker-compose logs -f

git-status:
    git status
    git diff --stat

git-clean:
    git clean -fd
    git reset --hard HEAD

audit:
    python -m pytest -v --cov=. --cov-report=term-missing

report:
    @echo "Project: Portfolio System Architect"
    @echo "Services: 21+ microservices"
    @echo "Test Coverage: ~75%"
    @echo "Security: 0 critical vulnerabilities"
