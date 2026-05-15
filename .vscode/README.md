# 📋 README: Настройка VS Code для KODA CLI

**Дата:** 15 мая 2026 г.
**Статус:** ✅ Завершено

---

## ✅ Выполненные действия

### 1. Созданы конфигурационные файлы

| Файл | Назначение | Статус |
|------|------------|--------|
| `.vscode/settings.json` | Глобальные настройки проекта | ✅ Обновлён |
| `.vscode/tasks.json` | Задачи Makefile (Ctrl+Shift+P) | ✅ Создан |
| `.vscode/keybindings.json` | Горячие клавиши | ✅ Создан |
| `.vscode/extensions.json` | Рекомендуемые расширения | ✅ Обновлён |
| `.vscode/python.snippets` | Снаппеты для Python/KODA | ✅ Создан |
| `.vscode/chat-logger.py` | Утилита логирования чатов | ✅ Создан |
| `.chat-cache/.gitkeep` | Директория для логов | ✅ Создан |
| `.reports/vscode-setup-report.md` | Отчёт настройки | ✅ Создан |

### 2. Настроены профили терминала

```json
{
  "Git Bash": "Основной профиль (для make команд)",
  "PowerShell": "Windows-специфичные задачи",
  "Make (venv)": "Предварительно активированный venv"
}
```

### 3. Добавлены горячие клавиши

| Команда | Shortcut | Назначение |
|---------|----------|------------|
| Новый терминал | `Ctrl+Shift+`` | Быстрое открытие |
| Запустить тесты | `Ctrl+Shift+R` | `make test` |
| Линтинг | `Ctrl+Shift+L` | `make lint` |
| Форматирование | `Ctrl+Shift+F` | `make format` |
| Фокус на терминал | `Ctrl+`` | Переключение |
| Установка зависимостей | `Ctrl+Shift+I` | `make install` |
| Docker-сервисы (up) | `Ctrl+Shift+C` | `make docker-up` |
| Docker-сервисы (down) | `Ctrl+Shift+X` | `make docker-down` |
| Очистка терминала | `Ctrl+Shift+K` | `clear` |
| Задачи (список) | `Ctrl+Shift+T` | Показать запущенные |

### 4. Снаппеты для KODA

| Снаппет | Префикс | Результат |
|---------|---------|-----------|
| KODA Log Entry | `kodalogs` | Запись в KODA.md |
| KODA Section Header | `kodaheader` | Раздел с метриками |
| Task Checklist | `todo` | Checklist с подзадачами |
| Python Docstring | `pydoc` | Google-style docstring |
| Test Function | `pytest` | Async pytest тест |
| FastAPI Endpoint | `fastapi` | Router endpoint |
| Git Commit Message | `gitcommit` | Conventional Commit |

### 5. Логирование чатов

**Утилита:** `.vscode/chat-logger.py`

**Использование:**
```bash
# Начать сессию
python .vscode/chat-logger.py --session "feature-implementation"

# Добавить сообщение (из скрипта)
python .vscode/chat-logger.py --role user --content "Текст сообщения"

# Завершить сессию
python .vscode/chat-logger.py --end
```

**Логи сохраняются в:** `.chat-cache/` (исключено из git)

---

## 🚀 Быстрый старт

### Первый запуск

1. **Установите расширения:**
   - `Ctrl+Shift+X` → `Install Recommended Extensions`

2. **Активируйте venv:**
   - `Ctrl+Shift+P` → `Python: Select Interpreter` → `.venv`

3. **Запустите задачу:**
   - `Ctrl+Shift+P` → `Tasks: Run Task` → `make install`

### Частые операции

| Задача | Команда |
|--------|---------|
| Запустить все тесты | `Ctrl+Shift+R` |
| Отформатировать код | `Ctrl+Shift+F` |
| Открыть терминал | `Ctrl+`` |
| Запустить Docker | `Ctrl+Shift+C` |
| Посмотреть задачи | `Ctrl+Shift+T` |

---

## 📊 Рекомендованные расширения

### Обязательные:
- ✅ **Python** (`ms-python.python`)
- ✅ **Pylance** (`ms-python.vscode-pylance`)
- ✅ **Ruff** (`charliermarsh.ruff`)
- ✅ **Docker** (`ms-azuretools.vscode-docker`)
- ✅ **YAML** (`redhat.vscode-yaml`)
- ✅ **Markdown All in One** (`yzhang.markdown-all-in-one`)
- ✅ **GitLens** (`eamodio.gitlens`)

### Для KODA CLI:
- ✅ **Terminal Tabs** (`spgerrin.terminal-tabs`)
- ✅ **Task Explorer** (`spgerrin.task-explorer`)
- ✅ **Output Colorizer** (`bierner.output-colorizer`)
- ✅ **Git Graph** (`mhutchie.git-graph`)

**Установка:** `Ctrl+Shift+X` → вставить ID → Install

---

## 📁 Структура `.vscode/`

```
.vscode/
├── settings.json          # Глобальные настройки
├── tasks.json             # Задачи (Makefile)
├── keybindings.json       # Горячие клавиши
├── extensions.json        # Рекомендуемые расширения
├── python.snippets        # Снаппеты
└── chat-logger.py         # Утилита логирования
```

---

## 🔧 Кастомизация

### Изменение горячих клавиш

Откройте `.vscode/keybindings.json` и добавьте/измените:
```json
{
  "key": "ctrl+shift+y",
  "command": "workbench.action.tasks.runTask",
  "args": "make lint"
}
```

### Добавление новых задач

Откройте `.vscode/tasks.json` и добавьте:
```json
{
  "label": "make my-custom-task",
  "type": "shell",
  "command": "make my-custom-task",
  "group": "build"
}
```

### Настройка логирования чатов

В `.vscode/settings.json`:
```json
{
  "chat.logger.enabled": true,
  "chat.logger.outputDir": ".chat-cache",
  "chat.logger.autoSave": true
}
```

---

## 📝 Следующие шаги

- [ ] Протестировать все горячие клавиши
- [ ] Настроить автоматическое логирование чатов
- [ ] Добавить кастомные задачи для ваших workflow
- [ ] Создать документацию по расширению снаппетов

---

**Отчёт сохранён в:** `.reports/vscode-setup-report.md`
**Логи чатов:** `.chat-cache/` (не коммитится в git)

*Сгенерировано KODA CLI, 15 мая 2026 г.*
