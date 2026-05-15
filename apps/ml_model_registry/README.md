# ML Model Registry

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Реестр машинных моделей с версионированием и A/B тестированием. Обеспечивает полный жизненный цикл моделей: регистрация, хранение, поиск, развертывание и мониторинг дрейфа данных.

### Ключевые возможности
- [x] Версионирование моделей (семантическое MAJOR.MINOR.PATCH)
- [x] REST API для управления моделями
- [x] A/B тестирование моделей в production
- [x] Поиск моделей по метаданным и архитектуре
- [x] Поддержка локального и облачного хранения (S3, Azure Blob)

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | ChromaDB (опционально), PostgreSQL |
| **Порт (Internal)** | 8002 (внутри контейнера) |
| **Порт (External)** | 8002 |
| **Traefik Route** | `/ml-registry` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/ml-registry`)
         ▼
┌─────────────────┐
│  ml_model_registry  │  Internal: 8002
│  (FastAPI)      │  External: 8002
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ChromaDB/      │
│  PostgreSQL     │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/ml_model_registry

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8002

# 4. Открыть Swagger UI
# http://localhost:8002/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d ml_model_registry

# Проверить статус
docker-compose ps | grep ml_model_registry

# Просмотр логов
docker-compose logs -f ml_model_registry
```

### Остановка

```bash
docker-compose stop ml_model_registry
# или
docker-compose down ml_model_registry
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/models` | Регистрация модели | ✅ |
| `GET` | `/api/v1/models/{model_id}` | Получение модели | ✅ |
| `GET` | `/api/v1/models` | Список моделей | ✅ |
| `GET` | `/api/v1/models/search` | Поиск моделей | ✅ |
| `DELETE` | `/api/v1/models/{model_id}` | Удаление модели | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8002/health

# Через Traefik
curl http://localhost/ml-registry/api/v1/models

# Регистрация модели
curl -X POST http://localhost:8002/api/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fraud_detector",
    "data": {"architecture": "XGBoost", "accuracy": 0.95},
    "version": "1.0.0"
  }'
```

### Пример ответа

```json
{
  "status": "registered",
  "model_id": "fraud_detector",
  "version": "1.0.0",
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8002/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Защита от Path Traversal** — санитизация путей к файлам (24 теста)
- [x] **SQL-инъекции** — отклонение вредоносных запросов
- [x] **XSS** — санитизация данных модели
- [x] **Инъекция ID** — валидация символов

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
pytest apps/ml_model_registry/tests/ --cov=apps/ml_model_registry --cov-report=term-missing

# С HTML отчётом
pytest apps/ml_model_registry/tests/ --cov=apps/ml_model_registry --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 70/70 | ≥80% ✅ |
| **Integration Tests** | 3/3 | ≥60% ✅ |
| **Security Tests** | 11/11 | 100% ✅ |
| **Total Coverage** | ~90% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 14 | CRUD операции, конфигурация |
| **Контрактные** | `test_contract.py` | 8 | Проверка интерфейсов |
| **Граничные случаи** | `test_edge_cases.py` | 8 | None, пустые данные, спецсимволы |
| **Fuzz-тесты** | `test_fuzz.py` | 5 | Случайные данные/ID |
| **Интеграционные** | `test_integration.py` | 3 | Полный цикл жизни модели |
| **Хранение** | `test_model_storage.py` | 6 | Сохранение/загрузка |
| **Производительность** | `test_performance.py` | 3 | 1000+ моделей |
| **Безопасность** | `test_security.py` | 11 | Инъекции, XSS, path traversal |
| **Отказоустойчивость** | `test_resilience.py` | 2 | Сбои хранилища |
| **API** | `test_api.py` | 2 | Health check, root |

**Итого:** 70 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
chromadb>=0.4.0  # опционально
psycopg2-binary>=2.9.0  # опционально
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
- [ ] ChromaDB (опционально, для векторного поиска)
- [ ] Auth Service (для аутентификации API)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Database (опционально)
DATABASE_URL=postgresql://user:password@postgres:5432/ml_registry  # pragma: allowlist secret

# Storage
STORAGE_MODE=local  # или azure/s3
LOCAL_STORAGE_PATH=./data/models

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
# .github/workflows/ml-model-registry-ci.yml
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
        run: pytest apps/ml_model_registry/tests/
      - name: Run linters
        run: ruff check apps/ml_model_registry/
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
- **[Decision Engine]** — принятие решений (использует модели из реестра)
- **[Portfolio Organizer]** — сбор доказательств для моделей

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с ChromaDB требует Docker-окружения | Open | Использовать memory mode для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 70 тестов с 100% прохождением
- **Added:** Защита от Path Traversal (24 теста)
- **Added:** A/B тестирование моделей
- **Fixed:** Конфликт портов (перенос на 8002)
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
