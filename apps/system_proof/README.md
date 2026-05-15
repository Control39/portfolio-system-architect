# System Proof

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Система сбора и верификации доказательств для Chain-of-Thought (CoT) рассуждений. Обеспечивает автоматическую валидацию критериев производственной готовности с прозрачной логикой принятия решений.

### Ключевые возможности
- [x] CRUD операции с коллекциями доказательств
- [x] Управление шагами рассуждения (step management)
- [x] Поиск и фильтрация по chain_id, архитектуре, тегам
- [x] Автоматическая верификация доказательств
- [x] Полная поддержка Chain-of-Thought (CoT)

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | PostgreSQL (опционально), Redis (кэш) |
| **Порт (Internal)** | 8003 (внутри контейнера) |
| **Порт (External)** | 8003 |
| **Traefik Route** | `/system-proof` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/system-proof`)
         ▼
┌─────────────────┐
│  system_proof   │  Internal: 8003
│  (FastAPI)      │  External: 8003
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL/    │
│  Redis          │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/system_proof

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8003

# 4. Открыть Swagger UI
# http://localhost:8003/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d system_proof

# Проверить статус
docker-compose ps | grep system_proof

# Просмотр логов
docker-compose logs -f system_proof
```

### Остановка

```bash
docker-compose stop system_proof
# или
docker-compose down system_proof
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/proofs` | Создание доказательства | ✅ |
| `GET` | `/api/v1/proofs` | Список доказательств | ✅ |
| `GET` | `/api/v1/proofs/{id}` | Получение доказательства | ✅ |
| `POST` | `/api/v1/proofs/{id}/verify` | Верификация | ✅ |
| `GET` | `/api/v1/proofs/search` | Поиск по критериям | ✅ |
| `DELETE` | `/api/v1/proofs/{id}` | Удаление доказательства | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8003/health

# Через Traefik
curl http://localhost/system-proof/api/v1/proofs

# Создание доказательства
curl -X POST http://localhost:8003/api/v1/proofs \
  -H "Content-Type: application/json" \
  -d '{
    "chain_id": "decision-001",
    "architecture": "microservices",
    "steps": [
      {"step": 1, "reasoning": "Выбран микросервисный подход", "verified": true}
    ]
  }'
```

### Пример ответа

```json
{
  "id": "proof-123",
  "chain_id": "decision-001",
  "architecture": "microservices",
  "status": "verified",
  "steps": [
    {"step": 1, "reasoning": "Выбран микросервисный подход", "verified": true}
  ],
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8003/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Валидация цепочек рассуждений** — проверка целостности CoT
- [x] **Защита от инъекций** — санитизация полей поиска

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
pytest apps/system_proof/tests/ --cov=apps/system_proof --cov-report=term-missing

# С HTML отчётом
pytest apps/system_proof/tests/ --cov=apps/system_proof --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 40/40 | ≥80% ✅ |
| **Integration Tests** | 15/15 | ≥60% ✅ |
| **Business Logic Tests** | 25/25 | 100% ✅ |
| **Total Coverage** | ~80% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 15 | CRUD, конфигурация, health checks |
| **Бизнес-логика** | `test_proof_business.py` | 25 | Верификация, поиск, фильтрация, transitions |

**Итого:** 40 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0  # опционально для PostgreSQL
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
- [ ] Redis (опционально, для кэширования)
- [ ] Auth Service (для аутентификации API)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Database (опционально)
DATABASE_URL=postgresql://user:password@postgres:5432/system_proof  # pragma: allowlist secret

# Cache (опционально)
REDIS_URL=redis://redis:6379

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
# .github/workflows/system-proof-ci.yml
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
        run: pytest apps/system_proof/tests/
      - name: Run linters
        run: ruff check apps/system_proof/
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
- **[Decision Engine]** — принятие решений (использует доказательства)
- **[Portfolio Organizer]** — сбор доказательств для портфолио
- **[Knowledge Graph]** — хранение связей между доказательствами

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с PostgreSQL требует Docker-окружения | Open | Использовать memory mode для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 40 тестов с 100% прохождением
- **Added:** Ядро системы (ProofCollection, верификация)
- **Added:** Поиск по chain_id/architecture/тегам
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
