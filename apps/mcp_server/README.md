# MCP Server

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Сервер Model Context Protocol (MCP) для взаимодействия с AI-агентами. Обеспечивает регистрацию инструментов, управление ресурсами и шаблонами промптов для автономных агентов.

### Ключевые возможности
- [x] Поддержка Model Context Protocol (MCP)
- [x] Регистрация и управление инструментами
- [x] Управление ресурсами и контекстом
- [x] Шаблоны промптов для AI-агентов
- [x] Жизненный цикл сервера (запуск, остановка, health checks)

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker, MCP SDK |
| **Зависимости** | Auth Service (опционально), AI Agents |
| **Порт (Internal)** | 8008 (внутри контейнера) |
| **Порт (External)** | 8008 |
| **Traefik Route** | `/mcp-server` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/mcp-server`)
         ▼
┌─────────────────┐
│  mcp_server     │  Internal: 8008
│  (FastAPI)      │  External: 8008
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Agents /    │
│  Knowledge Base │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/mcp_server

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8008

# 4. Открыть Swagger UI
# http://localhost:8008/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d mcp_server

# Проверить статус
docker-compose ps | grep mcp_server

# Просмотр логов
docker-compose logs -f mcp_server
```

### Остановка

```bash
docker-compose stop mcp_server
# или
docker-compose down mcp_server
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/tools` | Регистрация инструмента | ✅ |
| `GET` | `/api/v1/tools` | Список инструментов | ✅ |
| `POST` | `/api/v1/resources` | Добавление ресурса | ✅ |
| `GET` | `/api/v1/resources` | Список ресурсов | ✅ |
| `POST` | `/api/v1/prompts` | Добавление шаблона | ✅ |
| `GET` | `/api/v1/prompts` | Список шаблонов | ✅ |
| `POST` | `/api/v1/execute` | Выполнение инструмента | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8008/health

# Через Traefik
curl http://localhost/mcp-server/api/v1/tools

# Регистрация инструмента
curl -X POST http://localhost:8008/api/v1/tools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "code_analyzer",
    "description": "Анализ кода на Python",
    "parameters": ["code", "language"]
  }'
```

### Пример ответа

```json
{
  "tool_id": "tool-123",
  "name": "code_analyzer",
  "description": "Анализ кода на Python",
  "status": "registered",
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8008/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Аутентификация** — JWT через Auth Service
- [x] **Защита от инъекций** — санитизация кода и промптов

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
pytest apps/mcp_server/tests/ --cov=apps/mcp_server --cov-report=term-missing

# С HTML отчётом
pytest apps/mcp_server/tests/ --cov=apps/mcp_server --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 24/24 | ≥80% ✅ |
| **Business Logic Tests** | 24/24 | 100% ✅ |
| **Integration Tests** | 0/0 | N/A |
| **Total Coverage** | ~85% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic_features.py` | 8 | CRUD инструментов, ресурсы |
| **Бизнес-логика** | `test_server_impl.py` | 16 | Регистрация, выполнение, ошибки |

**Итого:** 24 теста, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
mcp>=0.1.0  # Model Context Protocol SDK
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### Внешние сервисы

- [x] **Auth Service** — аутентификация и JWT (опционально)
- [ ] **AI Agents** — агенты, использующие MCP
- [ ] **Knowledge Graph** — хранение контекста

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# AI Agent Configuration
AGENT_API_URL=http://localhost:8009/api

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
- **MCP metrics:** Количество инструментов, вызовов, время выполнения

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/mcp-server-ci.yml
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
        run: pytest apps/mcp_server/tests/
      - name: Run linters
        run: ruff check apps/mcp_server/
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
- **[Cognitive Agent]** — использует MCP для выполнения задач
- **[CodeAssistant]** — инструменты для анализа кода
- **[Knowledge Graph]** — хранение контекста

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Полная реализация MCP требует специфичной версии SDK | Open | Использовать упрощённую реализацию для тестирования |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 24 теста с 100% прохождением
- **Added:** Ядро MCP сервера (инструменты, ресурсы, промпты)
- **Added:** Регистрация и выполнение инструментов
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
