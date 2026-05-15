# [Название Сервиса]

> **Статус:** [Draft/Active/Maintenance]
> **Владелец:** [Команда/Имя]
> **Последнее обновление:** [Дата]

---

## 🎯 Назначение

[Краткое описание бизнес-логики в 1-2 предложениях. Например: "Движок принятия решений на основе правил с поддержкой RAG для объяснимого ИИ."]

### Ключевые возможности
- [ ] Возможность 1 (например: "REST API для управления моделями")
- [ ] Возможность 2 (например: "Версионирование ML-моделей")
- [ ] Возможность 3 (например: "A/B тестирование моделей")

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | [PostgreSQL, Redis, ChromaDB — указать актуальные] |
| **Порт (Internal)** | 8000 (внутри контейнера) |
| **Порт (External)** | [Порт из docker-compose.yml, например: 8001] |
| **Traefik Route** | `/api/[prefix]` или `/service-name` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/[route]`)
         ▼
┌─────────────────┐
│  [Service]      │  Internal: 8000
│  (FastAPI)      │  External: [PORT]
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL/    │
│  Redis/ChromaDB │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/[service-name]

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn main:app --reload --port 8000

# 4. Открыть Swagger UI
# http://localhost:8000/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d [service-name]

# Проверить статус
docker-compose ps | grep [service-name]

# Просмотр логов
docker-compose logs -f [service-name]
```

### Остановка

```bash
docker-compose stop [service-name]
# или
docker-compose down [service-name]
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/[action]` | [Основная функция] | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8000/health

# Через Traefik (если service exposed)
curl http://localhost/[route]/api/v1/[action]
```

### Пример ответа

```json
{
  "status": "ok",
  "service": "[service-name]",
  "version": "1.0.0"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:[PORT]/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [ ] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [ ] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [ ] **Защита от SSRF** — проверка URL на internal/private IP ranges
- [ ] **Защита от Path Traversal** — санитизация путей к файлам
- [ ] **Аутентификация** — JWT через Auth Service (`Authorization: Bearer <token>`)
- [ ] **Rate Limiting** — через Traefik middleware (если настроено)

### Security Checklist

При добавлении нового функционала проверить:

- [ ] Нет hardcoded secrets в коде
- [ ] Все внешние вызовы валидируют SSL
- [ ] Input sanitization для пользовательских данных
- [ ] Логирование security-событий (без секретов!)

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Из корневого каталога
pytest apps/[service-name]/tests/ --cov=apps/[service-name] --cov-report=term-missing

# Или из директории сервиса (если есть pytest.ini)
pytest --cov=. --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | [X/X] | ≥80% |
| **Integration Tests** | [X/X] | ≥60% |
| **Total Coverage** | [X%] | ≥80% |

### Типы тестов

- **Unit tests** — изолированные тесты компонентов (`tests/unit/`)
- **Integration tests** — тесты API endpoints (`tests/integration/`)
- **Security tests** — тесты на уязвимости (`tests/test_security_*.py`)
- **E2E tests** — полные сценарии использования (`tests/e2e/`)

---

## 📦 Зависимости

### Production зависимости

```txt
# requirements.txt или pyproject.toml
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
# ... остальные зависимости
```

### Development зависимости

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0  # для тестирования FastAPI
```

### Внешние сервисы

- [ ] PostgreSQL (если используется БД)
- [ ] Redis (если используется кэш/очередь)
- [ ] ChromaDB (если используется векторный поиск)
- [ ] Auth Service (если требуется аутентификация)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/[db_name]  # pragma: allowlist secret

# Logging
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-prod  # pragma: allowlist secret

# External Services
REDIS_URL=redis://redis:6379
```

### Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `.env` | Переменные окружения (не коммитить!) |
| `config.yaml` | Конфигурация сервиса (опционально) |
| `pyproject.toml` | Зависимости и настройки сборки |

---

## 📊 Мониторинг

### Метрики

- **Prometheus endpoint:** `GET /metrics` (если включено)
- **Structured logging:** JSON format в stdout
- **Health checks:** `/health`, `/ready`

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/[service]-ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest apps/[service-name]/tests/
      - name: Run linters
        run: ruff check apps/[service-name]/
```

### Развёртывание

- **Environment:** Staging → Production
- **Strategy:** Blue-Green или Canary (через Kubernetes)
- **Rollback:** Автоматический при health check failure

---

## 📚 Дополнительные ресурсы

### Документация

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — общий обзор архитектуры
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — правила контрибуции
- [SECURITY.md](../../SECURITY.md) — политика безопасности

### Связанные сервисы

- **[Auth Service]** — аутентификация и JWT
- **[Decision Engine]** — принятие решений (если есть зависимость)
- **[ML Model Registry]** — управление моделями (если есть зависимость)

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| [Описание] | Open/Fixed | [Workaround] |

---

## 📝 Changelog

### [1.0.0] — YYYY-MM-DD

- Added: [Перечислить новые функции]
- Fixed: [Исправленные баги]
- Changed: [Изменения в API]

---

## 👥 Контрибьюторы

- [Имя] — [Роль/Вклад]
- [Имя] — [Роль/Вклад]

---

*Шаблон сгенерирован для проекта **Portfolio System Architect**. Последнее обновление: 2026-05-15*
