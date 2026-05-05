# 🔍 Отчёт: Статический анализ Sphinx-конфигурации

**Дата:** 5 мая 2026 г.  
**Анализируемые файлы:** `docs/api/conf.py`, `docs/api/index.rst`  
**Статус:** ✅ Анализ завершён (без внесения изменений)

---

## 📋 Таблица найденных проблем

| Файл | Строка | Старое значение | Ожидаемое значение | Серьёзность |
|---------------------|-------------|-------------------|------------------------|-------------|
| `conf.py` | 27 | `it-compass` | `it_compass` | 🔴 Критично |
| `conf.py` | 27 | `cloud-reason` | `decision-engine` | 🔴 Критично |
| `conf.py` | 27 | `career-development` | `career_development` | 🟡 Средне |
| `conf.py` | 27 | `ml-model-registry` | `ml-model-registry` | ✅ ОК |
| `index.rst` | 8 | `it_compass <it_compass/modules>` | `it_compass <it_compass.modules>` | 🟡 Средне |
| `index.rst` | 9 | `cloud_reason <cloud_reason/modules>` | `decision_engine <decision_engine.modules>` | 🔴 Критично |
| `index.rst` | 10 | `career_development <career_development/modules>` | `career_development <career_development.modules>` | 🟡 Средне |
| `index.rst` | 11 | `ml_model_registry <ml_model_registry/modules>` | `ml_model_registry <ml_model_registry.modules>` | 🟡 Средне |
| `index.rst` | 14 | `apps.it_compass.src.main` | `apps.it_compass.src.main` | ✅ ОК |
| `index.rst` | 17 | `apps.cloud_reason.cloud_reason.main` | `apps.decision_engine.main` | 🔴 Критично |
| `index.rst` | 20 | `apps.career_development.career_development_system.main` | `apps.career_development.src.core.main` (не существует) | 🔴 Критично |
| `index.rst` | 23 | `apps.ml_model_registry.ml_model_registry.main` | `apps.ml_model_registry.src.main` | 🔴 Критично |
| `requirements-dev.txt` | — | sphinx не указан | Добавить `sphinx`, `furo`, `sphinx-autodoc-typehints` | 🔴 Критично |

---

## 📊 Анализ по категориям

### 1. Пути к сервисам в `conf.py` (строка 27)

```python
# ТЕКУЩЕЕ (невалидное):
for app in ["it-compass", "cloud-reason", "career-development", "ml-model-registry"]:

# ОЖИДАЕМОЕ:
for app in ["it_compass", "decision-engine", "career_development", "ml-model-registry"]:
```

**Проблема:** Используются дефисы вместо подчёркиваний там, где это не соответствует именам папок.

---

### 2. Имена модулей в `index.rst`

| Отображаемое имя | Указанный путь | Реальная структура |
|----------------|----------------|---------------------|
| `it_compass` | `it_compass/modules` | ❌ Не существует RST-файла, нужно `it_compass.modules` |
| `cloud_reason` | `cloud_reason/modules` | ❌ Папка переименована в `decision-engine` |
| `career_development` | `career_development/modules` | ❌ RST-файл не существует |
| `ml_model_registry` | `ml_model_registry/modules` | ❌ RST-файл не существует |

**Проблема с automodule:**

```python
# apps.cloud_reason.cloud_reason.main — такого модуля нет
# Реальный путь: apps.decision-engine/main.py

# apps.career_development.career_development_system.main — такого модуля нет
# Реальная структура: apps/career_development/src/ — нет main.py

# apps.ml_model_registry.ml_model_registry.main — неверный путь
# Реальный путь: apps.ml_model_registry/src/main.py
```

---

### 3. Зависимости

**Проверка `requirements-dev.txt`:**
- ❌ `sphinx` — не найден
- ❌ `furo` — не найден
- ❌ `sphinx-autodoc-typehints` — не найден

**Вывод:** Sphinx-документация не может быть собрана без установки зависимостей.

---

### 4. Актуальность Sphinx в проекте

**Текущее состояние:**
- ✅ MkDocs используется как основная система документации (`mkdocs.yml` в корне)
- ❌ Sphinx-конфигурация в `docs/api/` — устарела, не поддерживается
- ❌ Нет ссылок на Sphinx в `Makefile` или `mkdocs.yml`
- ❌ Нет CI/CD pipeline для Sphinx-сборки

**Вывод:** Sphinx-документация — артефакт прошлого, основная документация ведётся через MkDocs.

---

## 🎯 Рекомендации

| Приоритет | Действие | Обоснование |
|-----------|-------------|-------------|
| 🔴 **Высокий** | **Удалить папку `docs/api/`** | Sphinx не используется, конфигурация устарела после PR #84, все ссылки невалидны |
| 🟡 **Средний** | Перенести API-документацию в MkDocs формат (`docs/api/*.md`) | MkDocs — основная система документации проекта |
| 🟢 **Низкий** | Если Sphinx нужен — полностью переписать `conf.py` и `index.rst` | Требует ~2-3 часа работы, но не имеет смысла при наличии MkDocs |

---

## 📝 Итоговый вердикт

**Рекомендация:** **Удалить `docs/api/` целиком и перенести API-документацию в MkDocs формат.**

**Обоснование:**
1. Sphinx не указан в зависимостях
2. Все пути к сервисам невалидны после реорганизации
3. MkDocs уже используется и интегрирован в CI/CD
4. Поддержка двух систем документации избыточна

**Альтернатива:** Если нужна автоматическая генерация API-документации из docstrings — использовать `sphinx-apidoc` + MkDocs через `m2r2` или `autodoc2` плагин.

---

## 📂 Исходные файлы

- `docs/api/conf.py` — 28 строк
- `docs/api/index.rst` — 24 строки
- `requirements-dev.txt` — Sphinx-зависимости отсутствуют

---

*Отчёт сгенерирован Koda CLI, 5 мая 2026 г.*
