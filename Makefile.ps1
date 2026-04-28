# =============================================================================
# MAKEFILE ДЛЯ WINDOWS POWERSHELL
# =============================================================================
# Использование: make <target>
# Или: .\make.ps1 <target>
# =============================================================================

.PHONY: help install dev test lint format clean docker-up docker-down docker-build

# === Основные ===
help:
    @Write-Host "📚 Доступные команды:" -ForegroundColor Cyan
    @Write-Host "  make install     - Установить зависимости"
    @Write-Host "  make dev         - Запустить в режиме разработки"
    @Write-Host "  make test        - Запустить тесты"
    @Write-Host "  make lint        - Проверка кода"
    @Write-Host "  make format      - Форматирование кода"
    @Write-Host "  make clean       - Очистка кэша"
    @Write-Host "  make docker-up   - Запустить Docker сервисы"
    @Write-Host "  make docker-down - Остановить Docker сервисы"
    @Write-Host "  make docker-build- Сборка Docker образов"

install:
    @Write-Host "📦 Установка зависимостей..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m pip install pre-commit
    pre-commit install

dev:
    @Write-Host "🚀 Запуск в режиме разработки..." -ForegroundColor Green
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
    @Write-Host "🧪 Запуск тестов..." -ForegroundColor Yellow
    python -m pytest tests/ -v --tb=short --cov=. --cov-report=html

test-fast:
    @Write-Host "⚡ Быстрые тесты (без покрытия)..." -ForegroundColor Yellow
    python -m pytest tests/ -v --tb=short -x

lint:
    @Write-Host "🔍 Линтинг кода..." -ForegroundColor Yellow
    python -m ruff check .
    python -m bandit -r src/ -ll

format:
    @Write-Host "🎨 Форматирование кода..." -ForegroundColor Yellow
    python -m black .
    python -m isort .

format-check:
    @Write-Host "👀 Проверка форматирования..." -ForegroundColor Yellow
    python -m black --check .
    python -m isort --check-only .

clean:
    @Write-Host "🧹 Очистка кэша..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force .coverage -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force htmlcov -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force .ruff_cache -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force .mypy_cache -ErrorAction SilentlyContinue
    Write-Host "✅ Очистка завершена" -ForegroundColor Green

# === Docker ===
docker-up:
    @Write-Host "🐳 Запуск Docker сервисов..." -ForegroundColor Green
    docker-compose up -d

docker-down:
    @Write-Host "🛑 Остановка Docker сервисов..." -ForegroundColor Yellow
    docker-compose down

docker-build:
    @Write-Host "🏗️ Сборка Docker образов..." -ForegroundColor Yellow
    docker-compose build

docker-logs:
    @Write-Host "📋 Логи Docker..." -ForegroundColor Cyan
    docker-compose logs -f

# === Безопасность ===
security-audit:
    @Write-Host "🔒 Аудит безопасности..." -ForegroundColor Yellow
    python -m pip audit
    python -m bandit -r src/ -ll

secrets-scan:
    @Write-Host "🔍 Поиск секретов в Git..." -ForegroundColor Yellow
    git log --all --full-history -p | Select-String -Pattern "(api[_-]?key|password|secret|token).*[=:].*" -CaseSensitive:$false

# === Документация ===
docs:
    @Write-Host "📝 Генерация документации..." -ForegroundColor Yellow
    python -m pdoc -o docs/api ./src

# === Микросервисы ===
services-list:
    @Write-Host "📋 Список микросервисов:" -ForegroundColor Cyan
    @Get-ChildItem apps -Directory | ForEach-Object { Write-Host "  • $($_.Name)" }

service-up:
    @param($(SERVICE))
    @Write-Host "🚀 Запуск сервиса: $SERVICE..." -ForegroundColor Green
    docker-compose up -d $SERVICE

service-down:
    @param($(SERVICE))
    @Write-Host "🛑 Остановка сервиса: $SERVICE..." -ForegroundColor Yellow
    docker-compose down $SERVICE

# === База данных ===
db-migrate:
    @Write-Host "🔄 Миграция БД..." -ForegroundColor Yellow
    python -m alembic upgrade head

db-migrate-make:
    @param($(MESSAGE))
    @Write-Host "📝 Создание миграции: $MESSAGE..." -ForegroundColor Yellow
    python -m alembic revision --autogenerate -m "$MESSAGE"

db-reset:
    @Write-Host "⚠️ СБРОС БАЗЫ ДАННЫХ!" -ForegroundColor Red
    python -m alembic downgrade base
    python -m alembic upgrade head
