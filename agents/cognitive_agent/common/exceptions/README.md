# Модуль исключений Cognitive Agent

Этот модуль предоставляет иерархию исключений и централизованный обработчик ошибок для Cognitive Agent.

## Структура

```
common/
├── exceptions/
│   ├── README.md          # Этот файл
│   └── exceptions.py      # Иерархия исключений и ErrorHandler
```

## Иерархия исключений

### Базовое исключение

#### `CognitiveAgentError`

Базовое исключение для всех ошибок агента.

**Атрибуты:**
- `message` (str): Сообщение об ошибке
- `details` (Dict[str, Any]): Дополнительные детали ошибки
- `timestamp`: Временная метка возникновения
- `traceback_info`: Строковое представление стека вызовов

**Методы:**
- `to_dict() -> Dict[str, Any]`: Преобразовать исключение в словарь для логирования

**Пример:**
```python
from common.exceptions import CognitiveAgentError

try:
    raise CognitiveAgentError("Ошибка агента", details={"code": 1001})
except CognitiveAgentError as e:
    print(e.message)  # "Ошибка агента"
    print(e.to_dict())
```

### Специализированные исключения

#### `ConfigurationError`

Ошибка конфигурации агента.

```python
from common.exceptions import ConfigurationError

try:
    # Ошибка конфигурации
    raise ConfigurationError("Неверная конфигурация", details={"key": "missing_field"})
except ConfigurationError as e:
    print(f"Конфигурационная ошибка: {e.message}")
```

#### `SecurityViolationError`

Нарушение безопасности.

```python
from common.exceptions import SecurityViolationError

try:
    # Нарушение безопасности
    raise SecurityViolationError("Несанкционированный доступ", details={"user": "unknown"})
except SecurityViolationError as e:
    print(f"Ошибка безопасности: {e.message}")
```

#### `ResourceExhaustionError`

Исчерпание ресурсов (память, диск, CPU).

```python
from common.exceptions import ResourceExhaustionError

try:
    # Исчерпание ресурсов
    raise ResourceExhaustionError("Недостаточно памяти", details={"available": "128MB", "required": "512MB"})
except ResourceExhaustionError as e:
    print(f"Ошибка ресурсов: {e.message}")
```

#### `AIServiceError`

Ошибка сервиса ИИ.

```python
from common.exceptions import AIServiceError

try:
    # Ошибка ИИ сервиса
    raise AIServiceError("Сервер ИИ недоступен", details={"provider": "openai"})
except AIServiceError as e:
    print(f"Ошибка ИИ: {e.message}")
```

#### `FileOperationError`

Ошибка операции с файлами.

```python
from common.exceptions import FileOperationError

try:
    # Ошибка файловой операции
    raise FileOperationError("Файл не найден", details={"path": "/data/file.txt"})
except FileOperationError as e:
    print(f"Файловая ошибка: {e.message}")
```

#### `NetworkError`

Ошибка сети.

```python
from common.exceptions import NetworkError

try:
    # Ошибка сети
    raise NetworkError("Соединение потеряно", details={"host": "api.example.com"})
except NetworkError as e:
    print(f"Сетевая ошибка: {e.message}")
```

#### `ValidationError`

Ошибка валидации данных.

```python
from common.exceptions import ValidationError

try:
    # Ошибка валидации
    raise ValidationError("Неверный формат данных", details={"field": "email", "value": "invalid"})
except ValidationError as e:
    print(f"Ошибка валидации: {e.message}")
```

#### `TaskExecutionError`

Ошибка выполнения задачи.

```python
from common.exceptions import TaskExecutionError

try:
    # Ошибка выполнения задачи
    raise TaskExecutionError("Задача не выполнена", details={"task_id": "12345"})
except TaskExecutionError as e:
    print(f"Ошибка задачи: {e.message}")
```

#### `IntegrationError`

Ошибка интеграции с внешними системами.

```python
from common.exceptions import IntegrationError

try:
    # Ошибка интеграции
    raise IntegrationError("Не удалось подключиться к внешней системе", details={"system": "database"})
except IntegrationError as e:
    print(f"Ошибка интеграции: {e.message}")
```

#### `AgentStateError`

Ошибка состояния агента.

```python
from common.exceptions import AgentStateError

try:
    # Ошибка состояния
    raise AgentStateError("Агент в недопустимом состоянии", details={"state": "invalid"})
except AgentStateError as e:
    print(f"Ошибка состояния: {e.message}")
```

#### `DataProcessingError`

Ошибка обработки данных.

```python
from common.exceptions import DataProcessingError

try:
    # Ошибка обработки данных
    raise DataProcessingError("Не удалось обработать данные", details={"format": "json"})
except DataProcessingError as e:
    print(f"Ошибка обработки: {e.message}")
```

#### `CacheError`

Ошибка кэширования.

```python
from common.exceptions import CacheError

try:
    # Ошибка кэша
    raise CacheError("Не удалось записать в кэш", details={"key": "user:123"})
except CacheError as e:
    print(f"Ошибка кэша: {e.message}")
```

#### `AuditLogError`

Ошибка аудит-логирования.

```python
from common.exceptions import AuditLogError

try:
    # Ошибка аудита
    raise AuditLogError("Не удалось записать в лог", details={"event": "login"})
except AuditLogError as e:
    print(f"Ошибка аудита: {e.message}")
```

## ErrorHandler

Централизованный обработчик ошибок для Cognitive Agent.

### Основные методы

#### `handle_error(error, context=None) -> Dict[str, Any]`

Обработать ошибку и вернуть информацию о ней.

**Параметры:**
- `error` (Exception): Объект ошибки
- `context` (Dict[str, Any], optional): Контекст ошибки

**Возвращает:**
- Словарь с информацией об ошибке:
  - `handled` (bool): Обработана ли ошибка
  - `original_error` (Exception): Оригинальная ошибка
  - `timestamp`: Временная метка
  - `context` (Dict): Контекст
  - `recovery_action` (str): Действие восстановления
  - `should_retry` (bool): Нужно ли повторить
  - `retry_count` (int): Количество повторов

#### `safe_execute(func, *args, error_context=None, **kwargs)`

Безопасно выполнить функцию с обработкой ошибок.

**Параметры:**
- `func`: Функция для выполнения
- `*args`: Аргументы функции
- `error_context` (Dict, optional): Контекст ошибки
- `**kwargs`: Ключевые аргументы

**Возвращает:**
- Результат выполнения или словарь с ошибкой

#### `get_error_statistics() -> Dict[str, int]`

Получить статистику ошибок по типам.

**Возвращает:**
- Словарь `{error_type: count}`

#### `reset_error_statistics()`

Сбросить статистику ошибок.

### Примеры использования

#### Базовое использование

```python
from common.exceptions import ErrorHandler, NetworkError

handler = ErrorHandler()

# Обработка ошибки
error = NetworkError("Соединение потеряно")
result = handler.handle_error(error, context={"host": "api.example.com"})
print(result)  # {'handled': True, 'should_retry': True, ...}
```

#### Безопасное выполнение функции

```python
from common.exceptions import ErrorHandler, NetworkError

handler = ErrorHandler()

def risky_function():
    raise NetworkError("Соединение потеряно")

result = handler.safe_execute(risky_function)
print(result)  # {'success': False, 'error_info': {...}}
```

#### Статистика ошибок

```python
from common.exceptions import ErrorHandler

handler = ErrorHandler()

# Обработать несколько ошибок
handler.handle_error(ValueError("Ошибка 1"))
handler.handle_error(NetworkError("Ошибка 2"))
handler.handle_error(ValueError("Ошибка 3"))

# Получить статистику
stats = handler.get_error_statistics()
print(stats)  # {'ValueError': 2, 'NetworkError': 1}

# Сбросить статистику
handler.reset_error_statistics()
```

#### Декоратор для обработки ошибок

```python
from common.exceptions import handle_errors

@handle_errors()
def my_function():
    # Код, который может вызвать ошибки
    pass

# Функция будет автоматически обрабатывать ошибки
result = my_function()
```

#### Регистрация глобального обработчика

```python
from common.exceptions import register_error_handler, ErrorHandler

custom_handler = ErrorHandler()
register_error_handler(custom_handler)

# Теперь global_error_handler будет использовать custom_handler
```

## Лучшие практики

### 1. Использование специализированных исключений

Всегда используйте специализированные исключения вместо общих:

```python
# Плохо
raise Exception("Ошибка конфигурации")

# Хорошо
from common.exceptions import ConfigurationError
raise ConfigurationError("Неверная конфигурация", details={"key": "value"})
```

### 2. Обработка ошибок с контекстом

Всегда предоставляйте контекст при обработке ошибок:

```python
from common.exceptions import ErrorHandler, FileOperationError

handler = ErrorHandler()

try:
    # Операция с файлами
    pass
except FileOperationError as e:
    result = handler.handle_error(e, context={"file": "data.txt"})
```

### 3. Использование safe_execute для критичных операций

```python
from common.exceptions import ErrorHandler

handler = ErrorHandler()

def critical_operation():
    # Критичная операция
    pass

result = handler.safe_execute(critical_operation)
if not result.get('success'):
    print(f"Операция не удалась: {result.get('error_info')}")
```

### 4. Мониторинг ошибок через статистику

```python
from common.exceptions import global_error_handler

# В периодическом задании
stats = global_error_handler.get_error_statistics()
if stats.get('NetworkError', 0) > 10:
    # Отправить алерт
    send_alert("Слишком много сетевых ошибок")
```

### 5. Использование декораторов для простых случаев

```python
from common.exceptions import handle_errors

@handle_errors()
def process_data(data):
    # Обработка данных
    pass

# Автоматическая обработка ошибок
result = process_data({"key": "value"})
```

## Миграция

### Из старой версии

Если у вас есть старый код с общими исключениями:

```python
# Старый код
from common.exceptions import CognitiveAgentError

try:
    # Код
    pass
except Exception as e:
    # Обработка

# Новый код
from common.exceptions import ConfigurationError, NetworkError

try:
    # Код
    pass
except ConfigurationError as e:
    # Обработка конфигурации
except NetworkError as e:
    # Обработка сети
```

### Добавление новых исключений

Для добавления нового типа исключения:

```python
# В exceptions.py
class NewError(CognitiveAgentError):
    """Новое исключение"""
    pass

# В коде
from common.exceptions import NewError

try:
    # Код
    pass
except NewError as e:
    # Обработка
```

## Связанные модули

- `common.cache` - Кэширование данных
- `common.memory` - Управление памятью
- `common.utils` - Утилиты

## Смотрите также

- [Кэширование](../cache/README.md)
- [Память](../memory/README.md)
- [Утилиты](../utils/README.md)
- [План рефакторинга](../../REFACTORING_PLAN.md)
