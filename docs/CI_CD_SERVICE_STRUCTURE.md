# CI/CD для проверки структуры сервисов

> **Версия:** 1.0.0  
> **Дата:** 18 мая 2026 г.

---

## 🎯 Назначение

Автоматическая проверка соответствия всех сервисов стандарту структуры при каждом коммите и пулл-реквесте.

---

## 📦 Компоненты

### 1. GitHub Actions Workflow

**Файл:** `.github/workflows/service-structure.yml`

**Запускается:**
- При push в `main` и `develop`
- При создании/обновлении Pull Request
- Только если изменены файлы в `apps/`

**Что делает:**
1. Устанавливает Python 3.11
2. Устанавливает зависимости (fastapi, uvicorn, pytest)
3. Запускает `scripts/check_service_structure.py`
4. Блокирует merge если проверка не пройдена

### 2. Pre-commit Hook

**Файл:** `.pre-commit-config.yaml` (секция `check-service-structure`)

**Запускается:**
- Автоматически перед каждым коммитом
- При ручном запуске: `pre-commit run --all-files`

**Что делает:**
1. Проверяет структуру всех сервисов
2. Возвращает ошибку, если есть проблемы
3. Блокирует коммит до исправления

### 3. Скрипты проверки

**Файлы:**
- `scripts/check_service_structure.py` — проверка соответствия
- `scripts/auto_fix_service_structure.py` — автоматическое исправление

---

## 🛠️ Установка

### 1. Установить pre-commit hooks

```bash
# Установка pre-commit
pip install pre-commit

# Установка hooks в репозиторий
pre-commit install

# Проверка установки
pre-commit run --all-files
```

### 2. Проверить GitHub Actions

Убедитесь, что workflow активен:
1. Перейдите в репозиторий на GitHub
2. Откройте вкладку "Actions"
3. Найдите workflow "Service Structure Check"
4. Убедитесь, что он включён (toggle в правом верхнем углу)

---

## 📊 Использование

### Проверка перед коммитом

```bash
# Автоматическая проверка при коммите
git add .
git commit -m "feat: новый фича"
# Если есть проблемы — коммит заблокирован
```

### Ручная проверка всех сервисов

```bash
# Проверка всех сервисов
python scripts/check_service_structure.py

# Проверка конкретного сервиса
python scripts/check_service_structure.py --service auth_service

# Автоматическое исправление
python scripts/auto_fix_service_structure.py --all
```

### Проверка в CI/CD

При создании PR:
1. GitHub Actions автоматически запускает проверку
2. Результат отображается в разделе "Checks"
3. Если проверка не пройдена — merge заблокирован

---

## 📋 Что проверяется

### Обязательные файлы

| Файл | Описание |
|------|----------|
| `main.py` или `app.py` | Entry point сервиса |
| `README.md` | Документация с 7 секциями |
| `requirements.txt` | Зависимости |
| `Dockerfile` | Контейнеризация |

### Обязательные директории

| Директория | Описание |
|------------|----------|
| `src/` | Исходный код |
| `tests/` | Тесты |

### Качество README

Проверяется наличие 7 секций:
1. Purpose
2. Features
3. API
4. Dependencies
5. Deployment
6. Contributing

---

## 🔧 Настройка

### Исключение сервисов

Чтобы исключить сервис из проверки, добавьте его в `excluded` в `check_service_structure.py`:

```python
excluded = {"__pycache__", "tests", "utils", "__init__.py", "my-service"}
```

### Изменение требований

Для изменения требований к структуре:
1. Отредактируйте `scripts/check_service_structure.py`
2. Обновите `docs/SERVICE_STRUCTURE_STANDARD.md`
3. Запустите тесты

---

## 📊 Метрики

### Текущее состояние

| Показатель | Значение |
|------------|----------|
| Сервисов всего | 15 |
| Соответствуют стандарту | 15 (100%) |
| Средний балл | 100% |

### История изменений

| Дата | Изменение | Результат |
|------|-----------|-----------|
| 2026-05-18 | Создан workflow | 15/15 (100%) |
| 2026-05-18 | Добавлен pre-commit hook | Автоматическая проверка |

---

## 🚨 Устранение проблем

### Pre-commit check failed

```bash
# Показать проблемы
python scripts/check_service_structure.py

# Автоматически исправить
python scripts/auto_fix_service_structure.py --all

# Повторить проверку
pre-commit run --all-files
```

### GitHub Actions failed

1. Откройте PR на GitHub
2. Перейдите в вкладку "Checks"
3. Нажмите на "Service Structure Check"
4. Посмотрите логи ошибки
5. Исправьте проблемы локально
6. Push изменений

### Отключение проверки (не рекомендуется)

```bash
# Временно отключить pre-commit
git commit --no-verify -m "message"

# Отключить в GitHub Actions
# Отредактируйте .github/workflows/service-structure.yml
# или удалите workflow
```

---

## 📚 Ссылки

- [Стандарт структуры сервиса](../docs/SERVICE_STRUCTURE_STANDARD.md)
- [Скрипт проверки](../scripts/check_service_structure.py)
- [Скрипт исправления](../scripts/auto_fix_service_structure.py)
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Pre-commit docs](https://pre-commit.com/)

---

*Последнее обновление: 18 мая 2026 г.*
