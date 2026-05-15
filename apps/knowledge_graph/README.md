# Knowledge Graph

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Система управления графом знаний для хранения и запроса сущностей и их взаимосвязей. Обеспечивает семантический поиск, отслеживание навыков и связей между компонентами портфолио.

### Ключевые возможности
- [x] Управление сущностями (CRUD)
- [x] Отслеживание отношений между сущностями
- [x] Выполнение запросов к графу
- [x] Фильтрация по типу сущностей/связей
- [x] Поиск соседних узлов (neighbors)

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker |
| **Зависимости** | Neo4j/NetworkX (опционально), Auth Service |
| **Порт (Internal)** | 8006 (внутри контейнера) |
| **Порт (External)** | 8006 |
| **Traefik Route** | `/knowledge-graph` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/knowledge-graph`)
         ▼
┌─────────────────┐
│  knowledge_graph │  Internal: 8006
│  (FastAPI)      │  External: 8006
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Neo4j/         │
│  NetworkX       │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/knowledge_graph

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8006

# 4. Открыть Swagger UI
# http://localhost:8006/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d knowledge_graph

# Проверить статус
docker-compose ps | grep knowledge_graph

# Просмотр логов
docker-compose logs -f knowledge_graph
```

### Остановка

```bash
docker-compose stop knowledge_graph
# или
docker-compose down knowledge_graph
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/entities` | Добавление сущности | ✅ |
| `GET` | `/api/v1/entities/{entity_id}` | Получение сущности | ✅ |
| `GET` | `/api/v1/entities/type/{entity_type}` | Поиск по типу | ✅ |
| `POST` | `/api/v1/relationships` | Добавление связи | ✅ |
| `GET` | `/api/v1/relationships/{source_id}` | Связи сущности | ✅ |
| `POST` | `/api/v1/query` | Выполнение запроса | ✅ |
| `GET` | `/api/v1/neighbors/{entity_id}` | Соседние узлы | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8006/health

# Через Traefik
curl http://localhost/knowledge-graph/api/v1/entities

# Добавление сущности
curl -X POST http://localhost:8006/api/v1/entities \
  -H "Content-Type: application/json" \
  -d '{
    "id": "skill-python",
    "type": "skill",
    "properties": {"level": "advanced", "years": 3}
  }'
```

### Пример ответа

```json
{
  "id": "skill-python",
  "type": "skill",
  "properties": {"level": "advanced", "years": 3},
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8006/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Защита от инъекций** — санитизация Cypher/GraphQL запросов
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
pytest apps/knowledge_graph/tests/ --cov=apps/knowledge_graph --cov-report=term-missing

# С HTML отчётом
pytest apps/knowledge_graph/tests/ --cov=apps/knowledge_graph --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 39/39 | ≥80% ✅ |
| **Business Logic Tests** | 24/24 | 100% ✅ |
| **Integration Tests** | 15/15 | ≥60% ✅ |
| **Total Coverage** | ~80% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 15 | CRUD, конфигурация, health checks |
| **Бизнес-логика** | `test_kg_business.py` | 24 | Entities, relationships, queries, neighbors |

**Итого:** 39 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
networkx>=3.0  # для графов в памяти
neo4j>=5.0.0  # опционально для production
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
- [ ] **Neo4j** — production графовая БД (опционально)
- [ ] **Career Development** — хранение навыков

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Graph Database (опционально)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password  # pragma: allowlist secret

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
- **Graph metrics:** Количество сущностей/связей, глубина графа

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/knowledge-graph-ci.yml
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
        run: pytest apps/knowledge_graph/tests/
      - name: Run linters
        run: ruff check apps/knowledge_graph/
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
- **[Career Development]** — хранение профилей навыков
- **[Job Automation Agent]** — поиск вакансий по навыкам
- **[Portfolio Organizer]** — сбор доказательств компетенций

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с Neo4j требует Docker-окружения | Open | Использовать NetworkX in-memory для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 39 тестов с 100% прохождением
- **Added:** Ядро графа знаний (entities, relationships, queries)
- **Added:** Поиск по типу и соседним узлам
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
