# 📦 Cache Manager (Adapter)

Адаптер для старого кода, использующего cache_manager.py

## 📚 Содержание

- [Назначение](#Назначение)
- [Использование](#Использование)
- [Миграция](#Миграция)

---

## 🎯 Назначение

Этот файл предоставляет обратную совместимость для кода, который импортирует `cache_manager` напрямую.

Все функциональности перенесены в модули `cache/`:

- `cache/cache_core.py` — Базовая логика кэширования
- `cache/cache_strategies.py` — Стратегии кэширования
- `cache/cache_validators.py` — Валидаторы кэша

---

## 🚀 Использование

### Старый код (работает через адаптер)

```python
from agents.cognitive_agent.common.cache_manager import CacheManager

cache_mgr = CacheManager()
project_cache = cache_mgr.get_project_cache()
project_cache.set("key", "value")
```

### Новый код (рекомендуется)

```python
from agents.cognitive_agent.common.cache import BaseCache, TTLCache

# Базовый кэш
cache = BaseCache(name="my_cache")
cache.set("key", "value")

# TTL кэш
ttl_cache = TTLCache(default_ttl=3600)
ttl_cache.set("key", "value")
```

---

## 📝 Миграция

### Шаг 1: Обновить импорты

**Старый импорт:**
```python
from agents.cognitive_agent.common.cache_manager import CacheManager
```

**Новый импорт:**
```python
from agents.cognitive_agent.common.cache import BaseCache, TTLCache, FileCache
```

### Шаг 2: Обновить код

**Старый код:**
```python
cache_mgr = CacheManager()
project_cache = cache_mgr.get_project_cache()
project_cache.set("key", "value")
```

**Новый код:**
```python
cache = BaseCache(name="project_cache")
cache.set("key", "value")
```

---

## 📊 Сравнение API

| Старое API | Новое API | Примечание |
|------------|-----------|------------|
| `CacheManager` | `BaseCache`, `TTLCache`, `FileCache` | Более гибкая архитектура |
| `cache_mgr.get_project_cache()` | `BaseCache(name="project_cache")` | Прямое создание кэша |
| `MemoryAwareCache` | `FileCache` | Файловый кэш |

---

## 🛡️ Обратная совместимость

Все существующие импорты через `cache_manager` продолжают работать:

```python
from agents.cognitive_agent.common.cache_manager import (
    CacheEntry,
    BaseCache,
    FileCache,
    TTLCache,
    cached,
    global_cache,
    CacheStrategy,
    LRUStrategy,
    FIFOStrategy,
    LFUStrategy,
    TTLStrategy,
    CacheStrategyFactory,
    CacheValidator,
    SizeValidator,
    TypeValidator,
    HashValidator,
    PatternValidator,
    FileValidator,
    CustomValidator,
    CacheValidatorFactory,
    default_validator
)
```

---

## 📚 См. также

- [Cache Module](cache/README.md)
- [Memory Manager](../memory_manager.py)
- [Utils](../utils.py)
