# Оптимизация сканирования проекта

## Проблема
Ранее Cognitive Agent сканировал **все 16,000+ файлов** при каждом запуске, что вызывало:
- Высокую нагрузку на CPU (шумный ноутбук)
- Длительное время сканирования (~20 секунд)
- Избыточное потребление памяти

## Решение
Реализована **комбинация оптимизаций**:

### 1. Уважение `.gitignore` ✅
- Используется библиотека `pathspec` для парсинга `.gitignore`
- Исключаются: `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.archive` и др.
- **Экономия**: ~90% файлов (сканируем ~1,357 вместо 16,000)

### 2. Git diff режим ✅
- Сканируются только изменённые файлы (`git diff --name-only`)
- Инкрементальное сканирование по MD5 хэшам
- **Экономия**: ~95% ресурсов (сканируем 10-50 файлов вместо 1,357)

### 3. Кэширование хэшей ✅
- Сохранение хэшей в `.cognitive_agent_scan_cache.json`
- При повторном запуске проверяется только изменение хэша
- **Экономия**: ~99% времени при отсутствии изменений

---

## Режимы сканирования

### `auto` (по умолчанию)
```python
agent.scan_project(mode="auto")
```
- Проверяет git diff на изменения
- Если изменений нет → пропускает сканирование
- Если есть изменения → сканирует только их

### `git_diff`
```python
agent.scan_project(mode="git_diff")
```
- Сканирует только изменённые/добавленные файлы

### `full`
```python
agent.scan_project(mode="full")
```
- Полное сканирование всех файлов (с уважением .gitignore)
- Используется для первичного сканирования или принудительной проверки

### `paths`
```python
agent.scan_project(mode="paths")
# Или установить self.scan_paths = ['apps/cognitive_agent', '.agents']
```
- Сканирует только указанные директории

---

## Установка зависимостей

```powershell
# Активируйте виртуальное окружение
.\activate-venv.ps1

# Установите pathspec
C:\repo\.venv\Scripts\python.exe -m pip install pathspec>=0.12.0
```

---

## Метрики производительности

| Режим | Файлов | Время | CPU |
|-------|--------|-------|-----|
| **До оптимизации** | 16,000 | ~20 сек | 80-100% |
| `auto` (нет изменений) | 0 | ~0.1 сек | <5% |
| `git_diff` (10 файлов) | 10 | ~0.5 сек | 10-20% |
| `full` (с .gitignore) | 1,357 | ~2 сек | 30-40% |

---

## Использование в Cognitive Agent

### Отключить автозапуск
Автозапуск уже отключён в `.vscode/tasks.json`. Запускать вручную:

```powershell
# Режим auto (только изменения)
python -m apps.cognitive_agent.autonomous_agent --start --project C:\repo

# Режим full (полное сканирование)
python -m apps.cognitive_agent.autonomous_agent --start --project C:\repo --full-scan

# Режим git_diff
python -m apps.cognitive_agent.autonomous_agent --start --project C:\repo --git-diff
```

### Аргументы командной строки
- `--start` — запустить агента
- `--stop` — остановить агента
- `--status` — проверить статус
- `--scan` — выполнить однократное сканирование
- `--full-scan` — полное сканирование (вместо git diff)
- `--git-diff` — только изменённые файлы
- `--foreground` — работать в переднем плане

---

## Кэш сканирования

Файл `.cognitive_agent_scan_cache.json` содержит MD5 хэши всех сканированных файлов.

### Очистка кэша
```powershell
Remove-Item C:\repo\.cognitive_agent_scan_cache.json
```

После очистки будет выполнено полное сканирование.

---

## Настройка игнорирования

Редактируйте `.gitignore` в корне проекта. Автоматически поддерживаются:
- `.venv/`, `venv/`, `env/` — виртуальные окружения
- `__pycache__/`, `*.pyc` — кэш Python
- `node_modules/`, `dist/`, `build/` — артефакты сборки
- `.pytest_cache/`, `.ruff_cache/` — кэш инструментов
- `.archive/`, `.codeassistant/` — архивы

---

## Разработка

### Тестирование сканера
```python
from apps.cognitive_agent.src.project_scanner import ProjectScanner

scanner = ProjectScanner("C:/repo")

# Режим git diff
result = scanner.scan_git_diff()
print(f"Изменено: {result['changed_files']} файлов")

# Полное сканирование
result = scanner.scan_full()
print(f"Всего: {result['scanned_files']} файлов")

# Выборочное сканирование
result = scanner.scan_paths(["apps/cognitive_agent", ".agents"])
print(f"Выборочно: {result['scanned_files']} файлов")
```

---

## Планы на будущее

- [ ] Параллельное сканирование (multiprocessing)
- [ ] Webhook-триггеры от Git
- [ ] Интеграция с pre-commit хуками
- [ ] Статистика по типам файлов
- [ ] Экспорт результатов в JSON/CSV

---

## Авторы
- Разработано: Koda CLI
- Дата: 27 мая 2026
- Версия: 1.0.0