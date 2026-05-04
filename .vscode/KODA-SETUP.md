# Koda CLI Setup Guide

## 🚀 Настройка Koda CLI в VS Code

### 1. Установленные расширения

VS Code автоматически предложит установить рекомендуемые расширения при открытии проекта. Кликни "Install All" в панели Extensions.

**Ключевые расширения:**
- **Python** (ms-python.python) — поддержка Python
- **Pylance** (ms-python.vscode-pylance) — языковой сервер
- **Black Formatter** (ms-python.black-formatter) — форматирование
- **isort** (ms-python.isort) — сортировка импортов
- **Docker** (ms-azuretools.vscode-docker) — работа с контейнерами
- **Kubernetes** (ms-kubernetes-tools.vscode-kubernetes-tools) — K8s манифесты

### 2. Проверка Koda CLI

Открой терминал (Ctrl+`) и выполни:

```bash
koda --version
```

Если команда не найдена, добавь в PATH:
```powershell
$env:PATH += ";$env:APPDATA\npm"
```

### 3. Активация виртуального окружения

При первом открытии проекта VS Code предложит выбрать интерпретатор. Выбери:
- `.venv/Scripts/python.exe`

Или вручную:
```bash
# Git Bash
source .venv/bin/activate

# PowerShell
.venv\Scripts\Activate.ps1
```

### 4. Запуск Koda CLI

**Из терминала:**
```bash
koda
```

**Или через Command Palette (Ctrl+Shift+P):**
- Выбери `Debug: Select and Start Debugging` → `Python: Koda CLI`

### 5. Основные команды Koda

```bash
# Запуск агента
koda

# Анализ проекта
koda scan

# Генерация кода
koda generate

# Помощь
koda --help
```

### 6. Отладка

Используй **Debug Configurations** (F5):
- **Python: pytest текущий файл** — запуск тестов
- **Python: FastAPI - Cloud Reason** — запуск API
- **Python: Streamlit - IT Compass** — запуск UI

### 7. Горячие клавиши

| Действие | Комбинация |
|----------|------------|
| Открыть терминал | `` Ctrl+` `` |
| Командная панель | `Ctrl+Shift+P` |
| Запуск/отладка | `F5` |
| Остановить отладку | `Shift+F5` |
| Форматирование | `Shift+Alt+F` |
| Организация импортов | `Shift+Alt+O` |
| Поиск в файлах | `Ctrl+Shift+F` |

### 8. Рабочие процессы

**Ежедневная разработка:**
1. Открой проект в VS Code
2. Убедись, что активировано `.venv`
3. Запусти `koda` в терминале
4. Работай с кодом — форматирование и линтинг автоматические при сохранении

**Запуск тестов:**
```bash
# Через терминал
make test

# Или через Debug Configurations
```

**Запуск сервисов:**
```bash
# Docker Compose
make dev

# Или отдельные сервисы через Debug Configurations
```

### 9. Решение проблем

**Koda не найден:**
```powershell
# Проверь установку
npm list -g koda

# Переустанови
npm uninstall -g koda
npm install -g koda
```

**Нет активации окружения:**
```powershell
# В PowerShell может потребоваться выполнить
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Проблемы с Pylance:**
- Перезагрузи окно VS Code (`Ctrl+Shift+P` → `Developer: Reload Window`)
- Проверь `python.analysis.extraPaths` в настройках

### 10. Koda CLI — что он умеет

Koda CLI — это интерактивный CLI-агент для разработки ПО:

- **Анализ кода** — понимание структуры проекта
- **Генерация кода** — создание файлов и функций
- **Рефакторинг** — улучшение существующего кода
- **Тестирование** — написание и запуск тестов
- **Документация** — генерация и обновление docs
- **Поиск информации** — навигация по кодовой базе
- **Интеграция с ИИ** — использование LLM для помощи

### 11. Интеграция с проектом

Твой проект уже настроен для работы с Koda:

- ✅ `.kodacli/KODA.md` — контекст проекта
- ✅ `codeassistant/context.md` — контекст для ИИ-ассистента
- ✅ `pyproject.toml` — зависимости и настройки
- ✅ `.pre-commit-config.yaml` — pre-commit хуки
- ✅ `Makefile` — команды для разработки

### 12. Следующие шаги

1. **Установи рекомендуемые расширения** (появится уведомление)
2. **Проверь версию Koda**: `koda --version`
3. **Запусти Koda**: `koda` в терминале
4. **Изучи документацию**: `docs/` папка
5. **Запусти тесты**: `make test`

---

**Готово!** Koda CLI настроен и готов к работе. 🚀
