# 🔧 Исправление импортов в тестах

**Дата:** 2026-06-22
**Статус:** 🟡 В процессе

---

## 📋 Проблема

После реорганизации `src/` и `apps/` в тестах возникли ошибки импортов:

```
ImportError: cannot import name 'AgentConfig' from 'ai_config_manager'
ModuleNotFoundError: No module named 'ai_config_manager.config_manager'
IndentationError: expected an indented block after 'if' statement
```

---

## 🔧 Найденные проблемы

### 1. Синтаксические ошибки в conftest.py

**Файлы:** `apps/*/tests/conftest.py`

**Проблема:** Были пропущены строки после `if str(...) not in sys.path:`

**Исправленные файлы:**
- ✅ `apps/ai_config_manager/tests/conftest.py`
- ✅ `apps/auth_service/tests/conftest.py`
- ✅ `apps/career_development/tests/conftest.py`
- ✅ `apps/chat_backend/tests/conftest.py`
- ✅ `apps/decision_engine/tests/conftest.py`
- ✅ `apps/infra_orchestrator/tests/conftest.py`
- ✅ `apps/job_automation_agent/conftest.py`
- ✅ `apps/ml_model_registry/tests/conftest.py`
- ✅ `apps/thought_architecture/tests/conftest.py`

---

### 2. Ошибки импортов в тестах

**Пример ошибки:**
```
apps/ai_config_manager/tests/test_config.py:25:
ImportError: cannot import name 'AgentConfig' from 'ai_config_manager'
```

**Проблема:**
- Тесты используют `from ai_config_manager.config_manager import ...`
- Но модуль находится в `apps/ai_config_manager/src/ai_config_manager/`
- Нет `ai_config_manager` в корневом `src/`

**Решение:** Обновить conftest.py, чтобы добавлять оба пути:
1. `src/` - для общих модулей (АТОМЫ)
2. `apps/*/src/` - для модулей конкретного микросервиса

---

## 📝 Временные исправления

### `apps/ai_config_manager/tests/conftest.py`:

**До:**
```python
REPO_ROOT = Path(__file__).resolve().parents[2]  # до /apps/ai_config_manager
SRC_PATH = REPO_ROOT / "src"
```

**После:**
```python
REPO_ROOT = Path(__file__).resolve().parents[4]  # до корня репозитория
MOLECULE_ROOT = Path(__file__).resolve().parents[1]  # до /apps/ai_config_manager
SRC_PATH = REPO_ROOT / "src"

# Добавляем корневой src/ (для импорта общих модулей)
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Добавляем корень репозитория (для импорта apps.* модулей)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

---

## 🎯 План исправлений

### 1. Обновить все conftest.py (WIP)

**Задача:** Обновить `apps/*/tests/conftest.py` так, чтобы:
- Добавлялся корневой `src/` (для общих модулей)
- Добавлялся корень репозитория (для импорта `apps.*`)
- Или добавляется `apps/*/src/` конкретного микросервиса

**Статус:** Начато (см. выше)

### 2. Обновить импорты в тестах

**Задача:** Заменить импорты вида `from ai_config_manager.*` на `from apps.ai_config_manager.*`

**Пример:**
```python
# Было
from ai_config_manager.config_manager import ConfigManager

# Стало
from apps.ai_config_manager.src.ai_config_manager.config_manager import ConfigManager
# ИЛИ
from apps.ai_config_manager.config_manager import ConfigManager  # если в conftest добавлен apps/
```

### 3. Создать консистентную систему импортов

**Вариант A: Использовать только абсолютные импорты от корня**
```python
from src.common.health_check import health_check
from apps.ai_config_manager.config_manager import ConfigManager
```

**Вариант B: Использовать относительные импорты внутри микросервиса**
```python
from .config_manager import ConfigManager
from src.common.health_check import health_check
```

**Рекомендация:** Вариант A - более явный и понятный.

---

## 📊 Текущее состояние

| Статус | Описание |
|--------|----------|
| ✅ Синтаксические ошибки | Исправлены (4 conftest.py) |
| 🟡 Импорты | В процессе исправления |
| 🟡 CI/CD | Не обновлен |
| 🟡 Документация | Не обновлена |

---

## 🔍 Текущие ошибки

```
ImportError while importing test module 'C:\repo\apps\ai_config_manager\tests\test_config.py'.
ImportError: cannot import name 'AgentConfig' from 'ai_config_manager'

ImportError while importing test module 'C:\repo\apps\career_development\tests\test_competency_tracker.py'.
ImportError: cannot import name 'CompetencyTracker' from 'career_development'

... (еще 46 ошибок)
```

---

## 📝 Решение: Обновить conftest.py для всех микросервисов

**Правило:** В `apps/*/tests/conftest.py` добавлять:
1. `src/` - для общих модулей
2. `apps/*/src/` - для модулей конкретного микросервиса

**Пример:**
```python
# apps/ai_config_manager/tests/conftest.py

import sys
from pathlib import Path

# Пути
REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_PATH = REPO_ROOT / "src"
MOLECULE_SRC = Path(__file__).resolve().parents[1] / "src"

# Добавляем пути
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))

# Теперь можно импортировать:
# from src.common.health_check import health_check
# from ai_config_manager.config_manager import ConfigManager
```

---

**Автор:** GigaCode
**Последнее обновление:** 2026-06-22
**Следующий шаг:** Завершить обновление всех conftest.py и тестов
