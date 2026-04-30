# KODA.md — Контекст для взаимодействия с проектом

> **Дата создания:** 22 апреля 2026 г.
> **Тип проекта:** Продукт с кодом — когнитивная архитектура и система автоматизации

---

## 📋 Обзор проекта

### Назначение

**Portfolio System Architect** — это производственно-готовая экосистема когнитивной архитектуры, демонстрирующая трансформацию от полного отсутствия IT-опыта до создания 14 интегрированных микросервисов за 2 года. Проект представляет собой:

1. **Cognitive Automation Agent (CAA)** — автономная система автоматизации с интеллектуальными возможностями
2. **IT-Compass** — методология объективного измерения компетенций через 83 проверочных маркера в 19 IT-доменах
3. **Систему оркестрации ИИ** — использование ИИ как исполнительного слоя под строгим архитектурным контролем

### Ключевые технологии

| Категория | Технологии |
|-----------|------------|
| **Язык программирования** | Python 3.10+ |
| **Фреймворки** | FastAPI, LangChain, Streamlit |
| **База данных** | PostgreSQL 16, ChromaDB (векторная БД), Redis 7 |
| **Контейнеризация** | Docker, Docker Compose |
| **Оркестрация** | Kubernetes (Kustomize), GitOps |
| **Мониторинг** | Prometheus, Grafana, AlertManager |
| **API Gateway** | Traefik v3.0 |
| **CI/CD** | GitHub Actions |
| **Безопасность** | Trivy, Bandit, Sealed Secrets |
| **ИИ/ML** | LangChain, ChromaDB, Sentence Transformers |

### Архитектурная структура

```
portfolio-system-architect/
├── .agents/                    # Cognitive Automation Agent (продукт)
│   ├── skills/                # Навыки CAA (автономное выполнение)
│   ├── config/                # Конфигурации автономной системы
│   ├── workflows/             # Автономные рабочие процессы
│   └── tests/                 # Тесты для CAA
├── .codeassistant/            # SourceCraft Agent Skills
│   ├── skills/                # Skills для анализа и работы
│   ├── context.md             # Контекст для ИИ-ассистента
│   └── mcp.json               # MCP конфигурация
├── apps/                      # 14 интегрированных микросервисов
│   ├── it-compass/           # IT-Compass фреймворк
│   ├── cloud-reason/         # AI reasoning engine с RAG
│   ├── portfolio-organizer/  # Автоматический сбор доказательств
│   ├── system-proof/         # Хранение доказательств (CoT)
│   ├── ml-model-registry/    # Регистр ML-моделей
│   ├── auth-service/         # JWT аутентификация
│   ├── career-development/   # Развитие карьеры
│   └── ... (ещё 7 компонентов)
├── src/                       # Общие ядра и логика валидации
│   ├── ai/                   # ИИ-оркестрация
│   ├── core/                 # Базовая логика
│   ├── infrastructure/       # Инфраструктурные компоненты
│   ├── security/             # Безопасность
│   └── repo_audit/           # Инструмент аудита репозитория
├── deployment/                # Kubernetes, GitOps, Sealed Secrets
├── monitoring/                # Prometheus, Grafana, кастомные дашборды
├── docs/                      # Архитектурные решения, методология
├── tools/                     # Утилиты аудита, CI/CD, сканеры безопасности
└── docker/                    # Docker-конфигурации
```

### Основные компоненты

#### 1. Cognitive Automation Agent (.agents/)
Автономная система для управления проектами с интеллектуальными возможностями:
- **Project Scanner** — интеллектуальное сканирование технологического стека
- **Task Planner** — проактивное планирование задач
- **Learning System** — система самообучения на основе метрик
- **Trigger System** — система триггеров и автоматических действий

#### 2. IT-Compass (apps/it-compass/)
Методологическое ядро для объективного измерения компетенций:
- 83 проверочных маркера в 19 IT-доменах
- Модульный Python-пакет с JSON-схемой
- Streamlit UI для визуализации
- Интеграция с портфолио и облачными решениями
- Психологическая поддержка (профилактика выгорания)

#### 3. Microservices Architecture
14 интегрированных микросервисов, 12 из которых контейнеризованы:
- **Cloud Reason Engine** — принятие решений на основе ИИ с объяснимой логикой
- **Portfolio Organizer** — автоматический сбор доказательств и картирование компетенций
- **RAG API** — векторный поиск и документная интеллектуализация
- **System Proof** — автоматическая валидация критериев производственной готовности
- **ML Model Registry** — версионированные ML-модели с A/B тестированием
- **API Gateway** — единая точка входа с безопасностью и наблюдаемостью

---

## 🚀 Сборка и запуск

### Предварительные требования

- **Docker & Docker Compose** (Docker Desktop или Docker Engine)
- **Git** с Git LFS (Large File Storage)
- **Python 3.10+** (для разработки)
- **4GB+ RAM** для контейнеров

### Установка зависимостей

```bash
# Создание виртуального окружения (если отсутствует)
make install

# Или вручную:
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements-dev.txt
pip install -e .

# Установка pre-commit hooks
pre-commit install
```

### Запуск среды разработки

```bash
# Запуск всех сервисов через Docker Compose
make dev

# Или вручную:
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Проверка состояния сервисов
docker-compose ps
```

### Доступ к сервисам

| Сервис | URL | Назначение | Креденшиалы |
|--------|-----|------------|-------------|
| **Traefik Dashboard** | http://localhost:8080 | Управление API-шлюзом | - |
| **IT-Compass UI** | http://localhost:8501 | Трекинг компетенций | - |
| **Cloud-Reason API** | http://localhost:8001/docs | AI reasoning & RAG | - |
| **ML Registry API** | http://localhost:8001/docs | Управление моделями | - |
| **Grafana** | http://localhost:3000 | Мониторинг | admin/admin |
| **Prometheus** | http://localhost:9090 | Сбор метрик | - |
| **Auth Service** | http://localhost:8100 | JWT аутентификация | username=demo, password=demo |

### Запуск тестов

```bash
# Юнит- и интеграционные тесты с покрытием
make test

# Или вручную:
pytest --cov=apps --cov=src --cov-report=html --cov-report=term-missing

# E2E тесты (медленные)
pytest -m e2e

# Проверка покрытия (порог 95%)
pytest --cov-fail-under=95
```

### Линтинг и форматирование

```bash
# Запуск линтеров
make lint

# Вручную:
ruff check .
black --check .
mypy apps src

# Форматирование кода
make format

# Вручную:
black .
isort .
```

### Сборка Docker-образов

```bash
# Построение всех образов
make docker-build

# Вручную:
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml build
```

### Управление Docker-окружением

```bash
# Запуск всех сервисов
make docker-up

# Остановка сервисов
make docker-down

# Просмотр логов
make docker-logs

# Вручную:
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml logs -f
```

### Генерация документации

```bash
# Локальный просмотр документации
make docs

# Вручную:
mkdocs serve
```

### Pre-commit проверки

```bash
# Запуск всех pre-commit хуков
make pre-commit

# Вручную:
pre-commit run --all-files
```

### CI/CD pipeline

```bash
# Полная проверка (lint + test)
make ci

# Вручную:
make lint && make test
```

---

## 🛠️ Правила разработки

### Стиль кодирования

1. **Python-стандарты**:
   - Использование **Black** для форматирования
   - **isort** для сортировки импортов
   - **Ruff** для линтинга (заменяет flake8, pylint)
   - **MyPy** для статической типизации

2. **Структура кода**:
   - Файлы тестов: `test_*.py`
   - Функции тестов: `test_*`
   - Классы тестов: `Test*`
   - Пути тестов: `apps/`, `tests/`, `tests/e2e/`, `tests/unit/`

3. **Конфигурация линтеров**:
   - **pyrightconfig.json** — настройки статической типизации
   - **.ruff_cache/** — кэш линтера Ruff
   - **.pre-commit-config.yaml** — конфигурация pre-commit хуков

### Практики тестирования

1. **Уровни тестирования**:
   - **Юнит-тесты** — изолированные тесты отдельных компонентов
   - **Интеграционные тесты** — тесты взаимодействия компонентов
   - **E2E тесты** — полные сценарии использования (помечены как `slow`)
   - **Нагрузочные тесты** — с помощью Locust

2. **Покрытие кода**:
   - Минимальный порог: **95%** (настроен в `pyproject.toml`)
   - Отчёты: HTML + терминал с пропусками
   - Пути покрытия: `apps/`, `src/`

3. **Маркеры тестов**:
   - `@pytest.mark.e2e` — E2E тесты (запускаются отдельно)
   - `@pytest.mark.slow` — медленные тесты

4. **Файлы тестов**:
   - Расположение: `tests/`, `apps/*/tests/`
   - Имя: `test_*.py`
   - Импорты: тестовые утилиты из `tests/conftest.py`

### Правила контрибуции

1. **Git workflow**:
   - Использовать ветки с понятными именами
   - Коммиты с сообщениями на английском
   - Protected branches для `main`
   - Code review для всех PR

2. **Безопасность**:
   - Не коммитить секреты (использовать `.secrets.baseline`)
   - Регулярные Trivy-сканы
   - Bandit для Python-безопасности
   - Sealed Secrets для Kubernetes

3. **Документация**:
   - Все архитектурные решения в `docs/architecture/decisions/` (ADR)
   - Обновление README при изменении API
   - Чек-листы для сложных изменений

4. **CI/CD**:
   - Все изменения должны проходить CI
   - Автоматические тесты при push
   - GitOps-подход для деплоя

### Конфигурационные файлы

| Файл | Назначение |
|------|------------|
| `pyproject.toml` | Зависимости, настройки сборки, pytest |
| `requirements.txt` | Замороженные зависимости |
| `requirements-dev.txt` | Зависимости для разработки |
| `requirements.in` | Исходные зависимости (для pip-tools) |
| `docker-compose.yml` | Конфигурация Docker-сервисов |
| `Makefile` | Команды для разработки |
| `.pre-commit-config.yaml` | Pre-commit хуки |
| `sonar-project.properties` | Настройки SonarQube |
| `trivy-secret.yaml` | Конфигурация Trivy для секрета |

### Архитектурные принципы

1. **Разделение ответственности**:
   - `.agents/` — автономное выполнение (уровень реализации)
   - `.codeassistant/` — аналитические skills (уровень анализа)
   - Чёткие границы между микросервисами

2. **Contract-first design**:
   - API-контракты определяются заранее
   - Валидация через Pydantic
   - OpenAPI/Swagger документация

3. **Observability by default**:
   - Метрики для всех сервисов
   - Логирование в структурированном формате
   - Health checks для всех контейнеров

4. **Security by design**:
   - JWT аутентификация
   - Rate limiting через Traefik
   - Network policies в Kubernetes
   - Регулярные security сканы

---

## 📚 Дополнительные ресурсы

### Документация

- [`README.md`](README.md) — основной обзор проекта
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — детальная архитектура
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — быстрое начало
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — руководство по контрибуции
- [`docs/architecture/decisions/`](docs/architecture/decisions/) — архитектурные решения (ADR)

### Кейсы и примеры

- [`docs/cases/`](docs/cases/) — реальные примеры решения проблем
- [`examples/`](examples/) — примеры использования
- [`apps/it-compass/`](apps/it-compass/) — методология IT-Compass

### Инструменты

- [`tools/repo_audit/`](tools/repo_audit/) — инструмент аудита репозитория
- [`scripts/`](scripts/) — скрипты для автоматизации
- [`deployment/`](deployment/) — Kubernetes манифесты и GitOps

### Отчёты

- [`QUALITY-GATES.md`](quality-gates.md) — метрики качества
- [`PROFESSIONAL_ENVIRONMENT_SETUP_REPORT.md`](PROFESSIONAL_ENVIRONMENT_SETUP_REPORT.md) — отчёт о настройке окружения
- [`REFACTORING_SUMMARY.md`](REFACTORING_SUMMARY.md) — итоги рефакторинга

---

## 🔍 Для ИИ-агента Koda

### Контекст взаимодействия

1. **Язык**: Все ответы и документация на русском языке
2. **Тип проекта**: Продукт с кодом — Python-микросервисы
3. **Основная цель**: Демонстрация системного мышления и оркестрации ИИ
4. **Ключевые стейкхолдеры**: HR, технические лиды, DevOps, исследователи

### Рекомендации для анализа

1. **При чтении кода**:
   - Обращать внимание на ADR в `docs/architecture/decisions/`
   - Проверять соответствие архитектурным принципам
   - Искать интеграционные паттерны между микросервисами

2. **При генерации кода**:
   - Следовать стилю Black + isort + Ruff
   - Добавлять type hints
   - Писать тесты для нового кода
   - Использовать Pydantic для валидации

3. **При анализе проблем**:
   - Проверять health checks сервисов
   - Анализировать логи через `docker-compose logs`
   - Использовать Grafana для метрик
   - Проверять security сканы

### Критические пути

1. **Запуск среды**: `make dev` → проверить все сервисы
2. **Запуск тестов**: `make test` → покрытие > 95%
3. **Линтинг**: `make lint` → без ошибок
4. **Деплой**: `deployment/k8s/` → GitOps workflow

---

*Файл сгенерирован 22 апреля 2026 г. на основе анализа структуры проекта, README, ARCHITECTURE.md, Makefile, docker-compose.yml, pyproject.toml и QUICKSTART.md.*
