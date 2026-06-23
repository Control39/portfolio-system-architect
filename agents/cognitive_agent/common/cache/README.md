# Cognitive Agent Cache Module

## Описание

Модуль кэширования для Cognitive Agent предоставляет различные типы кэшей для хранения и управления временными данными. Система поддерживает TTL (Time-to-Live), стратегии управления, валидаторы и файловое хранение.

## Архитектура

```
common/cache/
├── cache_core.py      # Базовые классы кэша
├── cache_strategies.py # Стратегии управления кэшем
├── cache_validators.py # Валидаторы кэша
└── README.md           # Документация
```

## Базовые компоненты

### CacheEntry

Запись в кэше с поддержкой TTL.

```python
class CacheEntry:
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Args:
            key: Ключ записи
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
        """
```

**Методы:**
- `is_expired() -> bool` — Проверка истечения срока действия
- `to_dict() -> Dict[str, Any]` — Преобразование в словарь
- `from_dict(data: Dict[str, Any]) -> CacheEntry` — Создание из словаря

### BaseCache

Базовый класс кэша с общим интерфейсом.

```python
class BaseCache:
    def __init__(self, name: str = \"base_cache\"):
        """
        Args:
            name: Имя кэша для логирования
        """
```

**Методы:**
- `get(key: str) -> Optional[Any]` — Получение значения по ключу
- `set(key: str, value: Any, ttl: Optional[int] = None) -> None` — Установка значения
- `delete(key: str) -> bool` — Удаление записи
- `clear() -> None` — Очистка всего кэша
- `size() -> int` — Размер кэша
- `keys() -> list` — Получение всех ключей
- `__contains__(key: str) -> bool` — Проверка наличия ключа
- `__len__() -> int` — Размер кэша

## Типы кэшей

### FileCache

Файловый кэш с сохранением в файлы.

```python
class FileCache(BaseCache):
    def __init__(self, cache_dir: Path, name: str = \"file_cache\"):
        """
        Args:
            cache_dir: Директория для хранения кэша
        """
```

**Методы:**
- `_get_file_path(key: str) -> Path` — Получить путь к файлу для ключа
- `_save_to_file(key: str) -> None` — Сохранить запись в файл
- `_load_from_file(key: str) -> Optional[CacheEntry]` — Загрузить запись из файла
- `_load_from_files() -> None` — Загрузить все записи из файлов

**Особенности:**
- Автоматическое сохранение и загрузка из JSON файлов
- Хэширование ключей для имен файлов
- Поддержка перезапуска п��иложения (данные сохраняются)

### TTLCache

Кэш с TTL для всех записей.

```python
class TTLCache(BaseCache):
    def __init__(self, default_ttl: int = 3600, name: str = \"ttl_cache\"):
        """
        Args:
            default_ttl: Время жизни по умолчанию в секундах (1 час)
        """
```

**Методы:**
- `cleanup() -> int` — Очистить истекшие записи (возвращает количество удаленных)

**Особенности:**
- Установка TTL по умолчанию для всех записей
- Автоматическая очистка истекших записей
- Значение TTL по умолчанию: 3600 секунд (1 час)

## Декораторы

### cached

Декоратор для кэширования результатов функций.

```python
def cached(ttl: Optional[int] = None, cache_name: str = \"default_cache\") -> Callable:
    """
    Args:
        ttl: Time-to-live в секундах (None = бесконечно)
        cache_name: Имя кэша
    """
```

**Особенности:**
- Автоматическое создание ключа из имени функции и аргументов
- Логирование cache hit/miss
- Поддержка кастомного TTL

### global_cache

Глобальный кэш для приложений.

```python
global_cache = TTLCache(default_ttl=3600, name=\"global_cache\")
```

**Особенности:**
- Используется по умолчанию для кэширования
- TTL по умолчанию: 3600 секунд (1 час)

## Стратегии управления

### LRU Cache Strategy

LRU (Least Recently Used) стратегия — извлекает наименее недавно используемые записи.

```python
class LRUCacheStrategy(CacheStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### FIFO Cache Strategy

FIFO (First In, First Out) стратегия — извлекает самые старые записи.

```python
class FIFOCacheStrategy(CacheStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### LFU Cache Strategy

LFU (Least Frequently Used) стратегия — извлекает наименее часто используемые записи.

```python
class LFUCacheStrategy(CacheStrategy):
    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Максимальное количество записей
        """
```

### CacheStrategyFactory

Фабрика стратегий управления кэшем.

```python
class CacheStrategyFactory:
    @classmethod
    def create(cls, strategy_name: str, **kwargs) -> CacheStrategy:
        """
        Args:
            strategy_name: Имя стратегии (lru, fifo, lfu)
            **kwargs: Аргументы для конструктора стратегии
        """
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        \"\"\"Получить список доступных стратегий\"\"\"
```

## Валидаторы

### SizeValidator

Валидатор размера значения.

```python
class SizeValidator(CacheValidator):
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
class TypeValidator(CacheValidator):
    def __init__(self, allowed_types: List[type] = None):
        """
        Args:
            allowed_types: Список разрешенных типов
        """
```

### PatternValidator

Валидатор ключа по паттерну.

```python
class PatternValidator(CacheValidator):
    def __init__(self, pattern: str = r\"^[a-zA-Z][a-zA-Z0-9_]*$\"):
        """
        Args:
            pattern: Регулярное выражение для ключа
        """
```

### CustomValidator

Пользовательский валидатор.

```python
class CustomValidator(CacheValidator):
    def __init__(self, validate_func: Callable[[str, Any], bool], name: str = \"custom\"):
        """
        Args:
            validate_func: Функция валидации
            name: Имя валидатора
        """
```

### CacheValidatorFactory

Фабрика валидаторов кэша.

```python
class CacheValidatorFactory:
    @classmethod
    def create(cls, validator_name: str, **kwargs) -> CacheValidator:
        """
        Args:
            validator_name: Имя валидатора
            **kwargs: Аргументы для конструктора
        """
    
    @classmethod
    def get_available_validators(cls) -> List[str]:
        \"\"\"Получить список доступных валидаторов\"\"\"
```

### CacheValidatorChain

Цепочка валидаторов.

```python
class CacheValidatorChain:
    def __init__(self):
        \"\"\"Инициализация цепочки валидаторов\"\"\"
    
    def add(self, validator: CacheValidator) -> 'CacheValidatorChain':
        \"\"\"Добавить валидатор в цепочку\"\"\"
    
    def validate(self, key: str, value: Any) -> bool:
        \"\"\"Валидировать через цепочку\"\"\"
    
    def get_first_error(self) -> Optional[str]:
        \"\"\"Получить первое сообщение об ошибке\"\"\"
    
    def validate_all(self, entries: Dict[str, Any]) -> Dict[str, bool]:
        \"\"\"Валидировать несколько записей\"\"\"
```

## Примеры использования

### Создание и использование кэша

```python
from common.cache import TTLCache, FileCache, global_cache

# TTL кэш
ttl_cache = TTLCache(default_ttl=3600)
ttl_cache.set(\"key1\", \"value1\")
ttl_cache.set(\"key2\", \"value2\", ttl=600)

# Файловый кэш
from pathlib import Path
file_cache = FileCache(cache_dir=Path(\"./cache\"))
file_cache.set(\"key1\", \"value1\")

# Глобальный кэш
global_cache.set(\"key\", \"value\")
```

### Использование декоратора cached

```python
from common.cache import cached

@cached(ttl=3600, cache_name=\"api_cache\")
def fetch_data(url: str) -> dict:
    # Сложная операция получения данных
    return {\"url\": url, \"data\": \"result\"}

# Первый вызов - кэш miss
result1 = fetch_data(\"http://example.com\")

# Второй вызов - кэш hit
result2 = fetch_data(\"http://example.com\")
```

### Использование стратегий

```python
from common.cache import LRUCacheStrategy, CacheStrategyFactory

# Создание стратегии через фабрику
strategy = CacheStrategyFactory.create(\"lru\", max_size=100)

# Использование стратегии
# (предполагается интеграция со стратегиями в будущем)
```

### Использование валидаторов

```python
from common.cache import (
    SizeValidator, 
    TypeValidator, 
    PatternValidator,
    CacheValidatorChain
)

# Создание цепочки валидаторов
chain = CacheValidatorChain()
chain.add(SizeValidator(max_size=1024))
chain.add(TypeValidator(allowed_types=[str, int]))
chain.add(PatternValidator())

# Валидация
is_valid = chain.validate(\"key\", \"value\")

# Валидация нескольких записей
entries = {\"key1\": \"value1\", \"key2\": \"value2\"}
results = chain.validate_all(entries)
```

## Архитектура \"Core + Modules + Orchestrator\"\n\n### Core\n- `cache_core.py` — Базовые абстракции (CacheEntry, BaseCache, FileCache, TTLCache)

### Modules\n- `cache_strategies.py` — Стратегии управления кэшем\n- `cache_validators.py` — Валидаторы кэша\n\n### Orchestrator\n- `cached` — Декоратор для кэширования\n- `global_cache` — Глобальный кэш для приложений

## Миграция со старой версии

### Старый код (cache_manager.py)

```python
from common.cache_manager import CacheManager

manager = CacheManager()
manager.cache(\"key\", \"value\", ttl=3600)
```

### Новый код (common/cache/)

```python
from common.cache import global_cache

global_cache.set(\"key\", \"value\", ttl=3600)
```

## Зависимости

- `typing` — Типизация
- `abc` — Абстрактные базовые классы
- `re` — Регулярные выражения
- `time` — Время
- `pathlib.Path` — Пути к файлам
- `hashlib` — Хэширование
- `json` — JSON

## Логирование

Все модули используют стандартный модуль `logging` для записи событий.

```python
import logging

logger = logging.getLogger(__name__)
```

## Примечания

- Все TTL указаны в секундах
- По умолчанию TTLCache имеет TTL 3600 секунд (1 час)
- FileCache сохраняет данные в JSON формате
- Глобальный кэш доступен через `from common.cache import global_cache`
- Ключи хэшируются для имен файлов в FileCache
- Декоратор cached автоматически создает ключ из имени функции и аргументов