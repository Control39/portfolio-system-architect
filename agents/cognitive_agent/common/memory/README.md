# Cognitive Agent Memory Module

## Описание

Модуль памяти для Cognitive Agent предоставляет различные типы памяти для хранения и управления информацией. Система поддерживает краткосрочную, долгосрочную и рабочую память с возможностью настройки стратегий управления и валидации.

## Архитектура

```
common/memory/
├── memory_core.py      # Базовые классы памяти
├── memory_strategies.py # Стратегии управления памятью
├── memory_validators.py # Валидаторы памяти
└── README.md           # Документация
```

## Базовые компоненты

### MemoryEntry

Запись в памяти с поддержкой TTL, приоритетов и тегов.

```python
class MemoryEntry:
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None,
                 priority: int = 0, tags: List[str] = None):
        """
        Args:
            key: Ключ записи
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
            priority: Приоритет записи (0 = низкий, 10 = высокий)
            tags: Теги для фильтрации
        """
```

**Методы:**
- `is_expired() -> bool` — Проверка истечения срока действия
- `matches_tags(tags: List[str]) -> bool` — Проверка соответствия тегам
- `to_dict() -> Dict[str, Any]` — Преобразование в словарь
- `from_dict(data: Dict[str, Any]) -> MemoryEntry` — Создание из словаря

### BaseMemory

Базовый класс памяти с общим интерфейсом.

```python
class BaseMemory:
    def __init__(self, name: str = "base_memory"):
        """
        Args:
            name: Имя памяти для логирования
        """
```

**Методы:**
- `get(key: str) -> Optional[Any]` — Получение значения по ключу
- `set(key: str, value: Any, ttl: Optional[int] = None, priority: int = 0, tags: List[str] = None) -> None` — Установка значения
- `delete(key: str) -> bool` — Удаление записи
- `clear() -> None` — Очистка всей памяти
- `size() -> int` — Размер памяти
- `keys() -> list` — Получение всех ключей
- `get_by_tags(tags: List[str]) -> Dict[str, Any]` — Получение по тегам
- `get_by_priority(min_priority: int = 0) -> Dict[str, Any]` — Получение по приоритету

## Типы памяти

### ShortTermMemory

Краткосрочная память с автоматическим TTL.

```python
class ShortTermMemory(BaseMemory):
    def __init__(self, default_ttl: int = 300, name: str = "short_term_memory"):
        """
        Args:
            default_ttl: Время жизни по умолчанию в секундах (5 минут)
        """
```

**Особенности:**
- Автоматическое установление TTL при создании записи
- Значение TTL по умолчанию: 300 секунд (5 минут)

### LongTermMemory

Долгосрочная память с поддержкой приоритетов.

```python
class LongTermMemory(BaseMemory):
    def __init__(self, name: str = "long_term_memory"):
        """
        Args:
            name: Имя памяти для логирования
        """
```

**Методы:**
- `get_highest_priority() -> Optional[Any]` — Получение значения с самым высоким приоритетом
- `cleanup_expired() -> int` — Очистка истекших записей

**Особенности:**
- Поддержка приоритетов записей
- Эффективная очистка истекших записей

### WorkingMemory

Рабочая память с ограничением по размеру.

```python
class WorkingMemory(BaseMemory):
    def __init__(self, max_size: int = 100, name: str = "working_memory"):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

**Методы:**
- `get_lru_key() -> Optional[str]` — Получение ключа наименее недавно используемой записи
- `_evict_lru() -> Optional[str]` — Извлечение LRU записи

**Особенности:**
- Ограничение размера (по умолчанию: 100 записей)
- Автоматическое извлечение LRU записей при превышении лимита

### MemoryManager

Менеджер памяти для всего агента.

```python
class MemoryManager:
    def __init__(self, logger=None):
        """
        Args:
            logger: Логгер для записи событий
        """
```

**Методы:**
- `get(key: str) -> Optional[Any]` — Получение значения из любой памяти
- `set(key: str, value: Any, ttl: Optional[int] = None, priority: int = 0, tags: List[str] = None, memory_type: str = "short_term") -> bool` — Установка значения
- `cleanup() -> Dict[str, int]` — Очистка истекших записей
- `get_stats() -> Dict[str, Any]` — Получение статистики

**Особенности:**
- Управление всеми типами памяти
- Автоматический поиск в всех типах памяти
- Централизованная статистика

## Стратегии управления

### LRUMemoryStrategy

LRU (Least Recently Used) стратегия — извлекает наименее недавно используемые записи.

```python
class LRUMemoryStrategy(MemoryStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### FIFOMemoryStrategy

FIFO (First In, First Out) стратегия — извлекает самые старые записи.

```python
class FIFOMemoryStrategy(MemoryStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### LFUMemoryStrategy

LFU (Least Frequently Used) стратегия — извлекает наименее часто используемые записи.

```python
class LFUMemoryStrategy(MemoryStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### PriorityMemoryStrategy

Стратегия с приоритетами — извлекает записи с самым низким приоритетом.

```python
class PriorityMemoryStrategy(MemoryStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

**Методы:**
- `set_priority(key: str, priority: int) -> None` — Установка приоритета
- `get_priority(key: str) -> int` — Получение приоритета
- `get_lowest_priority_key() -> Optional[str]` — Получение ключа с самым низким приоритетом

### MemoryStrategyFactory

Фабрика стратегий управления памятью.

```python
class MemoryStrategyFactory:
    @classmethod
    def create(cls, strategy_name: str, **kwargs) -> MemoryStrategy:
        """
        Args:
            strategy_name: Имя стратегии (lru, fifo, lfu, priority)
            **kwargs: Аргументы для конструктора стратегии
        """

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Получить список доступных стратегий"""
```

## Валидаторы

### SizeValidator

Валидатор размера значения.

```python
class SizeValidator(MemoryValidator):
    def __init__(self, max_size: int = 1024 * 1024, min_size: int = 0):
        """
        Args:
            max_size: Максимальный размер в байтах
            min_size: Минимальный размер в байтах
        """
```

### TypeValidator

Валидатор типа значения.

```python
class TypeValidator(MemoryValidator):
    def __init__(self, allowed_types: List[type] = None):
        """
        Args:
            allowed_types: Список разрешенных типов
        """
```

### PatternValidator

Валидатор ключа по паттерну.

```python
class PatternValidator(MemoryValidator):
    def __init__(self, pattern: str = r"^[a-zA-Z][a-zA-Z0-9_]*$"):
        """
        Args:
            pattern: Регулярное выражение для ключа
        """
```

### CustomValidator

Пользовательский валидатор.

```python
class CustomValidator(MemoryValidator):
    def __init__(self, validate_func: Callable[[str, Any], bool], name: str = "custom"):
        """
        Args:
            validate_func: Функция валидации
            name: Имя валидатора
        """
```

### MemoryValidatorFactory

Фабрика валидаторов памяти.

```python
class MemoryValidatorFactory:
    @classmethod
    def create(cls, validator_name: str, **kwargs) -> MemoryValidator:
        """
        Args:
            validator_name: Имя валидатора
            **kwargs: Аргументы для конструктора
        """

    @classmethod
    def get_available_validators(cls) -> List[str]:
        """Получить список доступных валидаторов"""
```

### MemoryValidatorChain

Цепочка валидаторов.

```python
class MemoryValidatorChain:
    def __init__(self):
        """Инициализация цепочки валидаторов"""

    def add(self, validator: MemoryValidator) -> 'MemoryValidatorChain':
        """Добавить валидатор в цепочку"""

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать через цепочку"""

    def get_first_error(self) -> Optional[str]:
        """Получить первое сообщение об ошибке"""

    def validate_all(self, entries: Dict[str, Any]) -> Dict[str, bool]:
        """Валидировать несколько записей"""
```

## Примеры использования

### Создание и использование памяти

```python
from common.memory import ShortTermMemory, LongTermMemory, WorkingMemory

# Краткосрочная память
short_term = ShortTermMemory(default_ttl=300)
short_term.set("key1", "value1")
short_term.set("key2", "value2", ttl=600)

# Долгосрочная память
long_term = LongTermMemory()
long_term.set("key1", "value1", priority=5)
long_term.set("key2", "value2", priority=10)

# Рабочая память
working = WorkingMemory(max_size=100)
working.set("key1", "value1")
```

### Использование MemoryManager

```python
from common.memory import MemoryManager

manager = MemoryManager()

# Установка значения
manager.set("key", "value", memory_type="short_term")
manager.set("key", "value", memory_type="long_term")
manager.set("key", "value", memory_type="working")

# Получение значения
value = manager.get("key")  # Автоматически ищет во всех типах памяти

# Получение статистики
stats = manager.get_stats()
```

### Использование стратегий

```python
from common.memory import LRUMemoryStrategy, MemoryStrategyFactory

# Создание стратегии через фабрику
strategy = MemoryStrategyFactory.create("lru", max_size=100)

# Использование стратегии
strategy.on_add("key1", "value1")
strategy.on_access("key1", "value1")
strategy.on_remove("key1")

# Получение ключа для извлечения
key_to_evict = strategy.should_evict(memory_size=101, max_size=100)
```

### Использование валидаторов

```python
from common.memory import (
    SizeValidator,
    TypeValidator,
    PatternValidator,
    MemoryValidatorChain
)

# Создание цепочки валидаторов
chain = MemoryValidatorChain()
chain.add(SizeValidator(max_size=1024))
chain.add(TypeValidator(allowed_types=[str, int]))
chain.add(PatternValidator())

# Валидация
is_valid = chain.validate("key", "value")

# Валидация нескольких записей
entries = {"key1": "value1", "key2": "value2"}
results = chain.validate_all(entries)
```

## Архитектура "Core + Modules + Orchestrator"

### Core
- `memory_core.py` — Базовые абстракции (MemoryEntry, BaseMemory)

### Modules
- `memory_strategies.py` — Стратегии управления памятью
- `memory_validators.py` — Валидаторы памяти

### Orchestrator
- `MemoryManager` — Центральное управление памятью

## Миграция со старой версии

### Старый код (memory_manager.py)

```python
from common.memory_manager import MemoryManager

manager = MemoryManager()
manager.cache("key", "value", ttl=300)
```

### Новый код (common/memory/)

```python
from common.memory import MemoryManager

manager = MemoryManager()
manager.set("key", "value", ttl=300, memory_type="short_term")
```

## Зависимости

- `typing` — Типизация
- `abc` — Абстрактные базовые классы
- `re` — Регулярные выражения

## Логирование

Все модули используют стандартный модуль `logging` для записи событий.

```python
import logging

logger = logging.getLogger(__name__)
```

## Примечания

- Все TTL указаны в секундах
- Приоритеты записей: 0 (низкий) - 10 (высокий)
- По умолчанию рабочая память имеет размер 100 записей
- Краткосрочная память имеет TTL по умолчанию 300 секунд (5 минут)
- Долгосрочная память не имеет TTL по умолчанию (бесконечно)
