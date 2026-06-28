# Project Scanner

Оптимизированный сканер проекта для Cognitive Agent.

## 📋 Описание

Project Scanner — это высокопроизводительный инструмент для анализа структуры проекта, который:

- ✅ Сканирует файлы с кэшированием для ускорения повторных запусков
- ✅ Поддерживает параллельную обработку файлов
- ✅ Уважает `.gitignore` правила
- ✅ Экспортирует результаты в JSON/CSV
- ✅ Интегрируется с Cognitive Agent

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install pathspec tqdm
```

### Базовое использование

```python
from agents.cognitive_agent.src.project_scanner import ProjectScanner, ScannerConfig

# Создание сканера
scanner = ProjectScanner("C:\\my-project")

# Полное сканирование
results = scanner.scan_full()

# Вывод статистики
print(f"Сканировано файлов: {results['scanned_files']}")
print(f"Длительность: {results['duration']:.2f} сек")
```

## 📖 Использование

### Режимы сканирования

#### 1. Полное сканирование

```python
results = scanner.scan_full()
```

Сканирует все файлы проекта с уважением `.gitignore`.

#### 2. Инкрементальное сканирование (git diff)

```python
results = scanner.scan_git_diff()
```

Сканирует только изменённые файлы (working tree + staged).

#### 3. Выборочное сканирование

```python
results = scanner.scan_paths(["src/", "tests/"])
```

Сканирует только указанные директории/файлы.

### Конфигурация

```python
config = ScannerConfig(
    timeout=30,              # Таймаут операций (сек)
    max_workers=4,           # Количество потоков
    max_file_size=100*1024*1024,  # Макс. размер файла (байт)
    include_extensions=['.py', '.js'],  # Разрешённые расширения
    extra_ignores=['node_modules'],     # Дополнительные игноры
    cache_file=".scan_cache.json"       # Файл кэша
)

scanner = ProjectScanner("C:\\my-project", config)
```

### Экспорт результатов

```python
# JSON
scanner.export_results(results, "results.json", "json")

# CSV
scanner.export_results(results, "results.csv", "csv")
```

## 🛠️ CLI-интерфейс

### Запуск из корня проекта

```bash
# Полное сканирование
python scripts/run_project_scanner.py C:\my-project --mode full

# Инкрементальное (git diff)
python scripts/run_project_scanner.py C:\my-project --mode git_diff

# Выборочное
python scripts/run_project_scanner.py C:\my-project --mode paths --paths src/ tests/

# С экспортом
python scripts/run_project_scanner.py C:\my-project --mode full --export results.json --format json

# Подробный вывод
python scripts/run_project_scanner.py C:\my-project --verbose
```

### Параметры CLI

| Параметр       | Описание                          | По умолчанию    |
| -------------- | --------------------------------- | --------------- |
| `project_path` | Путь к проекту                    | **Обязательно** |
| `--mode`       | Режим сканирования                | `full`          |
| `--paths`      | Пути для выборочного сканирования | -               |
| `--config`     | Файл конфигурации (JSON)          | -               |
| `--export`     | Файл для экспорта                 | -               |
| `--format`     | Формат экспорта (`json`, `csv`)   | `json`          |
| `--verbose`    | Подробный вывод                   | False           |

## 🔌 Интеграция с Cognitive Agent

### Использование через сервис

```python
from agents.cognitive_agent.src.scanner_integration import ProjectScannerService

# Создание сервиса
service = ProjectScannerService(
    default_project_path="C:\\my-project",
    default_config_path="config/scanner.json"
)

# Сканирование
results = service.scan(mode="git_diff")

# Получение сводки
summary = service.get_last_summary()
print(summary)

# Экспорт
service.export_last_results("results.json")
```

### Функция `scan_project()`

```python
from agents.cognitive_agent.src.scanner_integration import scan_project

results = scan_project(
    "C:\\my-project",
    mode="full",
    use_cache=True,
    export_path="results.json"
)
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Базовые тесты
pytest agents/cognitive_agent/tests/test_project_scanner.py -v

# С покрытием
pytest agents/cognitive_agent/tests/test_project_scanner.py -v --cov=agents.cognitive_agent.src.project_scanner --cov-report=term-missing
```

### Структура тестов

- `TestScannerConfig` — тесты конфигурации
- `TestProjectScanner` — тесты сканера
- `TestFileProcessing` — тесты обработки файлов
- `TestEdgeCases` — граничные случаи

## 📊 Результаты

Формат возвращаемых данных:

```python
{
    "mode": "full",           # Режим сканирования
    "duration": 1.23,         # Длительность (сек)
    "total_files": 100,       # Всего файлов
    "scanned_files": 95,      # Сканировано
    "ignored_files": 5,       # Игнорировано
    "files": [
        {
            "path": "src/main.py",
            "hash": "abc123...",
            "size": 1024,
            "mtime": 1234567890.0
        },
        # ...
    ],
    "timestamp": "2026-06-13T12:00:00"
}
```

## ⚙️ Кэширование

Сканер автоматически кэширует хэши файлов для ускорения повторных запусков:

- Кэш сохраняется в `.cognitive_agent_scan_cache.json`
- При повторном сканировании сравниваются хэши
- Изменённые файлы обрабатываются заново

### Управление кэшем

```python
# Отключить кэш
scanner = ProjectScanner("C:\\my-project", ScannerConfig(cache_file=None))

# Удалить кэш вручную
import os
cache_file = Path("C:\\my-project\\.cognitive_agent_scan_cache.json")
if cache_file.exists():
    cache_file.unlink()
```

## 🔒 Безопасность

- MD5 хэши вычисляются с `usedforsecurity=False` (только для целостности)
- Нет внешних сетевых запросов
- Поддерживается работа с большими файлами (с ограничением по размеру)

## 🐛 Устранение проблем

### pathspec не установлен

```bash
pip install pathspec
```

### Ошибки прав доступа

Убедитесь, что у вас есть права на чтение всех файлов проекта.

### Медленное сканирование

- Увеличьте `max_workers` в конфигурации
- Добавьте больше паттернов в `.gitignore`
- Используйте режим `git_diff` для инкрементальных изменений

## 📝 Примеры использования

### Анализ изменений перед коммитом

```python
results = scan_project(".", mode="git_diff")
print(f"Изменено файлов: {results['changed_files']}")
```

### Генерация отчёта о проекте

```python
results = scan_project(".", mode="full", export_path="report.json")
```

### Проверка конкретных модулей

```python
results = scan_project(".", mode="paths", paths=["src/core/", "src/utils/"])
```

## 📚 См. также

- [Cognitive Agent Documentation](../README.md)
- [Project Scanner Source Code](../src/project_scanner.py)
- [Integration Tests](../tests/test_project_scanner.py)
