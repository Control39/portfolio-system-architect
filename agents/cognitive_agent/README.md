# Cognitive Agent

> **Статус:** 🟢 Production-ready
> **Версия:** 1.0.0
> **Дата актуализации:** 2026-07-02
> **Архитектор:** Екатерина Куделя (@Control39)
> **Контакт:** leadarchitect@yandex.ru

---

## Обзор

**Cognitive Agent** — это центральный автономный AI-агент экосистемы, который координирует все сервисы, анализирует качество кода/документации/тестов и принимает решения на основе структурированного анализа данных.

### Ключевые функции

- **Автономное сканирование** проектов с определением технологического стека
- **Интеграция с AI** (GigaChat + Ollama fallback) для reasoning и планирования
- **Анализ качества** (MyPy, Ruff, Bandit, Pyright, Coverage)
- **Анализ документации** (docstrings, Markdown, согласованность)
- **Анализ тестов** (поиск, качество, покрытие)
- **Планирование задач** с графами зависимостей
- **Enterprise-безопасность** (guardrails, RBAC, аудит)
- **Структурированное логирование** (JSON, ELK/Grafana)
- **Самовосстановление** и обучение на результатах

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                   AutonomousCognitiveAgent                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  BaseCognitiveAgent                   │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐ │  │
│  │  │  TaskPlanner │ │  ChromaDB    │ │  AuditLogger  │ │  │
│  │  └──────────────┘ └──────────────┘ └───────────────┘ │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐ │  │
│  │  │ CodeAnalyzer │ │DocAnalyzer   │ │TestAnalyzer   │ │  │
│  │  └──────────────┘ └──────────────┘ └───────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  AI Provider │    │   IT Compass │    │  Job Agent   │
│    Manager   │◄──►│   Scanner    │◄──►│ Integration  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Установка

### Системные требования

- Python 3.12+
- pip или poetry
- Docker (опционально, для контейнеризации)

### Быстрый старт

```bash
# 1. Клонирование репозитория
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect

# 2. Создание виртуального окружения
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Установка зависимостей
pip install -r requirements-dev.txt

# 4. Запуск Cognitive Agent
cd agents/cognitive_agent
python -m uvicorn src.main:app --reload --port 8008

# 5. Проверка работоспособности
curl http://localhost:8008/health
```

### Docker-версия

```bash
cd agents/cognitive_agent
docker-compose up -d cognitive-agent

# Логи
docker-compose logs -f cognitive-agent
```

---

## Использование

### Запуск агента

```python
from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

# Инициализация
agent = AutonomousCognitiveAgent(
    project_path="./my_project",
    agent_id="my-agent",
    name="My Cognitive Agent",
    config={"max_workers": 4, "timeout": 60}
)

# Запуск сканирования
scan_results = agent.scan_project()

# Анализ качества кода
quality_report = agent.analyze_code_quality()

# Генерация рекомендаций
recommendations = agent.generate_recommendations()
```

### API endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка работоспособности |
| GET | `/api/v1/status` | Статус агента |
| POST | `/api/v1/scan` | Запуск сканирования проекта |
| POST | `/api/v1/analyze` | Анализ качества кода/документации/тестов |
| POST | `/api/v1/recommend` | Генерация рекомендаций |

### Конфигурация

Создайте `config/agent-config.yaml`:

```yaml
ai_providers:
  primary: "gigachat-lite"
  fallback: "ollama-qwen2.5-coder"
  timeout: 30
  retry_attempts: 3

security:
  guardrails_enabled: true
  rbac_enabled: false
  file_validation_enabled: true

logging:
  level: "INFO"
  format: "json"
  audit_enabled: true

planning:
  enabled: true
  max_concurrent_tasks: 5

scanning:
  include_extensions: [".py", ".js", ".ts", ".md"]
  exclude_patterns: [".git/", "node_modules/", "__pycache__/"]
  max_file_size: 10485760  # 10MB
```

---

## Модули

### Анализаторы качества

#### CodeAnalyzer (`src/code_analyzer.py`)

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

# report = {
#     "results": {"mypy": {...}, "ruff": {...}, ...},
#     "summary": {"coverage_percentage": 75.5, "total_issues": 12}
# }
```

#### DocumentationAnalyzer (`src/documentation_analyzer.py`)

Анализ документации:

- Проверка docstrings в функциях и классах
- Структура Markdown-файлов (заголовки, организация)
- Согласованность кода и документации

```python
from agents.cognitive_agent.src.documentation_analyzer import DocumentationAnalyzer

analyzer = DocumentationAnalyzer(project_path="./my_project")
report = analyzer.run_documentation_analysis()

# report = {
#     "summary": {"total_issues": 5, "coverage": 0.75},
#     "files": {...}
# }
```

#### TestAnalyzer (`src/test_analyzer.py`)

Анализ тестов:

- Поиск файлов тестов (pytest, unittest)
- Оценка качества (утверждения, побочные эффекты)
- Покрытие кода тестами

```python
from agents.cognitive_agent.src.test_analyzer import TestAnalyzer

analyzer = TestAnalyzer(project_path="./my_project")
report = analyzer.run_test_analysis()

# report = {
#     "summary": {"total_tests": 150, "coverage": 0.82},
#     "files": {...}
# }
```

### Планирование задач

```python
from agents.cognitive_agent.src.task_planner import TaskPlanner

planner = TaskPlanner()

# Добавление задачи с зависимостями
task_id = planner.add_task(
    name="refactor_database",
    function=refactor_func,
    dependencies=["backup_db", "update_schema"],
    priority=1
)

# Выполнение плана
result = planner.execute_plan()
```

### Логирование и аудит

```python
from agents.cognitive_agent.src.base_agent import AuditLogger

logger = AuditLogger(agent_id="my-agent")

# Логирование действия
logger.log_action(
    action="scan_project",
    details={"files_scanned": 150, "duration_ms": 250},
    status="success"
)

# Логирование события безопасности
logger.log_security_event(
    event_type="access_denied",
    details={"path": "/etc/passwd", "action": "read"},
    severity="critical"
)
```

---

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# Конкретный модуль
pytest tests/test_code_analyzer.py -v

# С coverage
pytest tests/ --cov=src --cov-report=term-missing

# Только быстрые тесты
pytest -m "not slow"
```

### Статистика

- **Тестовых функций:** 19+ (для base_agent.py)
- **Проходимость:** 100%
- **Среднее покрытие:** ~75%

---

## Безопасность

### Уровни защиты

| Уровень | Механизмы |
|---------|----------|
| **Входные данные** | Pydantic-валидация, check_rate_limit |
| **Пути файлов** | SecurePath, path validation |
| **Команды** | DANGEROUS_PATTERNS, AI_RESPONSE_DANGEROUS_PATTERNS |
| **Доступ** | Guardrails, RBAC, enterprise_guardrails |
| **Аудит** | AuditLogger, log_security_event |

### Пример конфигурации безопасности

```yaml
security:
  guardrails_enabled: true
  blocked_patterns:
    - "rm -rf"
    - "eval("
    - "os.system"
  allowed_paths:
    - "^apps/"
    - "^agents/"
  safe_actions:
    - "read"
    - "scan"
    - "analyze"
```

---

## Мониторинг

### Метрики

- Количество вызовов AI (ai_calls_today)
- Success rate решений (memory.success_rate)
- Время выполнения задач (task_duration_ms)
- Количество сканированных файлов
- Ошибки безопасности (security_events)

### Логирование

Агент использует `structlog` для структурированного JSON-логирования:

```bash
# Логи в файле
logs/cognitive_agent.json

# Аудит-логи
logs/agent_audit.jsonl

# Основные логи
logs/cognitive_agent.log
```

---

## Интеграции

### AI Provider Manager

```python
from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

provider_manager = get_provider_manager()
active_provider = provider_manager.get_active_provider()

# Варианты: gigachat-lite, gigachat-pro, ollama-qwen2.5-coder
```

### IT Compass Scanner

```python
from apps.it_compass.src.it_compass_scanner import get_scanner

scanner = get_scanner()
scan_result = scanner.scan_project()

# Маркеры компетенций в 19 доменах
markers = scan_result.get("markers", [])
```

### ChromaDB (RAG)

```python
from apps.embedding_agent.chroma_indexer import ChromaDocumentIndexer
from apps.embedding_agent.embedder import DocumentEmbedder

indexer = ChromaDocumentIndexer(
    persist_directory="./chroma_db",
    collection_name="project_docs",
    embedder=DocumentEmbedder()
)

# Добавление документов
indexer.add_documents(documents)

# Поиск
results = indexer.search(query="архитектура агента")
```

---

## Отладка

### Включение отладки

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Или для structlog
import structlog
structlog.configure(processors=[...], wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
```

### Проверка зависимостей

```python
# Проверка доступных интеграций
print(agent._is_chroma_available())
print(agent._is_job_agent_available())
print(agent.ai_manager.get_active_provider())
```

---

## Поддержка

### Вопросы и проблемы

- **Issue:** [github.com/Control39/portfolio-system-architect/issues](https://github.com/Control39/portfolio-system-architect/issues)
- **Discussions:** [github.com/Control39/portfolio-system-architect/discussions](https://github.com/Control39/portfolio-system-architect/discussions)
- **Email:** leadarchitect@yandex.ru

### Документация

- [Глобальный README](../../README.md)
- [Architecture](../../docs/ARCHITECTURE.md)
- [AI Instructions](../../docs/ai/AI_INSTRUCTIONS.md)

---

## Лицензия

- **Код:** MIT License
- **Методология:** CC BY-ND 4.0 (© Екатерина Куделя)

---

<div align="center">

**Автономный AI-агент для координации экосистемы | Анализ качества кода | Enterprise-безопасность | Структурированное логирование**

*Последнее обновление: 2026-07-02*

</div>
