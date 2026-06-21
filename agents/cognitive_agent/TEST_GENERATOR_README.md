# Test Generator - Автоматическая генерация тестов

## 🎯 Назначение

`TestGenerator` — это модуль когнитивного агента, который автоматически генерирует тесты для Python-проектов.

**Ключевая идея:** Агент подходит к генерации тестов **осознанно** — используя профили сервисов и специализированные промпты.

---

## 📋 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CodeAnalyzer.run_full_analysis()                         │
│    - находит баги, недостатки в коде                        │\n│    - определяет покрытие тестами                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TestGenerator.analyze_and_generate(code, analysis)       │
│    - определяет профиль сервиса                             │
│    - выбирает промпт-шаблон на основе технологии             │
│    - вызывает AI (GigaChat/Ollama) для генерации            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TestAnalyzer проверяет новые тесты                       │
│    - запускает pytest, coverage                             │
│    - оценивает качество тестов                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Модули

### 1. `src/test_generator.py`

Основной класс `TestGenerator`:

```python
class TestGenerator:
    def analyze_and_generate(self, file_path: str) -> dict[str, Any]:
        """Анализ кода и генерация тестов"""
        
    def generate_for_service(self, service_name: str) -> dict[str, Any]:
        """Генерация тестов для всего сервиса"""
        
    def _select_prompt_template(self, service_profile, file_path) -> str:
        """Выбор промпт-шаблона"""
        
    def _call_ai_for_generation(self, prompt_template, context) -> str:
        """Вызов AI для генерации"""
```

### 2. `src/service_registry.py`

`ServiceRegistry` — реестр всех сервисов:

```python
@dataclass
class ServiceProfile:
    name: str
    path: str
    language: str
    framework: str
    criticality: str
    coverage_target: float

class ServiceRegistry:
    def get_profile_by_path(self, file_path) -> Optional[ServiceProfile]:
        """Получить профиль по пути файла"""
```

### 3. `src/service_discovery.py`

`ServiceDiscovery` — автодетект технологий:

```python
class ServiceDiscovery:
    @classmethod
    def detect_language(cls, service_path) -> str:
        """Определить язык программирования"""
        
    @classmethod
    def detect_framework(cls, service_path, language) -> Optional[str]:
        """Определить фреймворк"""
        
    @classmethod
    def detect_criticality(cls, service_path) -> str:
        """Определить критичность"""
```

---

## 📚 Промпт-шаблоны

### Структура

```
prompts/
├── python/
│   ├── fastapi/
│   │   ├── unit.md
│   │   ├── integration.md
│   │   └── api.md
│   ├── flask/
│   │   └── api.md
│   ├── django/
│   │   └── unit.md
│   └── base/
│       └── unit.md
└── config.yaml
```

### Формат шаблона

```markdown
Роль: Ты — эксперт по Python и pytest.

Контекст: 
- Изменен файл {file_path} в сервисе {service_name}
- Фреймворк: {framework}
- Цель покрытия: {coverage_target}%

Задача: Сгенерируй набор юнит-тестов.

Требования:
1. Тестируй happy path
2. Тестируй обработку ошибок
3. Используй моки для изоляции

Код для анализа:
{code}
```

---

## 🔍 Стратегия генерации

### По критичности сервиса

| Критичность | Типы тестов | Покрытие |
|-------------|-------------|----------|
| critical    | unit + integration + e2e | 95%+ |
| high        | unit + integration | 90% |
| medium      | unit | 80% |
| low         | unit (минимальные) | 75% |

### По технологии

| Фреймворк | Шаблон |
|-----------|--------|
| FastAPI   | `prompts/python/fastapi/` |
| Flask     | `prompts/python/flask/` |
| Django    | `prompts/python/django/` |
| Base      | `prompts/python/base/` |

---

## 🚀 Использование

### Генерация для одного файла

```python
from agents.cognitive_agent.src.test_generator import TestGenerator

generator = TestGenerator(project_path=".")

result = generator.analyze_and_generate("apps/my_service/api/users.py")

print(result["status"])
print(result["generated_tests"])
```

### Генерация для всего сервиса

```python
result = generator.generate_for_service("my_service")

print(f"Обработано файлов: {result['files_processed']}")
```

### В агенте

```python
from autonomous_agent_enterprise import AutonomousCognitiveAgent

agent = AutonomousCognitiveAgent()

# Генерация тестов для файла
agent.generate_tests_for_file("apps/my_service/api/users.py")

# Генерация тестов для сервиса
agent.generate_tests_for_service("my_service")
```

---

## 📊 Интеграция с CodeAnalyzer и TestAnalyzer

```python
# 1. CodeAnalyzer анализирует код
analysis_results = code_analyzer.run_full_analysis()

# 2. TestGenerator генерирует тесты на основе анализа
generated_tests = test_generator.analyze_and_generate(code, analysis_results)

# 3. TestAnalyzer проверяет качество новых тестов
test_quality = test_analyzer.evaluate_tests(generated_tests)
```

---

## 🧪 Тестирование

```bash
# Запуск тестов
pytest agents/cognitive_agent/tests/ -v

# Покрытие тестами
pytest agents/cognitive_agent/tests/ --cov=src/test_generator --cov-report=html
```

---

## 📝 Примеры

### Пример 1: Генерация для FastAPI

```python
# Файл: apps/user_service/api/users.py
# Фреймворк: FastAPI
# Критичность: high

result = generator.analyze_and_generate("apps/user_service/api/users.py")
# Используется: prompts/python/fastapi/api.md
```

### Пример 2: Генерация для Flask

```python
# Файл: apps/chat_backend/api/messages.py
# Фреймворк: Flask
# Критичность: medium

result = generator.analyze_and_generate("apps/chat_backend/api/messages.py")
# Используется: prompts/python/flask/api.md
```

---

## ⚙️ Настройка

### Конфигурация профилей

Файл: `agents/cognitive_agent/config/service-profiles.yaml`

```yaml
services:
  - name: "user-service"
    path: "apps/user_service"
    language: "python"
    framework: "fastapi"
    criticality: "high"
    test_frameworks: ["pytest"]
    coverage_target: 90.0
```

### Автодетект

Если файл `service-profiles.yaml` не найден, агент использует автодетект:

```python
registry = ServiceRegistry(repo_root=".")
# Автоматически обнаруживает сервисы в apps/ и agents/
```

---

## 🎓 Принципы работы

1. **Системный подход:** Агент знает про каждый сервис (технология, критичность, покрытие)
2. **Интеллектуальный выбор:** Промпт-шаблон выбирается на основе технологии и типа файла
3. **AI-генерация:** Использование GigaChat/Ollama для генерации高质量-тестов
4. **Валидация:** Проверка сгенерированных тестов через TestAnalyzer
5. **Метрики:** Сбор статистики по качеству тестов

---

## 📄 Логика выбора шаблона

```python
def _select_prompt_template(self, service_profile, file_path):
    # 1. Определить язык → prompts/{language}/
    # 2. Определить фреймворк → prompts/{language}/{framework}/
    # 3. Определить тип теста по имени файла → {test_type}.md
    
    return prompts_dir / service_profile.language / service_profile.framework / f"{test_type}.md"
```

---

**Автор:** GigaCode  
**Дата:** 2026-06-19  
**Версия:** 1.0.0 (Test Generator)
