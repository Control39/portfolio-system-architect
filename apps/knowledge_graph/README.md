# Knowledge Graph

**Сервис управления графом знаний**

---

## 🎯 Назначение

Knowledge Graph предоставляет API для:
- Создания и управления сущностями графа
- Создания и управления отношениями между сущностями
- Графовых запросов (поиск соседей, фильтрация)
- Статистики графа

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Тестов | **24** (100% проходят) |
| Покрытие | **~75%** (цель: 80%) |
| AI Config Manager | ✅ Integrated |
| Статус | 🟢 Production Ready |

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d knowledge-graph
```

### Локальный запуск

```bash
cd apps/knowledge_graph
python -m uvicorn src.api.main:app --reload --port 8000
```

### API Documentation

Откройте [http://localhost:8000/docs](http://localhost:8000/docs) для Swagger UI.

---

## 🔧 API Endpoints

### Health Check
- `GET /health` — Проверка здоровья сервиса
- `GET /ready` — Readiness probe
- `GET /live` — Liveness probe

### Сущности
- `GET /entities` — Список всех сущностей
- `POST /entities` — Создать сущность
- `GET /entities/{id}` — Получить сущность
- `PUT /entities/{id}` — Обновить сущность
- `DELETE /entities/{id}` — Удалить сущность (каскадно удаляет отношения)

### Отношения
- `GET /relationships` — Список всех отношений
- `POST /relationships` — Создать отношение
- `GET /relationships/{id}` — Получить отношение
- `DELETE /relationships/{id}` — Удалить отношение

### Графовые запросы
- `GET /entities/{id}/neighbors` — Получить соседей сущности
- `GET /query?entity_type=X&relationship_type=Y` — Выполнить графовый запрос

### Статистика
- `GET /statistics` — Статистика графа (сущности, отношения, типы)

---

## 📦 Примеры использования

### Создание сущности

```bash
curl -X POST http://localhost:8000/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "user-001",
    "entity_type": "person",
    "properties": {"name": "Alice", "age": 30}
  }'
```

### Создание отношения

```bash
curl -X POST http://localhost:8000/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "relationship_id": "rel-001",
    "source_entity": "user-001",
    "target_entity": "company-001",
    "relationship_type": "works_at",
    "properties": {"since": "2020"}
  }'
```

### Поиск соседей

```bash
curl http://localhost:8000/entities/user-001/neighbors
```

### Графовый запрос

```bash
curl "http://localhost:8000/query?entity_type=person&relationship_type=works_at"
```

---

## 🏗️ Архитектура

```
knowledge_graph/
├── src/
│   ├── api/
│   │   ├── main.py           # FastAPI приложение
│   │   └── __init__.py
│   ├── core/
│   │   └── knowledge_graph.py # Ядро графа (бизнес-логика)
│   ├── config_integration.py  # AI Config Manager
│   └── __init__.py
├── tests/
│   ├── test_api.py           # Тесты API (24 теста)
│   ├── test_kg_basic.py      # Базовые тесты
│   └── test_kg_business.py   # Бизнес-логика
├── Dockerfile
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/knowledge_graph/tests/ -v

# С покрытием
pytest apps/knowledge_graph/tests/ --cov=apps/knowledge_graph/src --cov-report=term-missing

# Только API тесты
pytest apps/knowledge_graph/tests/test_api.py -v
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Проверка существования сущностей перед созданием отношений
- ✅ Каскадное удаление отношений при удалении сущностей
- ✅ Защита от дубликатов ID
- ✅ Поддержка Unicode в свойствах

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.knowledge_graph.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

См. [`docs/AI_CONFIG_INTEGRATION.md`](../../docs/AI_CONFIG_INTEGRATION.md) для деталей.

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8000 | `/knowledge-graph` | 8000 |

Доступ через API Gateway: `http://localhost/knowledge-graph/health`

---

## 📝 Известные проблемы

- Нет интеграции с Neo4j/другой графовой БД (используется in-memory хранилище)
- Требуется добавление persistence слоя для production

---

*Последнее обновление: 17 мая 2026 г.*