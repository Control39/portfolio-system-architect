# Генерация тестов в Cognitive Agent

## Обзор

Модуль `test_generator.py` обеспечивает автоматическую генерацию тестов для Python кода с помощью PromptEngine и LLM.

## Архитектура

```
TestGenerator (Layer 4: Test Generation)
    ↓ Uses
PromptEngine (Layer 2: Strategy Manager)
    ↓ Uses
Prompt Templates (Layer 3: Business Logic)
    ↓ Executes via
LLM Client (OpenAI, GigaChat, Ollama)
```

## Возможности

1. **Автоматическое определение фреймворка**
   - FastAPI → `python/fastapi/api`, `python/fastapi/integration`
   - Flask → `python/flask/api`
   - Django → `python/django/unit`
   - Base Python → `python/base/unit`

2. **Автоматическое определение типа файла**
   - API-файлы → API-тесты
   - Models → Юнит-тесты моделей
   - Integration → Интеграционные тесты

3. **Генерация тестов для одного файла или директории**
   - `generate_test_for_file()` - один файл
   - `generate_tests_for_directory()` - все файлы в директории

4. **Применение сгенерированных тестов**
   - `apply_generated_tests()` - добавление к существующему файлу или перезапись

## Использование

### Простая генерация для одного файла

```python
from pathlib import Path
from agents.cognitive_agent.src.test_generator import TestGenerator

# Инициализация
generator = TestGenerator(project_path="C:/repo")

# Генерация (требуется LLM клиент)
result = await generator.generate_test_for_file(
    file_path="apps/decision_engine/core/models.py",
    llm_client=your_llm_client,
    target_coverage=85,
)

print(result["output"])  # Сгенерированный код тестов
```

### Генерация для директории

```python
results = await generator.generate_tests_for_directory(
    directory="apps/decision_engine/core",
    llm_client=your_llm_client,
    target_coverage=85,
    file_patterns=["*.py"],
)

for result in results:
    if result["success"]:
        print(f"Generated tests for {result['file_path']}")
```

### Применение сгенерированных тестов

```python
generator.apply_generated_tests(
    test_code=result["output"],
    output_file="apps/decision_engine/tests/test_models.py",
    mode="append",  # или "overwrite"
)
```

## Интеграция с Autonomous Agent

```python
# В autonomous_agent.py
self.test_generator = TestGenerator(
    project_path=str(self.project_path),
    prompts_dir=prompts_dir,
)

# Генерация при сканировании
results = await self.test_generator.generate_tests_for_directory(
    directory="apps/my_service/src",
    llm_client=self.ai_provider.llm_client,
)
```

## Порядок действий TestGenerator

1. **Определение фреймворка** - анализирует импорты в файле
2. **Определение типа файла** - анализирует имя файла и содержимое
3. **Выбор шаблона** - выбирает подходящий prompt template
4. **Контекст** - готовит контекст для LLM (код, сервис, цель покрытия)
5. **Генерация** - отправляет prompt LLM через execute_strategy
6. **Результат** - возвращает сгенерированный код тестов

## Примеры

### FastAPI API

```python
# Вход: apps/user_service/api/users.py
# Фреймворк: fastapi
# Тип: api
# Шаблон: python/fastapi/api.md

# Генерирует:
# - tests для endpoints
# - тесты авторизации
# - тесты валидации
# - тесты ошибок
```

### Django Models

```python
# Вход: apps/compass/models/competency.py
# Фреймворк: django
# Тип: models
# Шаблон: python/django/unit.md

# Генерирует:
# - tests для моделей
# - tests для методов
# - tests для валидации
```

### Base Python

```python
# Вход: apps/config/config.py
# Фреймворк: base
# Тип: unit
# Шаблон: python/base/unit.md

# Генерирует:
# - tests для функций
# - tests для классов
# - tests для обработки ошибок
```

## Интеграция с PromptEngine

TestGenerator использует `PromptEngine.execute_strategy()` для выполнения LLM запросов:

```python
result = await self.prompt_engine.execute_strategy(
    strategy=template_path,
    context=context,
    timeout=120,
)
```

Это позволяет использовать все преимущества hybrid architecture:
- ✅ Легкое изменение шаблонов без кода
- ✅ Поддержка duel mode (сравнение code vs prompt)
- ✅ Кэширование и мониторинг

## Следующие шаги

1. **Интеграция с TestAnalyzer** - автоматический запуск при изменении кода
2. **Мониторинг покрытия** - проверка качества сгенерированных тестов
3. **Кэширование** - избежание дублирования генерации
4. **Review mode** - показ генерированных тестов перед применением

## Файлы

- `agents/cognitive_agent/src/test_generator.py` - основной модуль
- `agents/cognitive_agent/test_test_generator.py` - тесты
- `agents/cognitive_agent/autonomous_agent.py` - интеграция
