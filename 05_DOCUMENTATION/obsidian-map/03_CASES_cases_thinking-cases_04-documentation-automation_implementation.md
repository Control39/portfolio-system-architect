# Implementation

- **Путь**: `03_CASES\cases\thinking-cases\04-documentation-automation\implementation.md`
- **Тип**: .MD
- **Размер**: 5,413 байт
- **Последнее изменение**: 2026-03-12 06:53:50

## Превью

```
# Реализация

## Структура файлов

```
scripts/
├── generate_obsidian_map.py   # Генерация карты знаний
├── generate_website.py         # Генерация сайта
├── run_daily.ps1               # Ежедневная автоматизация
└── ...
```

## Детали реализации

### generate_obsidian_map.py

```python
# Основные параметры
REPO_ROOT: Path = Path(".")           # Корень репозитория
OUTPUT_DIR: Path = Path("docs/obsidian-map")  # Выходная директория

# Игнорируемые директории
IGNORED_DIRS: Set[str] = {
    ".git"
... (файл продолжается)
```
