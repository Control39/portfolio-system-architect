# Cognitive Agent Utils Module

## Описание

Модуль утилит для Cognitive Agent предоставляет вспомогательные функции для работы с файлами, JSON, поиском и форматированием данных. Все функции оптимизированы для использования в AI-агентских сценариях.

## Архитектура

```
common/utils/
├── utils.py         # Основные утилиты (file_utils, format_utils)
├── file_utils.py    # Файловые утилиты (будущее развитие)
├── format_utils.py  # Форматирование данных (будущее развитие)
└── README.md        # Документация
```

## Основные функции

### calculate_file_hash

Вычислить хэш файла для определения изменений.

```python
def calculate_file_hash(file_path: Path) -> str:
    """
    Вычислить хэш файла для определения изменений

    Args:
        file_path: Путь к файлу

    Returns:
        SHA256 хэш файла в виде шестнадцатеричной строки
    """
```

**Пример использования:**

```python
from pathlib import Path
from common.utils import calculate_file_hash

file_path = Path("config.json")
file_hash = calculate_file_hash(file_path)
print(f"Хэш файла: {file_hash}")

# Проверка изменений
old_hash = file_hash
# ... изменение файла ...
new_hash = calculate_file_hash(file_path)
if old_hash != new_hash:
    print("Файл был изменен!")
```

**Особенности:**
- Использует SHA256 для надежного хэширования
- Читает файл порциями (4096 байт) для эффективности
- Возвращает хэш в человекочитаемом формате

### load_json_file

Загрузить JSON-файл с обработкой ошибок.

```python
def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Загрузить JSON-файл с обработкой ошибок

    Args:
        file_path: Путь к JSON файлу

    Returns:
        Словарь с данными из файла или None при ошибке
    """
```

**Пример использования:**

```python
from pathlib import Path
from common.utils import load_json_file

# Загрузка конфигурации
config = load_json_file(Path("config.json"))
if config:
    print(f"Конфигурация загружена: {config}")
else:
    print("Не удалось загрузить конфигурацию")

# Обработка ошибок
data = load_json_file(Path("nonexistent.json"))
if data is None:
    print("Файл не найден или содержит ошибки")
```

**Особенности:**
- Автоматическая обработка FileNotFoundError
- Обработка JSONDecodeError с логированием
- Возвращает None при ошибке вместо исключения
- Логирование предупреждений и ошибок

### find_files_by_extension

Найти файлы с указанными расширениями в директории.

```python
def find_files_by_extension(directory: Path, extensions: List[str]) -> List[Path]:
    """
    Найти файлы с указанными расширениями в директории

    Args:
        directory: Корневая директория для поиска
        extensions: Список расширений (например, ['.py', '.json'])

    Returns:
        Список путей к найденным файлам
    """
```

**Пример использования:**

```python
from pathlib import Path
from common.utils import find_files_by_extension

# Поиск всех Python файлов
python_files = find_files_by_extension(Path("."), ['.py'])
print(f"Найдено Python файлов: {len(python_files)}")

# Поиск нескольких типов файлов
files = find_files_by_extension(
    Path("src"),
    ['.py', '.json', '.md']
)
for file_path in files:
    print(f"- {file_path}")
```

**Особенности:**
- Рекурсивный поиск во всех поддиректориях
- Поддержка нескольких расширений за один вызов
- Работает с любыми расширениями (с или без точки)

### format_bytes

Форматировать размер в байтах в человекочитаемый формат.

```python
def format_bytes(size_bytes: int) -> str:
    """
    Форматировать размер в байтах в человекочитаемый формат

    Args:
        size_bytes: Размер в байтах

    Returns:
        Строка в формате '1.25MB', '512KB' и т.д.
    """
```

**Пример использования:**

```python
from common.utils import format_bytes

# Форматирование размеров
print(format_bytes(1024))       # 1.00KB
print(format_bytes(1024 * 1024))  # 1.00MB
print(format_bytes(1024 * 1024 * 1024))  # 1.00GB

# Использование в отчетах
cache_size = 5242880  # 5 MB
print(f"Размер кэша: {format_bytes(cache_size)}")
```

**Особенности:**
- Автоматическое определение единицы измерения
- Два знака после запятой для точности
- Поддержка от 0B до TB+

## Архитектура "Core + Modules + Orchestrator"

### Core
- `utils.py` — Базовые функции (calculate_file_hash, load_json_file, find_files_by_extension, format_bytes)

### Modules (будущее развитие)
- `file_utils.py` — Расширенные файловые утилиты
- `format_utils.py` — Специализированные функции форматирования

### Orchestrator
- Интеграция с другими модулями (cache, memory, exceptions)

## Миграция со старой версии

### Старый код (встроенные функции)

```python
import hashlib
import json

# Хэширование
with open(file_path, "rb") as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

# Загрузка JSON
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = None
```

### Новый код (common/utils/)

```python
from common.utils import calculate_file_hash, load_json_file

# Хэширование
file_hash = calculate_file_hash(file_path)

# Загрузка JSON
data = load_json_file(file_path)
```

## Зависимости

- `hashlib` — Хэширование файлов
- `json` — Парсинг JSON
- `pathlib.Path` — Работа с путями
- `typing` — Типизация
- `logging` — Логирование ошибок

## Логирование

Функции используют стандартный модуль `logging` для записи событий.

```python
import logging

logging.warning(f"Файл {file_path} не найден")
logging.error(f"Ошибка парсинга JSON в {file_path}: {e}")
```

## Лучшие практики

1. **И��пользуйте calculate_file_hash** для отслеживания изменений файлов
2. **Используйте load_json_file** вместо прямой загрузки JSON для обработки ошибок
3. **Используйте find_files_by_extension** для поиска файлов по типам
4. **Используйте format_bytes** для отображения размеров в UI и логах
5. **Всегда проверяйте None** при использовании load_json_file

## Примеры интеграции

### С кэшированием

```python
from pathlib import Path
from common.utils import calculate_file_hash, load_json_file
from common.cache import global_cache

def load_config_with_cache(config_path: Path) -> dict:
    """Загрузить конфигурацию с кэшированием по хэшу"""
    file_hash = calculate_file_hash(config_path)

    # Проверка кэша
    cache_key = f"config_{file_hash}"
    cached_config = global_cache.get(cache_key)
    if cached_config:
        return cached_config

    # Загрузка и кэширование
    config = load_json_file(config_path)
    if config:
        global_cache.set(cache_key, config, ttl=3600)
    return config
```

### С памятью

```python
from pathlib import Path
from common.utils import find_files_by_extension, load_json_file
from common.memory import WorkingMemory

def load_all_configs(memory: WorkingMemory, config_dir: Path):
    """Загрузить все конфигурации в память"""
    config_files = find_files_by_extension(config_dir, ['.json'])

    for config_file in config_files:
        config = load_json_file(config_file)
        if config:
            memory.store(f"config_{config_file.stem}", config)
```

## Примечания

- Все функции работают с Path из pathlib
- load_json_file возвращает None при ошибке (не исключение)
- find_files_by_extension рекурсивно ищет во всех поддиректориях
- format_bytes использует десятичные префиксы (1KB = 1024B)
- Хэширование использует SHA256 для надежности

## Планы развития

- Добавить `file_utils.py` для расширенных операций с файлами
- Добавить `format_utils.py` для специализированного форматирования
- Добавить функции для работы с CSV, YAML, XML
- Добавить функции для работы с архивами
