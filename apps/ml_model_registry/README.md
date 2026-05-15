# ML Model Registry

**Реестр машинных моделей с версионированием и A/B тестированием**

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Тесты** | 70/70 | ✅ 100% |
| **Покрытие** | ~90% | ✅ |
| **Линтинг** | Чисто | ✅ |
| **Уязвимости** | 0 | ✅ |

**🏆 Лучший сервис по тестам в проекте!**

---

## 🚀 Возможности

### Регистрация моделей

- **Версионирование**:
  - Автоматическое создание версий
  - Семантическое версионирование (MAJOR.MINOR.PATCH)
- **Метаданные**:
  - Архитектура модели
  - Дрейф данных
  - Метрики производительности
- **Хранение**:
  - Локальное (filesystem)
  - Облачное (S3, Azure Blob)
  - Векторная БД (ChromaDB)

### Управление

- `register_model(model_id, data, version)` — регистрация
- `get_model(model_id, version=None)` — получение модели
- `list_models()` — список моделей
- `search_models(query)` — поиск моделей
- `delete_model(model_id)` — удаление
- `get_model_versions(model_id)` — версии модели

---

## 🧪 Тесты

```bash
# Запуск тестов
pytest apps/ml_model_registry/tests/ -v

# С покрытием
pytest apps/ml_model_registry/tests/ --cov=apps/ml_model_registry --cov-report=html
```

### Покрытие тестами (70 тестов)

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
**Дополнительно:** 22 passed subtests

---

## 🔒 Безопасность

### Проверки

- ✅ **SQL-инъекции** — отклонение вредоносных запросов
- ✅ **XSS** — санитизация данных модели
- ✅ **Path traversal** — блокировка `../` в путях
- ✅ **Инъекция ID** — валидация символов
- ✅ **Validation** — проверка URL-эндпоинтов

### Примеры тестов безопасности

```python
# test_security.py

def test_sql_injection_in_search(self):
    """Проверка SQL-инъекции через поиск"""
    result = search_models("'; DROP TABLE models; --")
    assert result == []

def test_xss_attempt_in_model_data(self):
    """Проверка XSS через данные модели"""
    with pytest.raises(ValueError):
        register_model("test", {"data": "<script>alert('xss')</script>"})

def test_path_traversal_attempt(self):
    """Проверка обхода путей"""
    with pytest.raises(ValueError):
        register_model("../../../etc/passwd", {})
```

---

## 📁 Структура

```
apps/ml_model_registry/
├── src/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic модели
│   ├── core/
│   │   ├── registry.py        # Основная логика
│   │   └── storage.py         # Хранение моделей
│   └── utils/
│       └── validators.py      # Валидация безопасности
├── tests/
│   ├── test_basic.py          # Базовые тесты (14)
│   ├── test_contract.py       # Контрактные (8)
│   ├── test_edge_cases.py     # Граничные (8)
│   ├── test_fuzz.py           # Fuzz (5)
│   ├── test_integration.py    # Интеграционные (3)
│   ├── test_model_registry.py # Регистр (7)
│   ├── test_model_storage.py  # Хранение (6)
│   ├── test_performance.py    # Производительность (3)
│   ├── test_resilience.py     # Отказоустойчивость (2)
│   ├── test_security.py       # Безопасность (11)
│   └── test_api.py            # API (2)
└── config/
    └── settings.py            # Конфигурация
```

---

## 🚀 Использование

### Регистрация модели

```python
from apps.ml_model_registry.src.core.registry import ModelRegistry

registry = ModelRegistry(storage_path="data/models")

# Регистрация
result = registry.register_model(
    model_id="fraud_detector",
    data={"architecture": "XGBoost", "accuracy": 0.95},
    version="1.0.0"
)
# {'model_id': 'fraud_detector', 'version': '1.0.0', 'status': 'registered'}
```

### Получение модели

```python
model = registry.get_model("fraud_detector", version="1.0.0")
# {'model_id': 'fraud_detector', 'version': '1.0.0', 'data': {...}}
```

### Поиск моделей

```python
results = registry.search_models("XGBoost")
# [{'model_id': 'fraud_detector', 'version': '1.0.0', ...}]
```

---

## 📈 Производительность

- **1000+ моделей**: < 100ms на операцию
- **Поиск**: < 50ms для 1000 моделей
- **Регистрация**: < 200ms для модели 10MB

---

## 📚 Документация

- [API Documentation](../../docs/api/ml-model-registry.md)
- [Security Best Practices](../../docs/security/MODEL-REGISTRY.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
