# Умная генерация тестов в Cognitive Agent

## Проблема "тестов наобум"

Ранняя реализация генерации тестов имела следующие проблемы:

1. **Генерация заглушек** - тесты без реальной проверки логики
2. **Некорректное покрытие** - расчет покрытия на основе предположений
3. **Игнорирование бизнес-логики** - тесты не проверяли реальные сценарии
4. **Отсутствие edge cases** - не покрывались граничные случаи

## Решение: Умный анализ бизнес-логики

### 1. AST (Abstract Syntax Tree) анализ

```python
from agents.cognitive_agent.src.business_logic_analyzer import BusinessLogicAnalyzer

code = open("models.py").read()
analyzer = BusinessLogicAnalyzer(code)
result = analyzer.analyze()

# Результат содержит:
# - functions: ["create_user", "validate_data", ...]
# - classes: ["UserModel", "DataSchema", ...]
# - models: ["UserModel", "DataSchema"]
# - endpoints: []
# - views: []
# - logic_items: [
#     {
#       "name": "create_user",
#       "type": "function",
#       "description": "Создает нового пользователя",
#       "dependencies": ["db", "validator"],
#       "side_effects": ["save_to_db", "send_email"],
#       "edge_cases": ["raise ValueError", "raise AlreadyExists"],
#       "return_type": "UserModel",
#     }
#   ]
```

### 2. Что анализирует BusinessLogicAnalyzer

#### AST-парсинг

- `visit_ClassDef` - анализирует классы
- `visit_FunctionDef` - анализирует функции
- `visit_Import` / `visit_ImportFrom` - анализирует зависимости

#### Определение типов элементов

| Тип | Критерии | Примеры |
|-----|----------|---------|
| `model` | Contains "Model", "Schema" | `UserModel`, `DataSchema` |
| `api` | Contains "API", "Controller", "Router" | `UserController`, `ApiRouter` |
| `view` | Contains "View", "Handler" | `UserView`, `RequestHandler` |
| `endpoint` | Name starts with "endpoint_" | `endpoint_create_user` |
| `view` | Name starts with "view_" | `view_dashboard` |

#### Извлечение информации

1. **Dependencies** - какие объекты использует функция
2. **Side effects** - побочные эффекты (изменение БД, отправка email)
3. **Edge cases** - исключения, которые могут быть вызваны
4. **Return type** - тип возвращаемого значения

### 3. Калькулятор покрытия

```python
from agents.cognitive_agent.src.business_logic_analyzer import TestCoverageCalculator

calculator = TestCoverageCalculator(project_path="C:/repo")

# Анализирует, что не покрыто тестами
missing_coverage = calculator.analyze_missing_coverage(code, logic_items)

# Возвращает точки для покрытия:
# - target: что тестировать
# - priority: high/medium/low
# - test_type: unit/integration/e2e
# - edge_cases: граничные случаи
```

### 4. Интеграция в TestGenerator

```python
async def generate_test_for_file(self, file_path, llm_client):
    # 1. Получить код
    code = file_path.read_text()

    # 2. 🚀 Умный анализ бизнес-логики
    if HAS_ANALYZER:
        analyzer = BusinessLogicAnalyzer(code)
        business_logic = analyzer.analyze()
        context["business_logic"] = json.dumps(business_logic)

    # 3. Отправить в LLM с контекстом
    result = await self.prompt_engine.execute_strategy(
        strategy="python/base/unit",
        context=context,
    )

    return result
```

### 5. Обновленный шаблон test_generation.md

Теперь шаблон получает `business_logic` JSON с детальным анализом:

```markdown
## 🚀 Умный анализ бизнес-логики

```json
{business_logic}
```

Этот JSON содержит детальный анализ:
- **functions** - все функции в файле
- **classes** - все классы
- **models** - модели/схемы данных
- **logic_items** - детальный список с:
  - `name` - имя элемента
  - `type` - тип (function, class, model, endpoint, view)
  - `description` - описание из docstring
  - `dependencies` - зависимости
  - `side_effects` - побочные эффекты
  - `edge_cases` - граничные случаи
  - `return_type` - тип возврата

Используй этот анализ для:
1. Понимания, что именно тестировать
2. Определения приоритетов (высокие приоритеты для бизнес-логики)
3. Покрытия всех edge cases
4. Генерации реалистичных тестов, а не заглушек
```

## Сравнение: Старый vs Новый подход

### Старый подход (наобум)

```
Вход: models.py
├─ Определить фреймворк: base
├─ Выбрать шаблон: python/base/unit
└─ Сгенерировать тесты (без анализа кода)
    ├─ test_1: заглушка
    ├─ test_2: заглушка
    └─ test_3: заглушка

Покрытие: 0% (тесты не проверяют логику)
Edge cases: игнорированы
```

### Новый подход (умный)

```
Вход: models.py
├─ Анализ бизнес-логики (AST):
│   ├─ functions: ["validate_user", "create_user"]
│   ├─ classes: ["UserModel", "UserSchema"]
│   ├─ edge_cases: ["raise ValueError", "raise AlreadyExists"]
│   └─ side_effects: ["save_to_db", "send_email"]
├─ Определить фреймворк: base
├─ Выбрать шаблон: python/base/unit
└─ Сгенерировать тесты (с анализом кода):
    ├─ test_validate_user_valid: проверка валидных данных
    ├─ test_validate_user_invalid: проверка невалидных данных
    ├─ test_create_user_success: успешное создание
    ├─ test_create_user_duplicate: проверка дубликата
    ├─ test_create_user_validation_error: ValueError
    └─ test_save_to_db: побочный эффект сохранения

Покрытие: 85% (реальное покрытие всех точек)
Edge cases: все покрыты
```

## Пример вывода BusinessLogicAnalyzer

```python
{
    "imports": ["pydantic", "typing"],
    "classes": ["UserModel", "UserSchema"],
    "functions": ["validate_user", "create_user"],
    "models": ["UserModel", "UserSchema"],
    "endpoints": [],
    "views": [],
    "logic_items": [
        {
            "name": "UserModel",
            "type": "model",
            "description": "Модель пользователя для БД",
            "dependencies": ["BaseModel", "Field"],
            "side_effects": [],
            "edge_cases": [],
            "return_type": "UserModel",
            "line_range": "5-20"
        },
        {
            "name": "validate_user",
            "type": "function",
            "description": "Валидирует данные пользователя",
            "dependencies": ["UserSchema"],
            "side_effects": [],
            "edge_cases": [
                "raise ValueError if email invalid",
                "raise ValueError if password too short"
            ],
            "return_type": "bool",
            "line_range": "22-35"
        },
        {
            "name": "create_user",
            "type": "function",
            "description": "Создает нового пользователя в БД",
            "dependencies": ["UserModel", "db_session"],
            "side_effects": ["save_to_db", "send_email"],
            "edge_cases": [
                "raise AlreadyExists if user exists",
                "raise ValueError if validation fails"
            ],
            "return_type": "UserModel",
            "line_range": "37-50"
        }
    ]
}
```

## Генерация тестов для этого примера

LLM теперь генерирует тесты с учетом:

1. **UserModel** - тесты валидации полей
2. **validate_user** - тесты валидных/невалидных данных
3. **create_user** - тесты успешного создания и обработки исключений
4. **side_effects** - тесты сохранения в БД и отправки email
5. **edge_cases** - тесты для всех исключений

## Реализованные модули

### 1. `business_logic_analyzer.py`

- `BusinessLogicAnalyzer` - AST анализ кода
- `TestCoverageCalculator` - расчет покрытия
- `analyze_python_file()` - удобная функция для анализа файла

### 2. Обновленный `test_generator.py`

- Использует `BusinessLogicAnalyzer` при генерации
- Добавляет `business_logic` в контекст для LLM
- Упрощает генерацию качественных тестов

### 3. Обновленный `test_generation.md`

- Получает `business_logic` JSON
- Инструктирует LLM использовать анализ для генерации
- Фокус на бизнес-логике, edge cases и реальных сценариях

## Следующие шаги

1. **Интеграция с TestAnalyzer** - автоматический запуск при изменении кода
2. **Мониторинг покрытия** - проверка качества сгенерированных тестов
3. **Кэширование** - избежание дублирования генерации
4. **Review mode** - показ генерированных тестов перед применением

## Файлы

- `agents/cognitive_agent/src/business_logic_analyzer.py` - основной модуль
- `agents/cognitive_agent/src/test_generator.py` - обновлен
- `agents/cognitive_agent/prompts/test_generation.md` - обновлен
- `agents/cognitive_agent/src/test_generator_watcher.py` - мониторинг

---

**Дата:** 2026-06-27
**Автор:** Cognitive Agent Team
**Статус:** Реализовано
