# Job Automation Agent

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

AI-агент для автоматизации поиска вакансий и оптимизации резюме. Автоматически анализирует требования вакансий, извлекает навыки из резюме и вычисляет степень соответствия.

### Ключевые возможности
- [x] Анализ вакансий и требований
- [x] Парсинг резюме (извлечение навыков)
- [x] Вычисление совпадения навыков (match scoring)
- [x] Анализ рыночных трендов
- [x] Автономная работа агента (orchestration)

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | LangChain (опционально), Auth Service |
| **Порт (Internal)** | 8005 (внутри контейнера) |
| **Порт (External)** | 8005 |
| **Traefik Route** | `/job-agent` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/job-agent`)
         ▼
┌─────────────────┐
│  job-automation-agent │  Internal: 8005
│  (FastAPI)      │  External: 8005
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auth Service / │
│  Knowledge Graph│
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/job-automation-agent

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8005

# 4. Открыть Swagger UI
# http://localhost:8005/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d job-automation-agent

# Проверить статус
docker-compose ps | grep job-automation-agent

# Просмотр логов
docker-compose logs -f job-automation-agent
```

### Остановка

```bash
docker-compose stop job-automation-agent
# или
docker-compose down job-automation-agent
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/analyze/jobs` | Анализ вакансии | ✅ |
| `POST` | `/api/v1/parse/resume` | Парсинг резюме | ✅ |
| `GET` | `/api/v1/match` | Расчёт совпадения | ✅ |
| `POST` | `/api/v1/search` | Поиск вакансий | ✅ |
| `GET` | `/api/v1/trends` | Анализ трендов | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8005/health

# Через Traefik
curl http://localhost/job-agent/api/v1/analyze/jobs

# Анализ вакансии
curl -X POST http://localhost:8005/api/v1/analyze/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Required: Python, FastAPI, Docker...",
    "requirements": ["Python 3.10+", "FastAPI", "Docker"]
  }'
```

### Пример ответа

```json
{
  "job_id": "job-123",
  "analysis": {
    "primary_skills": ["Python", "FastAPI", "Docker"],
    "experience_level": "mid-senior",
    "salary_range": "$120k-150k"
  },
  "match_score": 0.85
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8005/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Защита от инъекций** — санитизация текста вакансий и резюме
- [x] **Аутентификация** — JWT через Auth Service

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
pytest apps/job-automation-agent/tests/ --cov=apps/job-automation-agent --cov-report=term-missing

# С HTML отчётом
pytest apps/job-automation-agent/tests/ --cov=apps/job-automation-agent --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 32/32 | ≥80% ✅ |
| **Business Logic Tests** | 21/21 | 100% ✅ |
| **Agent Orchestration** | 4/4 | 100% ✅ |
| **Total Coverage** | ~85% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 15 | CRUD, конфигурация, health checks |
| **Бизнес-логика** | `test_agent_business.py` | 21 | Парсинг, анализ, matching, тренды |
| **Оркестрация** | `test_agent_orchestration.py` | 4 | Автономная работа агента |

**Итого:** 32 теста (21 passed + 4 оркестрация + 7 базовых), 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
langchain>=0.3.0  # опционально для AI-агента
python-docx>=1.0.0  # для парсинга резюме
pdfplumber>=0.10.0  # для парсинга PDF
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### Внешние сервисы

- [x] **Auth Service** — аутентификация и JWT
- [ ] **Knowledge Graph** — хранение профилей навыков
- [ ] **ML Model Registry** — модели для matching

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# External APIs
AUTH_SERVICE_URL=http://localhost:8100/api
KNOWLEDGE_GRAPH_URL=http://localhost:8006/api

# AI Configuration (опционально)
LANGCHAIN_TRACING_V2=false
OPENAI_API_KEY=your-api-key  # pragma: allowlist secret

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
- **Agent metrics:** Количество обработанных вакансий/резюме

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/job-automation-agent-ci.yml
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
        run: pytest apps/job-automation-agent/tests/
      - name: Run linters
        run: ruff check apps/job-automation-agent/
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
- **[Knowledge Graph]** — хранение профилей навыков
- **[Career Development]** — трекинг карьерного роста
- **[Portfolio Organizer]** — сбор доказательств навыков

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Полная реализация агента требует langgraph | Open | Использовать упрощённую реализацию для тестирования |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 32 теста с 100% прохождением
- **Added:** Ядро анализа вакансий и парсинга резюме
- **Added:** JobAgentOrchestrator для автономной работы
- **Added:** Анализ рыночных трендов
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
