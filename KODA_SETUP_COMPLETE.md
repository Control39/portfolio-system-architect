# ✅ Koda CLI Настроен и Готов!

## Что сделано

### 1. Конфигурация VS Code
- ✅ `.vscode/settings.json` — настройки Python, Black, isort, pytest, Pylance
- ✅ `.vscode/launch.json` — конфиги отладки (тесты, FastAPI, Streamlit, Koda)
- ✅ `.vscode/extensions.json` — рекомендуемые расширения
- ✅ `.vscode/KODA-SETUP.md` — полное руководство

### 2. Контекст проекта
- ✅ `.kodacli/KODA.md` — скопирован контекст для Koda CLI

### 3. Проверка окружения
- ✅ Koda CLI v0.3.5 установлен и работает
- ✅ Все зависимости в `.venv` установлены (black, isort, pytest, ruff, mypy и др.)
- ✅ Python 3.10+ с виртуальным окружением активирован

## Как начать работать

### Быстрый старт

1. **Установи расширения** (если ещё не установлены):
   - Нажми `Ctrl+Shift+X`
   - Найди "Recommended Extensions"
   - Кликни "Install All"

2. **Запусти Koda CLI**:
   ```bash
   # В терминале Git Bash (открыть через Ctrl+`)
   koda
   ```

3. **Или через Command Palette**:
   - `Ctrl+Shift+P` → `Debug: Select and Start Debugging` → `Python: Koda CLI`

## Доступные команды

### Koda CLI
```bash
koda                      # Запуск интерактивного агента
koda scan                 # Анализ проекта
koda --help              # Показать все команды
```

### Разработка
```bash
make dev                 # Запуск всех сервисов через Docker
make test                # Запуск тестов с покрытием
make lint                # Проверка кода (ruff, black, mypy)
make format              # Форматирование кода
make docker-build        # Сборка Docker-образов
make docs                # Запуск документации
```

### Отладка в VS Code (F5)
- **Python: Текущий файл** — запустить открытый файл
- **Python: pytest текущий файл** — запустить тесты в файле
- **Python: pytest весь проект** — запустить все тесты
- **Python: FastAPI - Cloud Reason** — запустить API сервис
- **Python: Streamlit - IT Compass** — запустить UI приложение

## Рекомендуемые расширения

| Расширение | Назначение |
|------------|------------|
| Python | Основная поддержка Python |
| Pylance | Статический анализ и IntelliSense |
| Black Formatter | Форматирование кода |
| isort | Сортировка импортов |
| Docker | Работа с контейнерами |
| Kubernetes | K8s манифесты и деплой |
| Git Graph | Визуализация истории Git |
| Coverage Gutters | Покрытие кода тестами |
| Markdown Mermaid | Предпросмотр диаграмм |

## Горячие клавиши

| Действие | Комбинация |
|----------|------------|
| Открыть терминал | `` Ctrl+` `` |
| Командная панель | `Ctrl+Shift+P` |
| Поиск в файлах | `Ctrl+Shift+F` |
| Запуск/отладка | `F5` |
| Остановить отладку | `Shift+F5` |
| Форматирование | `Shift+Alt+F` |
| Организация импортов | `Shift+Alt+O` |

## Проверка работоспособности

### 1. Проверь версию Koda
```bash
koda --version
# Ожидаем: 0.3.5
```

### 2. Проверь зависимости
```bash
make lint
make test
```

### 3. Проверь сервисы
```bash
make dev
# Проверь: http://localhost:8501 (IT-Compass UI)
```

## Что дальше?

1. **Изучи документацию**:
   - `docs/INDEX.md` — общий обзор
   - `docs/QUICKSTART.md` — быстрое начало
   - `.vscode/KODA-SETUP.md` — детали настройки

2. **Запусти тесты**:
   ```bash
   make test
   ```

3. **Запусти Koda**:
   ```bash
   koda
   ```

4. **Начни разработку**:
   - Создай новую ветку: `git checkout -b feature/your-feature`
   - Напиши код
   - Запусти тесты: `make test`
   - Закоммить: `git commit -m "feat: description"`

## Решение проблем

### Koda не найден
```powershell
# Проверь PATH
$env:PATH

# Переустанови
npm uninstall -g koda
npm install -g koda
```

### Окружение не активируется
```powershell
# PowerShell может требовать изменения политики
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Нет форматирования при сохранении
- Проверь: `File` → `Preferences` → `Settings` → `Editor: Format On Save`
- Убедись, что выбран Black Formatter как дефолтный

## Контакты и поддержка

- **Документация проекта**: `docs/`
- **Контрибуция**: `CONTRIBUTING.md`
- **Архитектура**: `ARCHITECTURE.md`
- **Koda CLI**: `koda --help`

---

**Готово!** 🎉 Ты можешь начать работу с Koda CLI прямо сейчас.

Просто открой терминал и введи:
```bash
koda
```
