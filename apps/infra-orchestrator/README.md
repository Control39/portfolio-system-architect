# Infra Orchestrator

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Система оркестрации и управления инфраструктурой микросервисов. Обеспечивает полный жизненный цикл сервисов: регистрация, развёртывание, масштабирование, остановка и rollback с поддержкой multi-cluster.

### Ключевые возможности
- [x] Жизненный цикл сервисов (register, deploy, stop, scale)
- [x] Поддержка нескольких кластеров (multi-cluster)
- [x] Health checks и мониторинг состояния
- [x] Автоматическое и ручное масштабирование
- [x] История развёртываний с возможностью rollback

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker, Kubernetes (опционально) |
| **Зависимости** | Auth Service, Kubernetes client (опционально) |
| **Порт (Internal)** | 8007 (внутри контейнера) |
| **Порт (External)** | 8007 |
| **Traefik Route** | `/infra-orchestrator` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/infra-orchestrator`)
         ▼
┌─────────────────┐
│  infra-orchestrator │  Internal: 8007
│  (FastAPI)      │  External: 8007
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kubernetes /   │
│  Docker Compose │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/infra-orchestrator

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8007

# 4. Открыть Swagger UI
# http://localhost:8007/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d infra-orchestrator

# Проверить статус
docker-compose ps | grep infra-orchestrator

# Просмотр логов
docker-compose logs -f infra-orchestrator
```

### Остановка

```bash
docker-compose stop infra-orchestrator
# или
docker-compose down infra-orchestrator
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/api/v1/services` | Регистрация сервиса | ✅ |
| `GET` | `/api/v1/services` | Список сервисов | ✅ |
| `GET` | `/api/v1/services/{id}` | Информация о сервисе | ✅ |
| `POST` | `/api/v1/services/{id}/deploy` | Развёртывание | ✅ |
| `POST` | `/api/v1/services/{id}/stop` | Остановка | ✅ |
| `POST` | `/api/v1/services/{id}/scale` | Масштабирование | ✅ |
| `GET` | `/api/v1/services/{id}/history` | История развёртываний | ✅ |
| `POST` | `/api/v1/services/{id}/rollback` | Rollback | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8007/health

# Через Traefik
curl http://localhost/infra-orchestrator/api/v1/services

# Регистрация сервиса
curl -X POST http://localhost:8007/api/v1/services \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "payment-service",
    "service_type": "api",
    "cluster": "prod-us-east-1",
    "replicas": 3
  }'
```

### Пример ответа

```json
{
  "service_id": "svc-123",
  "service_name": "payment-service",
  "status": "deploying",
  "cluster": "prod-us-east-1",
  "replicas": 3,
  "created_at": "2026-05-15T10:30:00Z"
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8007/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Аутентификация** — JWT через Auth Service
- [x] **RBAC** — контроль доступа к операциям оркестрации

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
pytest apps/infra-orchestrator/tests/ --cov=apps/infra-orchestrator --cov-report=term-missing

# С HTML отчётом
pytest apps/infra-orchestrator/tests/ --cov=apps/infra-orchestrator --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 58/58 | ≥80% ✅ |
| **Business Logic Tests** | 55/55 | 100% ✅ |
| **Integration Tests** | 3/3 | ≥60% ✅ |
| **Total Coverage** | ~90% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 3 | Конфигурация, health checks |
| **Бизнес-логика** | `test_orchestrator_business.py` | 55 | Lifecycle, scaling, history, multi-cluster |

**Итого:** 58 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
kubernetes>=28.0.0  # опционально для Kubernetes
docker>=6.0.0  # опционально для Docker API
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
- [ ] **Kubernetes API** — production оркестрация (опционально)
- [ ] **Docker API** — локальная оркестрация (опционально)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Kubernetes (опционально)
KUBERNETES_API_URL=https://k8s-api.example.com:6443
KUBERNETES_TOKEN=your-token  # pragma: allowlist secret
KUBERNETES_CA_CERT=/path/to/ca.crt

# Docker (опционально)
DOCKER_HOST=unix:///var/run/docker.sock

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
- **Orchestration metrics:** Количество сервисов, статусы, история развёртываний

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/infra-orchestrator-ci.yml
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
        run: pytest apps/infra-orchestrator/tests/
      - name: Run linters
        run: ruff check apps/infra-orchestrator/
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
- **Все микросервисы** — управляются оркестратором
- **[Deployment]** — Kubernetes манифесты и GitOps

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с Kubernetes требует доступа к API | Open | Использовать Docker mode для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 58 тестов с 100% прохождением
- **Added:** Ядро оркестратора (ServiceConfig, ServiceInstance, InfrastructureOrchestrator)
- **Added:** Полный жизненный цикл сервисов
- **Added:** Multi-cluster поддержка
- **Added:** История развёртываний и rollback
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
