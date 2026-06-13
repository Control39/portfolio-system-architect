# Makefile for Portfolio System Architect
# Кроссплатформенный (Windows/Linux/Mac)
# Все настройки в pyproject.toml — единый источник истины

.ONESHELL:

.PHONY: help install dev prod monitoring test lint format clean \
        docker-up docker-down docker-build docker-logs \
        update-badge check-ports audit security pre-commit \
        reinstall status clean-cache

# Default target
help:
	@echo "🏗️  Portfolio System Architect — доступные команды:"
	@echo ""
	@echo "📦 Установка:"
	@echo "  make install        Установить зависимости + pre-commit hooks"
	@echo ""
	@echo "🚀 Запуск:"
	@echo "  make dev            Dev-режим (Docker Compose)"
	@echo "  make monitoring     Dev + мониторинг (Prometheus/Grafana/Jaeger)"
	@echo "  make prod           Prod-режим (с secrets)"
	@echo ""
	@echo "🧪 Тестирование и качество:"
	@echo "  make test           Запустить тесты с coverage"
	@echo "  make lint           Запустить линтеры (ruff, mypy)"
	@echo "  make format         Отформатировать код (ruff)"
	@echo "  make audit          Аудит мёртвых атомов"
	@echo "  make security       Аудит безопасности (pip-audit + bandit)"
	@echo "  make pre-commit     Запустить все pre-commit хуки"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up      Запустить все сервисы"
	@echo "  make docker-down    Остановить все сервисы"
	@echo "  make docker-build   Собрать Docker-образы"
	@echo "  make docker-logs    Смотреть логи"
	@echo "  make check-ports    Проверить конфликты портов"
	@echo ""
	@echo "🧹 Очистка:"
	@echo "  make clean          Удалить временные файлы и кэши"
	@echo "  make clean-cache    Удалить только __pycache__ и .pytest_cache"
	@echo ""
	@echo "🔄 Полезные команды:"
	@echo "  make reinstall      Полная переустановка (удалить venv + установить заново)"
	@echo "  make status         Проверить статус сервисов и портов"

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

PYTHON ?= python
VENV ?= .venv
PYPROJECT := pyproject.toml

# Кроссплатформенная проверка существования venv
ifeq ($(OS),Windows_NT)
    VENV_PYTHON := $(VENV)/Scripts/python.exe
    VENV_PIP := $(VENV)/Scripts/pip.exe
    VENV_RUFF := $(VENV)/Scripts/ruff.exe
    VENV_MYPY := $(VENV)/Scripts/mypy.exe
    VENV_PRE_COMMIT := $(VENV)/Scripts/pre-commit.exe
    RM_RF := powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    VENV_EXISTS := $(shell if exist $(VENV)\Scripts\python.exe (echo yes) else (echo no))
else
    VENV_PYTHON := $(VENV)/bin/python
    VENV_PIP := $(VENV)/bin/pip
    VENV_RUFF := $(VENV)/bin/ruff
    VENV_MYPY := $(VENV)/bin/mypy
    VENV_PRE_COMMIT := $(VENV)/bin/pre-commit
    RM_RF := rm -rf
    VENV_EXISTS := $(shell test -d $(VENV) && echo yes || echo no)
endif

# =============================================================================
# УСТАНОВКА
# =============================================================================

install:
ifeq ($(VENV_EXISTS),no)
	@echo "🔧 Создаю виртуальное окружение..."
	$(PYTHON) -m venv $(VENV)
endif
	@echo "📦 Устанавливаю зависимости..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -e ".[all]"
	$(VENV_PRE_COMMIT) install
	@echo "✅ Установка завершена"

# =============================================================================
# ЗАПУСК ОКРУЖЕНИЯ
# =============================================================================

dev:
	@echo "🚀 Запуск dev-окружения..."
	docker compose up -d
	@echo ""
	@echo "📊 Сервисы доступны:"
	@echo "  • Traefik Dashboard: http://localhost:8080"
	@echo "  • Auth Service:      http://localhost/auth"
	@echo "  • IT-Compass:        http://localhost/it-compass"
	@echo ""
	@echo "💡 Для мониторинга: make monitoring"

monitoring:
	@echo "🚀 Запуск dev + мониторинг..."
	docker compose -f docker-compose.yml -f docker/docker-compose.monitoring.yml up -d
	@echo ""
	@echo "📊 Мониторинг:"
	@echo "  • Grafana:     http://localhost:3000 (admin/admin)"
	@echo "  • Prometheus:  http://localhost:9090"
	@echo "  • Jaeger UI:   http://localhost:16686"
	@echo "  • AlertManager: http://localhost:9093"

prod:
	@echo "🚀 Запуск prod-окружения..."
	@if [ ! -d "secrets" ]; then \
		echo "⚠️  Папка secrets/ не найдена. Создаю..."; \
		mkdir -p secrets; \
		echo "⚠️  Добавь секреты в secrets/*.txt"; \
		exit 1; \
	fi
	docker compose -f docker-compose.prod.yml up -d
	@echo "✅ Prod-окружение запущено"

# =============================================================================
# ТЕСТИРОВАНИЕ И КАЧЕСТВО
# =============================================================================

test:
	@echo "🧪 Запуск тестов..."
	$(VENV_PYTHON) -m pytest
	@echo "✅ Тесты завершены"

lint:
	@echo "🔍 Запуск линтеров..."
	$(VENV_RUFF) check .
	$(VENV_RUFF) format --check .
	$(VENV_MYPY) apps src agents tools
	@echo "✅ Линтинг завершён"

format:
	@echo "🎨 Форматирование кода..."
	$(VENV_RUFF) check --fix .
	$(VENV_RUFF) format .
	@echo "✅ Форматирование завершено"

audit:
	@echo "🔍 Аудит мёртвых атомов..."
	$(VENV_PYTHON) scripts/audit_dead_atoms.py
	@echo ""
	@echo "🔍 Проверка архитектурных границ..."
	$(VENV_PYTHON) scripts/check_src_boundary.py

security:
	@echo "🔒 Аудит безопасности..."
	$(VENV_PIP) install -q pip-audit bandit
	$(VENV_PYTHON) -m pip_audit || echo "⚠️  Найдены уязвимости"
	$(VENV_PYTHON) -m bandit -r apps/ src/ agents/ tools/ -lll -f json -o bandit-report.json || echo "⚠️  Bandit нашёл проблемы"
	@echo "✅ Аудит безопасности завершён"

pre-commit:
	@echo "🪝 Запуск pre-commit хуков..."
	$(VENV_PRE_COMMIT) run --all-files

# =============================================================================
# DOCKER
# =============================================================================

docker-up:
	@echo "🚀 Запуск всех сервисов..."
	docker compose up -d

docker-down:
	@echo "🛑 Остановка всех сервисов..."
	docker compose down

docker-build:
	@echo "🔨 Сборка Docker-образов..."
	docker compose build

docker-logs:
	@echo "📋 Логи сервисов..."
	docker compose logs -f

check-ports:
	@echo "🔍 Проверка конфликтов портов..."
	$(VENV_PYTHON) scripts/check_ports.py

# =============================================================================
# ОЧИСТКА
# =============================================================================

clean:
	@echo "🧹 Очистка временных файлов..."
ifeq ($(OS),Windows_NT)
	powershell -Command "Get-ChildItem -Path . -Include __pycache__,.pytest_cache,.mypy_cache,.ruff_cache -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Path . -Include *.pyc,*.pyo -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue"
	powershell -Command "Remove-Item -Path .coverage,coverage.xml,htmlcov,bandit-report.json -Recurse -Force -ErrorAction SilentlyContinue"
else
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" \) -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	rm -rf .coverage coverage.xml htmlcov/ bandit-report.json 2>/dev/null || true
endif
	@echo "✅ Очистка завершена"

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ЦЕЛИ
# =============================================================================

# 🔄 Полная переустановка
reinstall:
	@echo "🔄 Полная переустановка..."
	$(RM_RF) $(VENV)
	$(MAKE) install

# 📊 Статус сервисов
status:
	@echo "🔍 Статус контейнеров:"
	-docker compose ps
	@echo ""
	@echo "🔍 Статус портов:"
	-$(VENV_PYTHON) scripts/check_ports.py

# 🧹 Лёгкая очистка (без venv)
clean-cache:
ifeq ($(OS),Windows_NT)
	powershell -Command "Get-ChildItem -Path . -Include __pycache__,.pytest_cache -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
else
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" \) -exec rm -rf {} + 2>/dev/null || true
endif
	@echo "✅ Кэш очищен"
