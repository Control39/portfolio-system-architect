# 🗺️ Карта зависимостей проекта

> **Последнее обновление:** 9 мая 2026 г.
> **Цель:** Визуализация структуры зависимостей и импортов

---

## 📦 Основные зависимости (Root)

### Production (`requirements.txt`)
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.6.0
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0
redis>=5.0.0
chromadb>=0.5.0
langchain>=0.3.0
sentence-transformers>=3.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
aiohttp>=3.9.0
httpx>=0.27.0
```

### Development (`requirements-dev.txt`)
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
black>=24.0.0
isort>=5.13.0
ruff>=0.5.0
mypy>=1.10.0
bandit>=1.7.0
pre-commit>=3.7.0
playwright>=1.44.0
locust>=2.28.0
```

---

## 🏗️ Структура микросервисов (14 модулей)

### 1. **apps/it_compass/** — Методология IT-Compass
```
Зависимости:
├── fastapi
├── pydantic
├── streamlit (UI)
├── pandas
└── matplotlib

Импорты:
├── apps.it_compass.core
├── apps.it_compass.marks
└── src.core.validation
```

### 2. **apps/decision-engine/** — AI Reasoning Engine
```
Зависимости:
├── fastapi>=0.136.1
├── langchain
├── chromadb
├── sentence-transformers
└── redis

Импорты:
├── src.ai.llm
├── src.ai.rag
├── apps.decision-engine.core
└── apps.decision-engine.api
```

### 3. **apps/portfolio_organizer/** — Сбор доказательств
```
Зависимости:
├── fastapi
├── sqlalchemy
├── psycopg2-binary
└── aiohttp

Импорты:
├── apps.portfolio_organizer.core
├── apps.portfolio_organizer.evidence
└── src.core.database
```

### 4. **apps/system-proof/** — Валидация готовности
```
Зависимости:
├── fastapi
├── pydantic
└── jinja2

Импорты:
├── apps.system_proof.core
├── apps.system_proof.validators
└── src.core.validation
```

### 5. **apps/ml-model-registry/** — Регистр моделей
```
Зависимости:
├── fastapi
├── sqlalchemy
├── psycopg2-binary
├── boto3 (S3)
└── mlflow

Импорты:
├── apps.ml_model_registry.core
├── apps.ml_model_registry.api
└── src.infrastructure.storage
```

### 6. **apps/auth_service/** — JWT Аутентификация
```
Зависимости:
├── fastapi
├── python-jose[cryptography]
├── passlib[bcrypt]
└── python-multipart

Импорты:
├── apps.auth_service.core
├── apps.auth_service.security
└── src.security.jwt
```

### 7. **apps/career_development/** — Развитие карьеры
```
Зависимости:
├── fastapi
├── sqlalchemy
└── pandas

Импорты:
├── apps.career_development.core
├── apps.career_development.api
└── apps.career_development.skills
```

### 8. **apps/cognitive-agent/** — Cognitive Automation Agent
```
Зависимости:
├── langchain
├── chromadb
├── sentence-transformers
├── aiohttp
└── pyyaml

Импорты:
├── apps.cognitive-agent.skills
├── apps.cognitive-agent.workflows
└── src.ai.agents
```

### 9. **apps/infra-orchestrator/** — Оркестрация инфраструктуры
```
Зависимости:
├── kubernetes
├── pyyaml
├── boto3
└── fastapi

Импорты:
├── apps.infra_orchestrator.k8s
├── apps.infra_orchestrator.cloud
└── src.infrastructure.k8s
```

### 10. **apps/knowledge-graph/** — Граф знаний
```
Зависимости:
├── neo4j
├── networkx
├── fastapi
└── pydantic

Импорты:
├── apps.knowledge_graph.core
└── apps.knowledge_graph.api
```

### 11. **apps/mcp-server/** — MCP Server
```
Зависимости:
├── mcp
├── fastapi
└── pydantic

Импорты:
├── apps.mcp_server.core
└── apps.mcp_server.tools
```

### 12. **apps/job-automation-agent/** — Автоматизация поиска работы
```
Зависимости:
├── playwright
├── langchain
├── chromadb
└── fastapi

Импорты:
├── apps.job_automation_agent.skills
└── apps.job_automation_agent.workflows
```

### 13. **apps/template-service/** — Шаблоны документов
```
Зависимости:
├── fastapi
├── jinja2
└── python-docx

Импорты:
├── apps.template_service.core
└── apps.template_service.templates
```

### 14. **apps/thought-architecture/** — Архитектура мышления
```
Зависимости:
├── fastapi
├── pydantic
└── graphviz

Импорты:
├── apps.thought_architecture.core
└── apps.thought_architecture.visualization
```

---

## 🔄 Общие модули (src/)

### `src/core/` — Базовая логика
```
├── database.py       # SQLAlchemy подключение
├── config.py         # Pydantic Settings
├── validation.py     # Валидация данных
└── logging.py        # Конфигурация логирования
```

### `src/ai/` — ИИ-оркестрация
```
├── llm/
│   ├── base.py           # Базовый LLM интерфейс
│   ├── yandex_gpt.py     # YandexGPT интеграция
│   └── openai.py         # OpenAI интеграция
├── rag/
│   ├── retriever.py      # RAG retrieval
│   └── embeddings.py     # Векторные эмбеддинги
└── agents/
    ├── base.py           # Базовый агент
    └── orchestrator.py   # Оркестратор агентов
```

### `src/infrastructure/` — Инфраструктура
```
├── k8s/
│   ├── client.py         # Kubernetes клиент
│   └── resources.py      # K8s ресурсы
├── storage/
│   ├── s3.py             # S3 хранение
│   └── local.py          # Локальное хранение
└── cache/
    └── redis.py          # Redis кэш
```

### `src/security/` — Безопасность
```
├── jwt.py              # JWT токены
├── password.py         # Хеширование паролей
└── secrets.py          # Управление секретами
```

---

## 🔗 Ключевые зависимости между сервисами

```
┌──────────────────┐
│  decision-engine │─────┐
└──────────────────┘     │
                         ▼
┌──────────────────┐  ┌──────────────┐
│ portfolio-       │─▶│  src.ai.rag  │
│ organizer        │  └──────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  system-proof    │
└──────────────────┘

┌──────────────────┐
│  cognitive-agent │─────┐
└──────────────────┘     │
         │               │
         ▼               ▼
┌──────────────────┐  ┌──────────────┐
│ job-automation   │  │  src.agents  │
│ agent            │  └──────────────┘
└──────────────────┘
```

---

## 📊 Статус зависимостей

| Категория | Статус | Примечание |
|-----------|--------|------------|
| **FastAPI** | ✅ Актуально | 0.115.0 → 0.136.1 (один модуль) |
| **LangChain** | ⚠️ Устарело | Версия 0.3.x, требуется миграция на 1.x |
| **ChromaDB** | ⚠️ Устарело | Версия 0.5.x, требуется ручная миграция на 1.x |
| **pytest** | ✅ Актуально | 8.0.0+ |
| **security** | ✅ Проверено | Trivy, Bandit, Dependabot |

---

## 🚨 Известные проблемы

1. **langchain 0.3 → 1.x** — breaking changes, требуется рефакторинг
2. **chromadb 0.5 → 1.x** — полная переработка API
3. **Дублирование требований** — некоторые модули имеют дублирующиеся `requirements.txt`

---

## 🛠️ Рекомендации

1. **Централизовать зависимости** — использовать `pyproject.toml` для всех модулей
2. **Мигрировать LangChain** — запланировать рефакторинг на 0.3 → 1.x
3. **Мигрировать ChromaDB** — ручная миграция 0.5 → 1.x
4. **Удалить дубликаты** — объединить дублирующиеся requirements.txt

---

*Сгенерировано: 9 мая 2026 г.*
*Команда: `find . -name "requirements*.txt" | xargs cat | sort | uniq`*
