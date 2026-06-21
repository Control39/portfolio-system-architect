# 📁 Directory common for Cognitive Agent

Эта директория содержит общие утилиты и базовые классы, используемые в различных компонентах Cognitive Agent.

## 🗂️ Структура

### Core Modules

- [cache/](./cache/) - Модуль кэширования
  - [cache_core.py](./cache/cache_core.py) - Базовая логика кэширования
  - [cache_strategies.py](./cache/cache_strategies.py) - Стратегии кэширования (LRU, FIFO, LFU)
  - [cache_validators.py](./cache/cache_validators.py) - Валидаторы кэша
  - [README.md](./cache/README.md) - Документация модуля кэширования
- [cache_manager.py](./cache_manager.py) - Адаптер для старого кода (обратная совместимость)

### Base Components

- [base_agent_extensions.py](./base_agent_extensions.py) - Расширения базового класса агента
- [base_logger.py](./base_logger.py) - Базовый класс логгера
- [base_scanner.py](./base_scanner.py) - Базовый класс сканера
- [base_security.py](./base_security.py) - Базовые функции безопасности

### Utilities

- [exceptions.py](./exceptions.py) - Общие исключения агента
- [memory_manager.py](./memory_manager.py) - Менеджер памяти и состояния
- [pattern_analyzer.py](./pattern_analyzer.py) - Анализатор паттернов в коде
- [utils.py](./utils.py) - Вспомогательные утилиты

---

## 🏗️ Основные компоненты

### Менеджеры

- **Cache Manager** ([cache/](./cache/), [cache_manager.py](./cache_manager.py)) - Управляет кэшированием данных и результатов анализа
  - [BaseCache](./cache/cache_core.py) - Базовый класс кэша
  - [FileCache](./cache/cache_core.py) - Файловый кэш
  - [TTLCache](./cache/cache_core.py) - Кэш с Time-To-Live
  - [cached](./cache/cache_core.py) - Декоратор для кэширования функций

- **Memory Manager** ([memory_manager.py](./memory_manager.py)) - Управляет состоянием агента и историей решений

- **Pattern Analyzer** ([pattern_analyzer.py](./pattern_analyzer.py)) - Анализирует паттерны в коде и архитектуре

### Базовые классы

- **Base Logger** ([base_logger.py](./base_logger.py)) - Обеспечивает структурированное логирование
- **Base Scanner** ([base_scanner.py](./base_scanner.py)) - Базовая функциональность для сканирования
- **Base Security** ([base_security.py](./base_security.py)) - Обеспечивает безопасность выполнения операций

### Исключения

- **Exceptions** ([exceptions.py](./exceptions.py)) - Иерархия исключений агента
  - `CognitiveAgentError` - Базовое исключение
  - `ConfigurationError` - Ошибка конфигурации
  - `SecurityViolationError` - Нарушение безопасности
  - `ResourceExhaustionError` - Исчерпание ресурсов
  - `AIServiceError` - Ошибка сервиса ИИ
  - `FileOperationError` - Ошибка операции с файлами
  - `NetworkError` - Ошибка сети
  - `ValidationError` - Ошибка валидации данных
  - `TaskExecutionError` - Ошибка выполнения задачи
  - `IntegrationError` - Ошибка интеграции с внешними системами
  - `AgentStateError` - Ошибка состояния агента
  - `DataProcessingError` - Ошибка обработки данных
  - `CacheError` - Ошибка кэширования
  - `AuditLogError` - Ошибка аудит-логирования
  - `ErrorHandler` - Централизованный обработчик ошибок

---

## 🚀 Использование

### Импорт компонентов

```python
# Импорт модуля кэширования
from agents.cognitive_agent.common.cache import BaseCache, TTLCache, FileCache

# Импорт базовых классов
from agents.cognitive_agent.common.base_logger import BaseLogger
from agents.cognitive_agent.common.base_scanner import BaseScanner
from agents.cognitive_agent.common.base_security import BaseSecurity

# Импорт исключений
from agents.cognitive_agent.common.exceptions import (
    CognitiveAgentError,
    ConfigurationError,
    SecurityViolationError
)

# Импорт утилит
from agents.cognitive_agent.common.utils import calculate_file_hash, load_json_file
```

### Обработка ошибок

```python
from agents.cognitive_agent.common.exceptions import ErrorHandler, ConfigurationError

# Создать обработчик ошибок
error_handler = ErrorHandler()

# Обработать ошибку
try:
    raise ConfigurationError("Invalid configuration")
except Exception as e:
    error_info = error_handler.handle_error(e)
    print(error_info)
```

### Кэширование

```python
from agents.cognitive_agent.common.cache import TTLCache

# Создать TTL кэш
cache = TTLCache(default_ttl=3600)  # 1 час

# Установить значение
cache.set("key", "value")

# Получить значение
value = cache.get("key")
```

---

## 📊 Миграция к новой архитектуре

### Старая структура

```python
from agents.cognitive_agent.common.cache_manager import CacheManager

cache_mgr = CacheManager()
project_cache = cache_mgr.get_project_cache()
```

### Новая структура

```python
from agents.cognitive_agent.common.cache import BaseCache, TTLCache

# Прямое создание кэша
cache = BaseCache(name="project_cache")
```

---

## 📚 См. также

- [Core Module](../core/)
- [Modules](../modules/)
- [Src Module](../src/)
- [Metacognitive Control](../metacognitive_control/)
- [Knowledge Graph](../knowledge_graph/)
- [Security](../security/)

---

**Обновлено:** 2026-06-19
**Автор:** GigaCode
**Статус:** Phase 1 in progress
