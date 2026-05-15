# Knowledge Graph

**Knowledge graph management and query system**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 39/39 | ✅ 100% |
| **Покрытие** | ~80% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

---

## 🚀 Возможности

- **Entity Management** — добавление и поиск сущностей
- **Relationship Tracking** — управление связями между сущностями
- **Graph Queries** — выполнение запросов к графу
- **Type-based Filtering** — фильтрация по типу сущностей/связей
- **Neighbor Discovery** — поиск соседних узлов
- **API endpoints**:
  - `POST /entities` — добавление сущности
  - `POST /relationships` — добавление связи
  - `GET /entities/{type}` — поиск по типу
  - `POST /query` — выполнение запроса
  - `GET /health` — health check

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/knowledge_graph/tests/ -v

# С покрытием
pytest apps/knowledge_graph/tests/ --cov=apps/knowledge_graph --cov-report=html
```

### Ключевые тесты
- **39 тестов** (15 базовых + 24 бизнес-логики)
- Покрытие: CRUD сущностей, связи, запросы, граничные случаи

---

**Last Updated**: 2026-05-15
**Status**: 🟢 Production Ready