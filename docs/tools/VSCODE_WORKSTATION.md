# 💻 VS Code как рабочая станция ИИ‑архитектора


> Как я превратила VS Code в центр управления когнитивной экосистемой.



---


## 🧰 Настроенные компоненты


| Файл | Назначение |
|------|----------|
| `.vscode/settings-default.json` | Базовые настройки (форматирование, Python path) |
| `.vscode/tasks.json` | Задачи: `make test`, `make lint`, `docker-up` |
| `.vscode/keybindings.json` | Горячие клавиши для автоматизации |
| `.vscode/extensions.json` | Рекомендованные расширения |
| `.vscode/python.snippets` | Снаппеты: `kodalogs`, `fastapi`, `pytest` |
| `.vscode/chat-logger.py` | Логирование чатов с ИИ‑агентами |

---

## ⚙️ Быстрый старт


1. Открой репозиторий в VS Code.
2. Нажми `Ctrl+Shift+X` → «Install Recommended Extensions».
3. Выбери интерпретатор: `.venv`.
4. Запусти: `Ctrl+Shift+I` → установка зависимостей.


---

## 🔄 Горячие клавиши


| Команда | Клавиша | Действие |
|--------|--------|--------|
| Установка зависимостей | `Ctrl+Shift+I` | `make install` |
| Запуск тестов | `Ctrl+Shift+R` | `make test` |
| Линтинг | `Ctrl+Shift+L` | `make lint` |
| Форматирование | `Ctrl+Shift+F` | `make format` |
| Docker Up | `Ctrl+Shift+C` | `make docker-up` |
| Docker Down | `Ctrl+Shift+X` | `make docker-down` |
| Открыть терминал | `Ctrl+\`` | Переключение |
| Задачи | `Ctrl+Shift+T` | Список make‑задач |

---

## 📜 Логирование чатов с ИИ

**Утилита:** `.vscode/chat-logger.py`

**Зачем:**
* Аудит решений.
* Анализ эффективности промптов.
* Обучение агента на прошлых диалогах.

**Логи:** `.chat-cache/` (не коммитятся).

**Пример:**
```bash
python .vscode/chat-logger.py --session "feature-implementation" --role user --content "Как реализовать loose coupling?"
```

---

## 🛠️ Расширения


**Обязательные:**
* `ms-python.python`
* `ms-python.vscode-pylance`
* `charliermarsh.ruff`
* `ms-azuretools.vscode-docker`
* `redhat.vscode-yaml`

**Для ИИ‑архитектуры:**
* `spgerrin.terminal-tabs` — несколько терминалов.
* `spgerrin.task-explorer` — визуальный запуск задач.
* `eamodio.gitlens` — анализ коммитов.

---

## 🔄 Интеграция с Makefile

Все задачи связаны с Makefile:
```makefile
install:
	pip install -r requirements.txt

test:
	python -m pytest tests/

lint:
	ruff check .

format:
	ruff check . --fix
	black .
```

---

## 📁 Структура

```
.vscode/
├── settings-default.json    # Шаблон
├── tasks.json               # Задачи
├── keybindings.json         # Клавиши
├── extensions.json          # Расширения
├── python.snippets          # Снаппеты
└── chat-logger.py           # Логгер
```
