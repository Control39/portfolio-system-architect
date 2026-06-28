# 🏗️ Архитектурные правила для ИИ-разработчиков

> **ВАЖНО:** Это обязательные правила. Нарушение архитектуры приведёт к техническому долгу и сломанной масштабируемости.

---

## 📐 Трёхуровневая архитектура (strict top-down dependencies)

```
┌─────────────────────────────────────────────────────────────┐
│                    УРОВЕНЬ 3: АГЕНТЫ                         │
│              (Когнитивные системы, AI)                       │
│                                                             │
│  🤖 agents/cognitive_agent/                                 │
│     - Автономный агент                                      │
│     - Анализ кода, генерация тестов                         │
│     - Принятие решений                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓ использует
┌─────────────────────────────────────────────────────────────┐
│                  УРОВЕНЬ 2: СЕРВИСЫ (apps/)                  │
│              (21 независимый микросервис)                    │
│                                                             │
│  🏢 apps/decision_engine/         — Движок решений          │
│  🏢 apps/job_automation_agent/    — Автоматизация задач     │
│  🏢 apps/knowledge_graph/         — Граф знаний             │
│  🏢 apps/it_compass/              — IT компас               │
│  🏢 apps/mcp_server/              — MCP сервер              │
│  🏢 apps/auth_service/            — Аутентификация          │
│  🏢 apps/chat_backend/            — Chat backend            │
│  🏢 apps/ml_model_registry/       — Реестр ML моделей       │
│  🏢 apps/portfolio_organizer/     — Организатор портфолио   │
│  🏢 apps/career_development/      — Развитие карьеры        │
│  🏢 apps/infra_orchestrator/      — Инфраструктурный оркестр│
│  🏢 apps/system_proof/            — Системные доказательства│
│  🏢 apps/thought_architecture/    — Архитектура мышления    │
│  🏢 apps/embedding_agent/         — Embedding агент         │
│  🏢 apps/ai_provider_manager/     — Управление AI провайдерами│
│  🏢 apps/assistant_orchestrator/  — Оркестратор ассистентов │
│  🏢 apps/context_builder/         — Построение контекста    │
│  🏢 apps/competency_gap_engine/   — Анализ компетенций      │
│  🏢 apps/template_service/        — Сервис шаблонов         │
│  🏢 apps/ai_config_manager/       — Централизованная конфигурация│
│                                                             │
│  Каждый сервис:                                             │
│  ├── src/           — Код сервиса                           │
│  ├── tests/         — Тесты сервиса                         │
│  ├── docs/          — Документация                          │
│  └── README.md      — Описание сервиса                      │
└─────────────────────────────────────────────────────────────┘
                              ↓ используют
┌─────────────────────────────────────────────────────────────┐
│                  УРОВЕНЬ 1: АТОМЫ (src/)                     │
│              (Базовые переиспользуемые компоненты)           │
│                                                             │
│  📦 src/ai/              — AI интеграции                    │
│     ├── config/          — AI Config Manager                │
│     ├── gigachat_bridge/ — GigaChat                         │
│     └── ollama_bridge/   — Ollama                           │
│                                                             │
│  📦 src/common/          — Общие утилиты                    │
│     ├── async_helpers/   — Асинхронные помощники            │
│     └── health_check/    — Проверка здоровья                │
│                                                             │
│  📦 src/config/          — Конфигурации                     │
│                                                             │
│  📦 src/core/            — Базовые компоненты               │
│     ├── powershell/      — PowerShell скрипты               │
│     └── python/          — Python утилиты                   │
│                                                             │
│  📦 src/infrastructure/  — Инфраструктурный код             │
│                                                             │
│  📦 src/interfaces/      — Интерфейсы и API                 │
│                                                             │
│  📦 src/security/        — Безопасность                     │
│     ├── rate_limiter/    — Rate limiting                    │
│     ├── secret_manager/  — Управление секретами             │
│     ├── secure_path/     — Валидация путей                  │
│     ├── sandbox_executor/ — Песочница                       │
│     └── file_type_validator/ — Валидация файлов             │
│                                                             │
│  📦 src/shared/          — Общие модели                     │
│     └── schemas/         — YAML/JSON схемы                  │
│                                                             │
│  📦 src/vector_store/    — Векторное хранилище              │
│     ├── chroma_impl/     — ChromaDB                         │
│     └── embedder/        — Embedding                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Правила импортов (ОБЯЗАТЕЛЬНО К СОБЛЮДЕНИЮ)

### 1. Агенты могут использовать сервисы и атомы

```python
# ✅ Правильно - агент использует сервис
from apps.decision_engine.src.decision_engine import DecisionEngine

# ✅ Правильно - агент использует атом
from src.security.rate_limiter import RateLimiter
from src.security.secret_manager import SecretManager

# ✅ Правильно - агент использует атом
from src.ai.config import ConfigManager
```

### 2. Сервисы могут использовать ТОЛЬКО атомы

```python
# ✅ Правильно - сервис использует атом
from src.ai.config import ConfigManager
from src.security.rate_limiter import RateLimiter

# ❌ НЕЛЬЗЯ - сервис не должен зависеть от другого сервиса
from apps.job_automation_agent.job_agent import JobAgent

# ❌ НЕЛЬЗЯ - сервис не должен зависеть от агентов
from agents.cognitive_agent.src.base_agent import BaseCognitiveAgent
```

### 3. Атомы не должны зависеть от других уровней

```python
# ✅ Правильно - атом использует только стандартные библиотеки
import os
from typing import Optional
from dataclasses import dataclass

# ❌ НЕЛЬЗЯ - атом не должен зависеть от сервисов
from apps.decision_engine.src.main import app

# ❌ НЕЛЬЗЯ - атом не должен зависеть от агентов
from agents.cognitive_agent.src.base_agent import BaseCognitiveAgent
```

---

## 📂 Структура проекта

```
portfolio-system-architect/
├── agents/                           # АГЕНТЫ (Уровень 3)
│   └── cognitive_agent/
│       ├── src/                     # Модули агента
│       ├── skills/                  # 25+ навыков
│       ├── config/                  # Конфигурация (guardrails.yaml)
│       ├── tests/                   # Тесты агента
│       └── enterprise_guardrails.py # Enterprise guardrails
│
├── apps/                            # СЕРВИСЫ (Уровень 2)
│   ├── decision_engine/
│   │   ├── src/                     # Код сервиса
│   │   ├── tests/                   # Тесты сервиса
│   │   ├── docs/                    # Документация
│   │   └── README.md                # Описание сервиса
│   ├── job_automation_agent/
│   ├── knowledge_graph/
│   ├── it_compass/
│   ├── auth_service/
│   └── ... (18+ других сервисов)
│
├── src/                             # АТОМЫ (Уровень 1)
│   ├── ai/                          # AI интеграции
│   │   ├── config/                  # AI Config Manager
│   │   ├── gigachat_bridge/         # GigaChat
│   │   └── ollama_bridge/           # Ollama
│   ├── common/                      # Общие утилиты
│   │   ├── async_helpers/           # Асинхронные помощники
│   │   └── health_check/            # Проверка здоровья
│   ├── config/                      # Конфигурации
│   ├── core/                        # Базовые компоненты
│   │   ├── powershell/              # PowerShell скрипты
│   │   └── python/                  # Python утилиты
│   ├── infrastructure/              # Инфраструктурный код
│   ├── interfaces/                  # Интерфейсы и API
│   ├── security/                    # Безопасность
│   │   ├── rate_limiter/            # Rate limiting
│   │   ├── secret_manager/          # Управление секретами
│   │   ├── secure_path/             # Валидация путей
│   │   ├── sandbox_executor/        # Песочница
│   │   └── file_type_validator/     # Валидация файлов
│   ├── shared/                      # Общие модели
│   │   └── schemas/                 # YAML/JSON схемы
│   └── vector_store/                # Векторное хранилище
│       ├── chroma_impl/             # ChromaDB
│       └── embedder/                # Embedding
│
├── tests/                           # Общие тесты
│   ├── e2e/                         # End-to-end тесты
│   ├── integration/                 # Интеграционные тесты
│   └── fixtures/                    # Фикстуры
│
├── docs/                            # Документация
│   ├── architecture/                # Архитектурные решения
│   │   ├── decisions/               # ADR (Architecture Decision Records)
│   │   └── ai-developer-rules.md    # Это файл
│   └── professional-journey/        # Профессиональный путь
│
├── requirements.in                  # Ядро: основные зависимости
├── requirements.txt                 # Ядро: полный снимок зависимостей
├── requirements-dev.txt             # Ядро: зависимости для разработки
└── pyproject.toml                   # Конфигурация проекта
```

---

## 🔗 Как сервисы взаимодействуют

### 1. Через общие атомы (src/)

```python
# apps/decision_engine/src/main.py
from src.ai.config import ConfigManager  # ✅ Использует общий AI Config
from src.security.rate_limiter import RateLimiter  # ✅ Использует общий rate limiter
```

### 2. Через прокси-импорты (для миграций)

```python
# apps/decision_engine/src/config_integration.py
try:
    from src.ai.config import ConfigManager  # Новая локация
    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    # Fallback на старую локацию (только для миграций)
```

### 3. Через API (если сервисы общаются по сети)

```python
# apps/chat_backend/src/main.py
# HTTP API для общения с другими сервисами
```

---

## 🎯 Принципы архитектуры

### ✅ Правильно:

1. **Атомы независимы** — `src/ai/config/` не зависит от сервисов
2. **Сервисы используют атомы** — `apps/decision_engine/` импортирует из `src/`
3. **Агенты используют сервисы** — `agents/cognitive_agent/` импортирует из `apps/`
4. **Тесты рядом с кодом** — `apps/decision_engine/tests/` тестирует `apps/decision_engine/src/`
5. **Общие тесты в корне** — `tests/e2e/`, `tests/integration/`

### ❌ Неправильно:

1. **Сервисы зависят друг от друга** — `apps/decision_engine/` НЕ ДОЛЖЕН импортировать из `apps/job_automation_agent/`
2. **Атомы зависят от сервисов** — `src/ai/config/` НЕ ДОЛЖЕН импортировать из `apps/`
3. **Тесты разбросаны** — тесты сервиса должны быть в `apps/*/tests/`, а не в `tests/`

---

## 🔒 Безопасность (Обязательные правила)

### Все секреты должны проходить через `src/security/`

```python
# ✅ Правильно
from src.security.secret_manager import SecretManager
from src.security.rate_limiter import RateLimiter

# ❌ НЕЛЬЗЯ
# Хардкод секретов
API_KEY = "secret123"  # pragma: allowlist secret

# ❌ НЕЛЬЗЯ
# Импорт из агентов
from agents.cognitive_agent.security.secret_manager import SecretManager
```

### Все path operations должны использовать `src/security/secure_path.py`

```python
# ✅ Правильно
from src.security.secure_path import SecurePath

secure_path = SecurePath(project_path)
safe_path = secure_path.resolve(user_input)

# ❌ НЕЛЬЗЯ
# Прямая работа с путями
path = Path(user_input)  # Может быть path traversal атака
```

### Все rate limiting через `src/security/rate_limiter.py`

```python
# ✅ Правильно
from src.security.rate_limiter import RateLimiter

limiter = RateLimiter(max_calls=100, window_seconds=60)
limiter.check_rate_limit("api:user123")

# ❌ НЕЛЬЗЯ
# Свой rate limiting
count = 0
if count > 100:  # Неправильная реализация
    raise Exception("Too many requests")
```

---

## 📝 Документация (Обязательные правила)

1. **Каждый сервис имеет `README.md`** в корне
2. **Каждый модуль имеет docstrings** на Python
3. **Архитектурные решения описываются в `docs/architecture/decisions/`** (ADR)
4. **Каждый коммит должен ссылаться на ADR** если меняет архитектуру

---

## 🧪 Тестирование

### Обязательные тесты для каждого сервиса:

```bash
# Запуск тестов сервиса
pytest apps/decision_engine/tests/

# Запуск тестов атома
pytest src/security/tests/

# Запуск всех тестов
pytest
```

### Покрытие кода:

- Сервисы: минимум 80%
- Атомы: минимум 90%
- Безопасность: 100% (критично!)

---

## 🚀 Запуск проекта

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки
pip install -r requirements-dev.txt

# Запуск тестов
pytest

# Запуск линтеров
ruff check src/
ruff format src/

# Запуск сервиса
cd apps/decision_engine
python -m src.main
```

---

## 📚 Связанные документы

- [`ARCHITECTURE.md`](../../ARCHITECTURE.md) — Общая архитектура
- [`AGENTS.md`](../../AGENTS.md) — Информация об авторе
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — Вклад в проект
- [`docs/architecture/atoms-and-molecules.md`](../../docs/architecture/atoms-and-molecules.md) — Атомы и молекулы
- [`docs/architecture/dependency-management.md`](../../docs/architecture/dependency-management.md) — Управление зависимостями

---

## ⚠️ ПРОВЕРКА УТВЕРЖДЕНИЙ АГЕНТА

Cognitive Agent склонен к галлюцинациям — он может выдумывать
"нарушения архитектуры", которых нет.

ПЕРЕД тем как принимать любое утверждение агента:
1. Проверь его против docs/architecture/ai-developer-rules.md
2. Попроси агента процитировать документацию
3. Если цитаты нет — утверждение ложное

Пример:
- Агент: "Нарушение: агент импортирует из src/"
- Документация: "✅ Агенты могут использовать атомы из src/"
- Вывод: Агент неправ

---

*Последнее обновление: 2026-06-27*
*Версия: 2.0*
*Статус: Актуально*
