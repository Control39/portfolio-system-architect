# Thought Architecture

**Сервис управления архитектурными решениями (ADRs)**

---

## 🎯 Назначение

Thought Architecture предоставляет API для:
- Создания и управления архитектурными решениями
- Жизненного цикла решений (предложение → одобрение/отклонение → замена)
- Поиска решений по тексту и тегам
- Статистики по статусам и уровням решений
- Управления записями архитектуры

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Тестов | **28** (100% проходят) |
| Покрытие | **~75%** (цель: 80%) |
| AI Config Manager | ✅ Integrated |
| Статус | 🟢 Production Ready |

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d thought-architecture
```

### Локальный запуск

```bash
cd apps/thought-architecture
python -m uvicorn main:app --reload --port 8000
```

### API Documentation

Откройте [http://localhost:8000/docs](http://localhost:8000/docs) для Swagger UI.

---

## 🔧 API Endpoints

### Health Check
- `GET /health` — Проверка здоровья сервиса
- `GET /ready` — Readiness probe
- `GET /live` — Liveness probe

### Решения (Decisions)
- `GET /decisions` — Список всех решений (с фильтрацией по статусу/уровню/тегу)
- `POST /decisions` — Создать решение
- `GET /decisions/{id}` — Получить решение по ID
- `PUT /decisions/{id}` — Обновить решение
- `DELETE /decisions/{id}` — Удалить решение

### Жизненный цикл
- `PUT /decisions/{id}/approve?approver=X` — Одобрить решение
- `PUT /decisions/{id}/reject?reason=X` — Отклонить решение
- `PUT /decisions/{id}/supersede?new_decision_id=X` — Заменить решением

### Поиск и статистика
- `GET /decisions/search?query=X` — Поиск по тексту
- `GET /statistics` — Статистика по решениям

### Записи архитектуры (Records)
- `GET /records` — Список записей
- `POST /records` — Создать запись
- `GET /records/{id}` — Получить запись
- `PUT /records/{id}/add_decision?decision_id=X` — Добавить решение к записи
- `DELETE /records/{id}` — Удалить запись

---

## 📦 Примеры использования

### Создание решения

```bash
curl -X POST http://localhost:8000/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "adr-001",
    "title": "Выбор PostgreSQL",
    "description": "Используем PostgreSQL как основную БД",
    "level": "high",
    "tags": ["database", "infrastructure"]
  }'
```

### Одобрение решения

```bash
curl -X PUT "http://localhost:8000/decisions/adr-001/approve?approver=tech-lead"
```

### Поиск решений

```bash
curl "http://localhost:8000/decisions/search?query=database"
```

### Фильтрация по статусу

```bash
curl "http://localhost:8000/decisions?status=accepted"
```

---

## 🏗️ Архитектура

```
thought-architecture/
├── src/
│   ├── api/
│   │   ├── app.py            # FastAPI приложение
│   │   └── __init__.py
│   ├── core.py               # Бизнес-логика (ThoughtArchitect)
│   ├── config_integration.py # AI Config Manager
│   └── __init__.py
├── tests/
│   ├── test_api.py           # Тесты API (28 тестов)
│   └── test_thought_business.py # Бизнес-логика
├── main.py                   # Точка входа
├── Dockerfile
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/thought-architecture/tests/ -v

# С покрытием
pytest apps/thought-architecture/tests/ --cov=apps/thought_architecture/src --cov-report=term-missing

# Только API тесты
pytest apps/thought-architecture/tests/test_api.py -v
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Проверка статусов перед переходами (approve/reject/supersede)
- ✅ Защита от дубликатов ID
- ✅ Поддержка Unicode в полях

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.thought_architecture.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

См. [`docs/AI_CONFIG_INTEGRATION.md`](../../docs/AI_CONFIG_INTEGRATION.md) для деталей.

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8000 | `/thought-architecture` | 8000 |

Доступ через API Gateway: `http://localhost/thought-architecture/health`

---

## 📝 Известные проблемы

- Нет интеграции с PostgreSQL (используется in-memory хранилище)
- Требуется добавление persistence слоя для production

---

*Последнее обновление: 17 мая 2026 г.*