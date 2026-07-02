# Директория src для Cognitive Agent

Эта директория содержит исходный код основных компонентов Cognitive Agent — автономного AI-агента, координирующего все сервисы экосистемы.

---

## Структура

```
agents/cognitive_agent/src/
├── autonomous_agent.py           # Основная версия агента (Standard)
├── base_agent.py                 # Базовый класс с enterprise-функциональностью
├── main.py                       # FastAPI-сервер и точка входа
├── api/                          # API endpoints
│   └── endpoints.py              # HTTP API для агента
├── code_analyzer.py              # Анализатор качества кода
├── documentation_analyzer.py     # Анализатор документации
├── test_analyzer.py              # Анализатор тестов
├── project_scanner.py            # Сканер проекта
├── task_planner.py               # Планировщик задач
├── task_planner_enhanced.py      # Улучшенный планировщик задач
├── config_integration.py         # Интеграция с конфигурацией
├── logging_config.py             # Конфигурация логирования
├── security/                     # Модули безопасности
├── models/                       # Pydantic-модели
├── transparency_logger.py        # Прозрачное логирование
├── memory_integrity.py           # Целостность памяти
├── conflict_resolver.py          # Разрешение конфликтов
├── approval_workflow.py          # Workflow одобрений
├── proposal_system.py            # Система предложений
├── rollback_manager.py           # Менеджер откатов
├── explanation_engine.py         # Движок объяснений
└── self_testing_module.py        # Модуль самотестирования
```

---

## Основные компоненты

### Базовый класс

`base_agent.py` содержит общую функциональность для всех версий агента:

- Инициализация компонентов (logger, config, guardrails)
- Методы сканирования и анализа
- Планирование задач (TaskPlanner)
- Интеграция с ChromaDB (RAG)
- Enterprise-безопасность (guardrails, RBAC)
- Аудит и логирование (AuditLogger, StructuredLogger)
- Методы для работы с AI провайдерами

**Использование:**

```python
from agents.cognitive_agent.src.base_agent import BaseCognitiveAgent

class MyAgent(BaseCognitiveAgent):
    def start(self):
        pass  # Реализация запуска

    def stop(self):
        pass  # Реализация остановки

    def scan_project(self):
        return {}  # Реализация сканирования

    def execute_task(self, task):
        return {}  # Реализация выполнения задачи
```

### Анализаторы качества

#### CodeAnalyzer

Интеграция со статическими анализаторами Python:

- **MyPy** — проверка типизации
- **Ruff** — стиль и стандарты
- **Bandit** — безопасность
- **Pyright** — дополнительная проверка типов
- **Coverage** — покрытие тестами

```python
from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer(project_path="./my_project")
report = analyzer.generate_quality_report()
```

#### DocumentationAnalyzer

Анализ документации:

- Проверка docstrings в функциях и классах
- Структура Markdown-файлов
- Согласованность кода и документации

```python
from agents.cognitive_agent.src.documentation_analyzer import DocumentationAnalyzer

analyzer = DocumentationAnalyzer(project_path="./my_project")
report = analyzer.run_documentation_analysis()
```

#### TestAnalyzer

Анализ тестов:

- Поиск файлов тестов (pytest, unittest)
- Оценка качества (утверждения, побочные эффекты)
- Покрытие кода тестами

```python
from agents.cognitive_agent.src.test_analyzer import TestAnalyzer

analyzer = TestAnalyzer(project_path="./my_project")
report = analyzer.run_test_analysis()
```

### Планирование задач

`task_planner.py` и `task_planner_enhanced.py` обеспечивают построение графов зависимостей:

- Добавление задач с зависимостями
- Условное выполнение
- Параллельное выполнение
- Retry-логика
- Откат изменений

```python
from agents.cognitive_agent.src.task_planner import TaskPlanner

planner = TaskPlanner()
task_id = planner.add_task(
    name="refactor_database",
    function=refactor_func,
    dependencies=["backup_db"],
    priority=1
)
result = planner.execute_plan()
```

### Логирование и аудит

`base_agent.py` содержит два основных класса логирования:

#### StructuredLogger

JSON-логирование для ELK/Grafana:

```python
from agents.cognitive_agent.src.base_agent import StructuredLogger

logger = StructuredLogger(name="my_app", log_file="logs/app.json")
logger.info("Processing request", user_id="123")
```

#### AuditLogger

Аудит-логирование для трассировки:

```python
from agents.cognitive_agent.src.base_agent import AuditLogger

logger = AuditLogger(agent_id="my-agent")
logger.log_action(
    action="scan_project",
    details={"files_scanned": 150},
    status="success"
)
```

### Самотестирование

`self_testing_module.py` обеспечивает автоматическое создание тестов:

- Обнаружение измененных файлов
- Генерация тестов через AI
- Валидация pytest

```python
from agents.cognitive_agent.src.self_testing_module import SelfTestingModule

module = SelfTestingModule(project_path="./my_project")
module.test_file_change("src/my_module.py")
```

---

## Интеграция

### Импорт модулей

Используйте абсолютные импорты:

```python
# Правильно
from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer
from agents.cognitive_agent.src.task_planner import TaskPlanner

# Неправильно
from code_analyzer import CodeAnalyzer  # Relative import
```

### Зависимости

Основные зависимости:

- `fastapi` — веб-сервер
- `structlog` — структурированное логирование
- `langchain` — интеграция с AI
- `chromadb` — RAG
- `pydantic` — валидация данных

Полный список в `requirements.txt`.

---

## Тестирование

```bash
# Запуск тестов модуля
pytest tests/test_code_analyzer.py -v
pytest tests/test_documentation_analyzer.py -v
pytest tests/test_test_analyzer.py -v

# Запуск всех тестов агента
pytest tests/ -v

# С coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Основные методы

### BaseCognitiveAgent

| Метод | Описание |
|-------|----------|
| `scan_project(mode)` | Сканирование проекта |
| `execute_task(task)` | Выполнение задачи через AI |
| `analyze_code_quality()` | Анализ качества кода |
| `analyze_documentation()` | Анализ документации |
| `analyze_test_quality()` | Анализ тестов |
| `generate_recommendations()` | Генерация рекомендаций |
| `get_status()` | Получение статуса агента |
| `add_task(...)` | Добавление задачи в планировщик |
| `get_task(task_id)` | Получение информации о задаче |
| `update_task_status(task_id, status)` | Обновление статуса задачи |

### TaskPlanner

| Метод | Описание |
|-------|----------|
| `add_task(...)` | Добавление задачи с зависимостями |
| `execute_plan()` | Выполнение плана задач |
| `get_task_status(task_id)` | Получение статуса задачи |
| `cancel_plan()` | Отмена выполнения плана |
| `clear_plan()` | Очистка плана |

---

## Конфигурация

Конфигурация загружается из `config/agent-config.yaml`:

```yaml
ai_providers:
  primary: "gigachat-lite"
  fallback: "ollama-qwen2.5-coder"

security:
  guardrails_enabled: true
  rbac_enabled: false

logging:
  level: "INFO"
  format: "json"
  audit_enabled: true
```

---

## Безопасность

Все модули поддерживают безопасность через:

- Валидацию входных данных (Pydantic)
- Проверку путей файлов (SecurePath)
- Guardrails для AI-запросов
- Аудит действий (AuditLogger)

---

## Пример использования

```python
from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

# Инициализация
agent = AutonomousCognitiveAgent(
    project_path="./my_project",
    agent_id="my-agent",
    name="My Cognitive Agent"
)

# Запуск
agent.start()

# Сканирование
scan_results = agent.scan_project(mode="full")

# Анализ качества
quality_report = agent.analyze_code_quality()
doc_report = agent.analyze_documentation()
test_report = agent.analyze_test_quality()

# Рекомендации
recommendations = agent.generate_recommendations()

# Остановка
agent.stop()
```

---

## См. также

- [README агента](../README.md) — полное описание агента
- [Глобальный README](../../README.md) — архитектура экосистемы
- [API Documentation](src/api/endpoints.md) — HTTP API

---

*Последнее обновление: 2026-07-02*
