# 🏗 Portfolio System Architect

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/Control39/portfolio-system-architect/ci.yml?label=CI)](https://github.com/Control39/portfolio-system-architect/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Microservices ecosystem for portfolio management and automation*

</div>

---

## ⚠️ Временные неудобства

> **Документация обновляется.** Некоторые ссылки в этом README могут быть временно неактивны в связи с рефакторингом архитектуры. Спасибо за понимание!

---

## 📋 О проекте

Платформа для автоматизации и управления портфелем на базе микросервисной архитектуры. Проект включает:

- **Cognitive Automation Agent** — автономная система автоматизации
- **IT-Compass** — методология измерения компетенций
- **14 интегрированных микросервисов** — контейнеризированные сервисы

---

## 🏗 Architecture Overview

```
  +----------------+     +---------------------+     +-------------------+
  |                |     |                     |     |                   |
  |   User (Web)   |---->|    Traefik (API    |---->|   Auth Service    |
  |                |     |    Gateway)         |     |                   |
  +----------------+     +---------------------+     +-------------------+
                                 |                            |
                                 |                            |
                                 v                            v
                    +----------------------+     +-----------------------+
                    |                      |     |                       |
                    |   IT-Compass (UI)    |     |   Decision Engine (AI) |
                    |                      |     |                       |
                    +----------------------+     +-----------------------+
                                 |                            |
                                 |                            |
                                 +------------+---------------+
                                              |
                                              v
                                 +--------------------------+
                                 |                          |
                                 |     PostgreSQL & Redis   |
                                 |      (Data Storage)      |
                                 |                          |
                                 +--------------------------+
```

*Рис. 1: Упрощенная схема взаимодействия ключевых компонентов.*

---

## 🚀 Быстрый старт

### Установка

```bash
# Создание виртуального окружения
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск окружения
docker-compose up
```

### Доступ к сервисам

| Сервис | URL | Назначение |
|--------|-----|------------|
| IT-Compass UI | http://localhost:8501 | Трекинг компетенций |
| Cloud-Reason API | http://localhost:8001/docs | AI reasoning & RAG |
| Grafana | http://localhost:3000 | Мониторинг (admin/admin) |

---

## 📦 Основные компоненты

### Когнитивный агент
- **Project Scanner** — сканирование технологического стека
- **Task Planner** — планирование задач
- **Learning System** — самообучение на основе метрик

### Микросервисы

**Основные:**
- **Cognitive Agent** — AI-автоматизация
- **Decision Engine** — система принятия решений
- **IT-Compass** — методология системного мышления
- **Knowledge Graph** — управление знаниями

**Инфраструктура:**
- **Infra Orchestrator** — управление инфраструктурой
- **Auth Service** — аутентификация
- **MCP Server** — Model Context Protocol
- **ML Model Registry** — управление ML-моделями

**Бизнес-сервисы:**
- **Portfolio Organizer** — управление портфелем
- **Career Development** — развитие карьеры
- **Job Automation Agent** — автоматизация задач
- **AI Config Manager** — управление конфигурациями

---

## 🛠️ Технологии

| Категория | Технологии |
|-----------|------------|
| **Язык** | Python 3.10+ |
| **Фреймворки** | FastAPI, LangChain, Streamlit |
| **БД** | PostgreSQL 16, ChromaDB, Redis 7 |
| **Контейнеризация** | Docker, Docker Compose |
| **Оркестрация** | Kubernetes (Kustomize), GitOps |
| **Мониторинг** | Prometheus, Grafana, AlertManager |
| **CI/CD** | GitHub Actions |
| **Безопасность** | Trivy, Bandit, Sealed Secrets |

---

## 📁 Структура проекта

```
portfolio-system-architect/
├── apps/                    # Микросервисы (14 компонентов)
│   ├── cognitive-agent/     # Когнитивный агент
│   ├── it-compass/          # Методология компетенций
│   ├── decision-engine/     # AI reasoning engine
│   └── ... (ещё 11 сервисов)
├── src/                     # Общие ядра и логика
├── deployment/              # Kubernetes, GitOps
├── monitoring/              # Prometheus, Grafana
├── docs/                    # Документация
├── tests/                   # Тесты
└── tools/                   # Утилиты
```

---

## 🧪 Тестирование

```bash
# Юнит- и интеграционные тесты
pytest --cov=apps --cov=src --cov-report=html

# E2E тесты
pytest -m e2e

# Проверка покрытия (порог 95%)
pytest --cov-fail-under=95
```

---

## 📄 Документация

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — детальная архитектура
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — руководство по контрибуции
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — быстрое начало
- [`deployment/README.md`](deployment/README.md) — развёртывание
- [`.devtools/`](.devtools/) — конфигурация инструментов разработки (AI, IDE)

---

## 🔧 Разработка

### Линтинг и форматирование

```bash
# Проверка качества
make lint

# Форматирование
make format

# Полная проверка (lint + test)
make ci
```

### Docker-окружение

```bash
# Запуск всех сервисов
make docker-up

# Просмотр логов
make docker-logs

# Сборка образов
make docker-build
```

---

## 📋 Полезные команды

```bash
# Установка зависимостей
make install

# Запуск среды разработки
make dev

# Запуск тестов
make test

# Генерация документации
make docs

# Pre-commit проверки
make pre-commit
```

---

## 🤝 Вклад в развитие

См. [CONTRIBUTING.md](CONTRIBUTING.md)

## 📋 Технические долги

- [ ] **Переименование `cognitive-agent`** → `cognitive_agent` (валидный Python-пакет)
  - 📄 План: `.koda/plans/cognitive-agent-rename-analysis.md`
  - ⚠️ Риск: Высокий (800+ файлов), 2-3 часа работы
  - 🎯 Приоритет: Низкий (не критично, код работает)

## 📄 Лицензия

MIT
