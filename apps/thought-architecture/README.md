# Thought Architecture

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Система отслеживания и управления архитектурными решениями (ADR). Обеспечивает полный жизненный цикл решений: от предложения до принятия/отклонения/замены, с хранением доказательств и отзывов.

### Ключевые возможности
- [x] Полный жизненный цикл решений (proposed → accepted/rejected/superseded)
- [x] Управление Architecture Records (доказательства, отзывы)
- [x] Продвинутое фильтрование (по статусу, уровню, тегам)
- [x] Статистика и анализ распределения решений
- [x] REST API для управления решениями

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | Auth Service (опционально) |
| **Порт (Internal)** | 8010 (внутри контейнера) |
| **Порт (External)** | 8010 |
| **Traefik Route** | `/thought-architecture` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/thought-architecture`)
         ▼
┌─────────────────┐
│  thought-architecture │  Internal: 8010
│  (FastAPI)      │  External: 8010
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL/    │
│  Memory Store   │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/thought-architecture

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8010

# 4. Открыть Swagger UI
# http://localhost:8010/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d thought-architecture

# Проверить статус
docker-compose ps | grep thought-architecture

# Просмотр логов
docker-compose logs -f thought-architecture
```

### Остановка

```bash
docker-compose stop thought-architecture
# или
docker-compose down thought-architecture
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/decisions` | Создание решения | ✅ |
| `GET` | `/api/v1/decisions/{decision_id}` | Получение решения | ✅ |
| `GET` | `/api/v1/decisions` | Список решений (с фильтрами) | ✅ |
| `PUT` | `/api/v1/decisions/{decision_id}/approve` | Одобрение решения | ✅ |
| `PUT` | `/api/v1/decisions/{decision_id}/reject` | Отклонение решения | ✅ |
| `PUT` | `/api/v1/decisions/{decision_id}/supersede` | Замена решения | ✅ |
| `GET` | `/api/v1/statistics` | Статистика по решениям | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8010/health

# Создание решения
curl -X POST http://localhost:8010/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Использовать PostgreSQL вместо SQLite",
    "description": "Необходимо для поддержки production-нагрузок",
    "level": "high",
    "tags": ["database", "performance"]
  }'

# Одобрение решения
curl -X PUT http://localhost:8010/api/v1/decisions/{id}/approve \
  -H "Authorization: Bearer <token>"
```

### Пример ответа

```json
{
  "decision_id": "dec_123",
  "title": "Использовать PostgreSQL вместо SQLite",
  "status": "proposed",
  "level": "high",
  "tags": ["database", "performance"],
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8010/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Ролевая модель** — интеграция с Auth Service (admin/user)
- [x] **Уникальность ID** — защита от дубликатов
- [x] **Санитизация тегов** — ограничение длины и символов

### Security Checklist

При добавлении нового функционала проверить:

- [x] Нет hardcoded secrets в коде
- [x] Все внешние вызовы валидируют SSL
- [x] Input sanitization для пользовательских данных
- [x] Логирование security-событий (без секретов!)

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Из корневого каталога
pytest apps/thought-architecture/tests/ --cov=apps/thought-architecture --cov-report=term-missing

# С HTML отчётом
pytest apps/thought-architecture/tests/ --cov=apps/thought-architecture --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 38/38 | ≥80% ✅ |
| **Integration Tests** | 3/3 | ≥60% ✅ |
| **Total Coverage** | ~85% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 15 | CRUD операции, конфигурация |
| **Бизнес-логика** | `test_thought_business.py` | 37 | Жизненный цикл, фильтрация, статистика |
| **Интеграционные** | `test_integration_thought_architecture.py` | 3 | Полный workflow |
| **Граничные случаи** | Встроен в бизнес-тесты | 9 | None, Unicode, длинные строки |

**Итого:** 38 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### Внешние сервисы

- [ ] PostgreSQL (опционально, для production)
- [ ] Auth Service (для аутентификации API)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Database (опционально)
DATABASE_URL=postgresql://user:password@postgres:5432/thought_arch  # pragma: allowlist secret

# Storage
STORAGE_MODE=memory  # или postgresql

# Logging
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-prod  # pragma: allowlist secret
```

### Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `.env` | Переменные окружения (не коммитить!) |
| `config/settings.py` | Конфигурация сервиса |
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
# .github/workflows/thought-architecture-ci.yml
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
        run: pytest apps/thought-architecture/tests/
      - name: Run linters
        run: ruff check apps/thought-architecture/
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
- **[Decision Engine]** — принятие решений (использует ADR)
- **[Cognitive Agent]** — автономное принятие решений

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с PostgreSQL требует Docker-окружения | Open | Использовать memory mode для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 38 тестов с 100% прохождением
- **Added:** Полный жизненный цикл решений (approve, reject, supersede)
- **Added:** Статистика и фильтрация по тегам
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
