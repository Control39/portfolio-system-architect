# Decision Engine

> **Статус:** MVP
> **Порт:** 8001
> **Маршрут:** `/decision-engine`

---

## 🎯 Назначение

AI-driven система принятия решений с RAG (Retrieval-Augmented Generation) и объяснимой логикой reasoning.

---

## 🏗️ Архитектура

### Технологии
- **Язык:** Python 3.10+
- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL 16, ChromaDB (векторная)
- **Контейнеризация:** Docker + Docker Compose

### Зависимости
- **PostgreSQL 16** — основная БД
- **ChromaDB** — векторный поиск
- **Traefik** — API шлюз

### Структура
```
decision_engine/
├── src/
│   ├── api/          # API эндпоинты
│   ├── core/         # Бизнес-логика (reasoning engine)
│   └── models/       # Pydantic модели
├── tests/            # 50 тестов (100% покрытие)
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start

### Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск только decision-engine
docker-compose up -d decision-engine

# Проверка состояния
docker-compose ps
```

### Локальный запуск (для разработки)

```bash
# Активация виртуального окружения
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn src.main:app --reload --port 8001
```

### Доступ к сервису

- **Через Traefik:** `http://localhost/decision-engine`
- **Прямой доступ:** `http://localhost:8001`
- **API Documentation:** `http://localhost:8001/docs` (Swagger UI)

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| GET   | `/health` | Health check | ❌ |
| GET   | `/ready`  | Readiness check | ❌ |
| GET   | `/api/v1/status` | Статус сервиса | ❌ |
| POST  | `/api/v1/decide` | Принятие решения | ✅ |
| POST  | `/api/v1/reason` | Reasoning с объяснением | ✅ |

### Примеры запросов

#### Health Check
```bash
curl http://localhost:8001/api/v1/status
# {"status": "healthy", "service": "decision-engine"}
```

#### Принятие решения
```bash
curl -X POST http://localhost:8001/api/v1/decide \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какой фреймворк выбрать для проекта?",
    "context": ["FastAPI", "Django", "Flask"]
  }'
```

#### Reasoning с объяснением
```bash
curl -X POST http://localhost:8001/api/v1/reason \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Почему FastAPI лучше Flask для микросервисов?",
    "depth": "detailed"
  }'
```

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — секреты не логируются
- [x] **Валидация входных данных** — Pydantic модели для всех запросов
- [ ] **Защита от SSRF** — валидация URL (планируется)
- [x] **JWT аутентификация** — интеграция с `auth_service`
- [ ] **Rate Limiting** — ограничение через Traefik

### Аутентификация

- **Метод:** JWT
- **Интеграция:** `auth_service`
- **Роли:** admin, user, service

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты с покрытием
pytest tests/ --cov=. --cov-report=term-missing

# Конкретный файл
pytest tests/test_endpoints.py -v

# Сгенерировать HTML отчёт
pytest tests/ --cov=. --cov-report=html
# Открыть: htmlcov/index.html
```

### Покрытие кода

| Модуль | Покрытие | Статус |
|--------|----------|--------|
| `api/` | ~90% | ✅ |
| `core/` | ~80% | ✅ |
| **Всего** | **~85%** | **✅** |

**Цель:** ≥80% покрытие для production-ready сервисов

### Типы тестов

- **Юнит-тесты** — изолированное тестирование функций (35 тестов)
- **Интеграционные тесты** — тестирование API эндпоинтов (10 тестов)
- **E2E тесты** — полные сценарии reasoning (5 тестов)

---

## 📊 Мониторинг

### Метрики

- **Prometheus:** `http://localhost:9090/targets`
- **Grafana:** `http://localhost:3000` (дашборд Decision Engine)

### Логи

```bash
# Логи сервиса
docker-compose logs -f decision-engine

# Логи с временными метками
docker-compose logs -f --tail=100 decision-engine
```

### Health Check

```bash
curl http://localhost:8001/api/v1/status
# {"status": "healthy", "service": "decision-engine", "rag_index": "ready"}
```

---

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию | Обязательная |
|------------|----------|----------------------|--------------|
| `LOG_LEVEL` | Уровень логирования | `INFO` | ❌ |
| `DATABASE_URL` | URL базы данных | - | ✅ |
| `RAG_INDEX_PATH` | Путь к векторной БД | `./data/rag-index` | ❌ |
| `JWT_SECRET` | Секрет для JWT | `dev-secret` | ✅ |

### Пример `.env`

```bash
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://user:pass@postgres:5432/decision_engine  # pragma: allowlist secret
RAG_INDEX_PATH=./data/rag-index
JWT_SECRET=your-production-secret-here  # pragma: allowlist secret
```

---

## 📝 История изменений

| Версия | Дата | Изменения | Автор |
|--------|------|-----------|-------|
| 0.1.0 | 2026-05-15 | Initial MVP (50 тестов, 85% покрытие) | [YourName] |
| | | | |

---

## 🤝 Вклад

См. [CONTRIBUTING.md](../../CONTRIBUTING.md) для правил контрибуции.

### Задачи для контрибьюторов

- [ ] Добавить защиту от SSRF
- [ ] Реализовать rate limiting
- [ ] Улучшить coverage до 90%
- [ ] Добавить E2E тесты для сложных reasoning-сценариев

---

## 📚 Дополнительные ресурсы

- [Архитектура проекта](../../ARCHITECTURE.md)
- [Быстрый старт](../../QUICK_START.md)
- [Безопасность](../../SECURITY.md)
- [CI/CD workflows](../../.github/workflows/README.md)

---

## 🐛 Известные проблемы

См. [KNOWN_ISSUES.md](../../docs/KNOWN_ISSUES.md) для списка известных проблем.

---

*Документ сгенерирован автоматически. Последнее обновление: 15 мая 2026 г.*
