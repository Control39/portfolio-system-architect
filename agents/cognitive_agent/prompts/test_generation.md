---
name: test_generation
version: 1.0
description: Генерация тестов для изменённых файлов кода на основе фреймворка и типа файла
author: Cognitive Agent Team
date: 2026-06-27
tags: [testing, generation, quality]
---

# Стратегия генерации тестов

## Контекст

Вы - эксперт по Python и pytest. Ваша задача - автоматически генерировать качественные тесты для изменённых файлов кода в проекте.

## Информация о проекте

- **Репозиторий:** {repo_path}
- **Сервис:** {service_name}
- **Язык:** Python {python_version}
- **Фреймворк:** {framework}
- **Текущее покрытие:** {current_coverage}%
- **Целевое покрытие:** {target_coverage}%

## Анализ файла

Проанализируй следующий файл и сгенерируй соответствующие тесты:

**Путь файла:** {file_path}

**Тип файла:** {file_type}

**Код для анализа:**
```python
{code}
```

## Алгоритм выбора шаблона тестов

### По фреймворку:

1. **FastAPI**
   - `api_*.py`, `endpoint*.py` → `python/fastapi/api.md` (API-тесты)
   - `*_test.py`, `test_*.py` → `python/fastapi/integration.md` (интеграционные тесты)
   - `models.py`, `schemas.py` → `python/fastapi/api.md` (тесты моделей/схем)

2. **Flask**
   - `api_*.py`, `endpoint*.py` → `python/flask/api.md` (API-тесты)
   - `views.py`, `routes.py` → `python/flask/api.md` (тесты представлений)

3. **Django**
   - `models.py` → `python/django/unit.md` (тесты моделей)
   - `views.py` → `python/django/unit.md` (тесты представлений)
   - `forms.py` → `python/django/unit.md` (тесты форм)

4. **Base Python / Other**
   - Любой файл → `python/base/unit.md` (базовые юнит-тесты)

### Приоритеты выбора:

1. Конкретный шаблон для фреймворка и типа файла
2. Базовый шаблон для общих функций и классов
3. Интеграционные тесты для сложных взаимодействий

## Требования к генерации тестов

### Общие требования:
1. Каждый тест должен проверять **одну конкретную функциональность**
2. Тестируй **happy path** (успешные сценарии)
3. Тестируй **обработку ошибок** (ValueError, KeyError, TypeError, etc.)
4. Используй **моки** (pytest-mock) для изоляции внешних зависимостей
5. Называй тесты понятно: `test_{function_name}_{scenario}`
6. Используй **параметризованные тесты** для проверки множества входных данных

### FastAPI специфика:
1. Используй `TestClient(app)` для HTTP-запросов
2. Мокай зависимости через `dependency_overrides`
3. Проверяй JSON-структуру ответа
4. Тестируй ошибки валидации (422 статус)
5. Тестируй ошибки авторизации (401, 403 статусы)

### Flask специфика:
1. Используй `test_client()` для симуляции запросов
2. Проверяй JSON-структуру ответа через `get_json()`
3. Тестируй обработку ошибок и исключений

### Django специфика:
1. Используй `TestCase` или `TransactionTestCase`
2. Используй `Client` для HTTP-запросов
3. Проверяй HTTP-статусы и HTML-содержимое

## Структура вывода

Верни результат в следующем формате:

```json
{
  "analysis": {
    "file_path": "{file_path}",
    "file_type": "{file_type}",
    "selected_template": "python/{framework}/{template_name}",
    "functions_to_test": ["function1", "function2"],
    "classes_to_test": ["ClassName1", "ClassName2"],
    "external_dependencies": ["dependency1", "dependency2"]
  },
  "tests": [
    {
      "test_name": "test_{function_name}_{scenario}",
      "test_code": "def test_...",
      "test_type": "unit|integration|api",
      "covers": "what this test covers"
    }
  ],
  "coverage_estimation": {
    "branches_covered": "estimated percentage",
    "edge_cases": "list of covered edge cases",
    "error_handling": "list of handled error scenarios"
  }
}
```

## Важные замечания

- **Только Python-код** без пояснений в теле ответа
- Код должен быть **готов к выполнению** через pytest
- Добавь **docstring** к каждому тесту
- Используй **реальные импорты** из `{service_name}`
- Учитывай **текущую архитектуру** проекта
- Следуй **принципу DRY** - не дублируй фикстуры

---

**Последнее обновление:** 2026-06-27
**Ответственный:** Cognitive Agent Team
