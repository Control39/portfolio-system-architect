# Интеграция prompts/ в Cognitive Agent (2026-06-27)

## Обзор

Корневой каталог `prompts/` (шаблоны генерации тестов) успешно интегрирован в Cognitive Agent через расширение `PromptEngine` для поддержки подпапок.

## Что было сделано

### 1. Создана структура подпапок

```
agents/cognitive_agent/prompts/
├── config.yaml                           # Конфигурация выбора шаблонов
├── test_generation.md                    # Главный шаблон для генерации тестов
├── test_coverage_analysis.md             # Шаблон анализа покрытия (старый)
└── python/                               # Подпапки по фреймворкам
    ├── base/
    │   └── unit.md                       # Базовые юнит-тесты
    ├── django/
    │   └── unit.md                       # Django тесты
    ├── fastapi/
    │   ├── api.md                        # FastAPI API тесты
    │   └── integration.md                # FastAPI интеграционные тесты
    └── flask/
        └── api.md                        # Flask API тесты
```

### 2. Расширена функциональность PromptEngine

**Изменения в `prompt_engine.py`:**

- ✅ `_discover_templates()` - теперь рекурсивно обнаруживает шаблоны в подпапках
- ✅ `load_template()` - поддерживает как простые имена (`test_generation`), так и относительные пути (`python/fastapi/api`)
- ✅ Автоматическое обнаружение всех шаблонов в `agents/cognitive_agent/prompts/`

**Результат:** Теперь агент может загружать шаблоны из любой вложенной структуры.

### 3. Обновлена документация

- ✅ `README.md` - обновлён для описания новой структуры подпапок
- ✅ `config.yaml` - документирует правила выбора шаблонов по фреймворку и типу файла
- ✅ `test_generation.md` - новый главный шаблон для автоматической генерации тестов

### 4. Добавлены тесты

- ✅ `test_prompt_engine.py` - расширены тесты для проверки подпапок и обратной совместимости

## Как это работает

### Выбор шаблона по фреймворку и типу файла:

1. **FastAPI**
   - `api_*.py`, `endpoint*.py` → `python/fastapi/api.md`
   - `integration*.py` → `python/fastapi/integration.md`

2. **Flask**
   - `api_*.py`, `endpoint*.py` → `python/flask/api.md`

3. **Django**
   - `models.py` → `python/django/unit.md`
   - `views.py` → `python/django/unit.md`

4. **Base Python / Other**
   - Любой файл → `python/base/unit.md`

### Пример использования в коде:

```python
from pathlib import Path
from agents.cognitive_agent.src.prompt_engine import PromptEngine

# Инициализация
prompts_dir = Path("agents/cognitive_agent/prompts")
engine = PromptEngine(prompts_dir=prompts_dir)

# Загрузка шаблона по относительному пути
template = engine.load_template("python/fastapi/api")

# Рендер с контекстом
prompt = engine.render("python/fastapi/api", {
    "file_path": "apps/user_service/api/users.py",
    "service_name": "user_service",
    "framework": "FastAPI",
    "coverage_target": "85",
    "code": "# user code here"
})
```

## Обратная совместимость

✅ Все старые шаблоны (например, `test_coverage_analysis.md`) продолжают работать по простому имени.

## Следующие шаги

### Потенциальные улучшения:

1. **Интеграция с TestAnalyzer** - автоматический запуск `test_generation` при изменении кода
2. **Кэширование результатов** - избежание дублирования генерации тестов
3. **Выбор покрытия** - адаптация целей покрытия на основе критичности сервиса
4. **Генерация fixtures** - автоматическое создание тестовых данных

## Резервирование корневого prompts/

✅ Корневой `prompts/` следует признать deprecated - все шаблоны теперь в `agents/cognitive_agent/prompts/`.

## Файлы изменений

**Новые файлы:**
- `agents/cognitive_agent/prompts/config.yaml`
- `agents/cognitive_agent/prompts/test_generation.md`
- `agents/cognitive_agent/prompts/python/base/unit.md`
- `agents/cognitive_agent/prompts/python/django/unit.md`
- `agents/cognitive_agent/prompts/python/fastapi/api.md`
- `agents/cognitive_agent/prompts/python/fastapi/integration.md`
- `agents/cognitive_agent/prompts/python/flask/api.md`

**Изменённые файлы:**
- `agents/cognitive_agent/prompts/README.md`
- `agents/cognitive_agent/src/prompt_engine.py`
- `agents/cognitive_agent/test_prompt_engine.py`

## Статус

✅ **ЗАВЕРШЕНО** - Интеграция успешно протестирована и готова к использованию.

---

**Дата:** 2026-06-27  
**Автор:** Cognitive Agent Team  
**Приоритет:** Высокий (улучшение автономности агента)
