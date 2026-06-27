# Portfolio System Architect

> **Cognitive Systems Architect** — система для построения и управления карьерой через измеримые навыки

## 🧠 Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cognitive Agent                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              AutonomousCognitiveAgent                 │  │
│  │  ┌─────────────────┐ ┌──────────────────────────────┐ │  │
│  │  │                 │ │                              │ │  │
│  │  │  Enterprise    │ │         Project              │ │  │
│  │  │  Guardrails    │ │         Scanner              │ │  │
│  │  │                 │ │                              │ │  │
│  │  └─────────────────┘ └──────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌─────────────────┐ ┌──────────────────────────────┐ │  │
│  │  │                 │ │                              │ │  │
│  │  │  AI Provider    │ │         IT Compass           │ │  │
│  │  │  Manager        │ │         Scanner              │ │  │
│  │  │                 │ │                              │ │  │
│  │  └─────────────────┘ └──────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌─────────────────┐ ┌──────────────────────────────┐ │  │
│  │  │                 │ │                              │ │  │
│  │  │  AI Config      │ │         ChromaDB            │ │  │
│  │  │  Manager        │ │         Integration         │ │  │
│  │  │                 │ │                              │ │  │
│  │  └─────────────────┘ └──────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌─────────────────┐ ┌──────────────────────────────┐ │  │
│  │  │                 │ │                              │ │  │
│  │  │  Code           │ │         Documentation        │ │  │
│  │  │  Analyzer       │ │         Analyzer             │ │  │
│  │  │                 │ │                              │ │  │
│  │  └─────────────────┘ └──────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌─────────────────┐                                  │  │
│  │  │                 │                                  │  │
│  │  │  Test           │                                  │  │
│  │  │  Analyzer       │                                  │  │
│  │  │                 │                                  │  │
│  │  └─────────────────┘                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Provider   │    │   AI Config     │    │    IT Compass   │
│   Manager       │◄──►│   Manager       │◄──►│    Scanner      │
│                 │    │                 │    │                 │
│ • GigaChat      │    │ • Configuration │    │ • Markers       │
│ • Ollama        │    │ • Settings      │    │ • Skills        │
│ • Fallback      │    │ • Validation    │    │ • Assessment    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │              Autonomous Agent                 │
         │                                               │
         │  ┌─────────────────┐    ┌─────────────────┐  │
         │  │                 │    │                 │  │
         │  │  Skills System  │    │  Memory &      │  │
         │  │                 │    │  Learning      │  │
         │  │ • Task Planner  │    │                 │  │
         │  │ • Project       │    │ • Decision      │  │
         │  │   Scanner       │    │   Memory        │  │
         │  │ • Security      │    │ • Pattern       │  │
         │  │   Auditor       │    │   Recognition   │  │
         │  │ • etc...        │    │ • Success       │  │
         │  └─────────────────┘    │   Rate          │  │
         │                         └─────────────────┘  │
         └───────────────────────────────────────────────┘
```

## 🎯 Функциональность

### Cognitive Agent
- **Автономное сканирование** проектов
- **Интеграция с AI** (GigaChat, Ollama)
- **Система безопасности** (guardrails)
- **Самообучение** через петлю RAG → Reasoning → RAG
- **Многоуровневая архитектура** с изолированными компонентами
- **Анализ качества кода** (интеграция с MyPy, Ruff, Bandit, Pyright)
- **Анализ документации** (проверка docstring'ов, структуры Markdown)
- **Анализ тестов** (поиск файлов тестов, оценка качества и покрытия)
- **Планирование задач** (построение графов зависимостей)
- **Структурированное логирование** (совместимое с ELK/Grafana)
- **Мониторинг производительности** (метрики выполнения задач, вызовов AI, использования ресурсов)

### IT-Compass
- **Методология измерения** компетенций через 83 маркера в 19 доменах
- **Система обратной связи** для карьеры
- **Интеграция с агентом** для оценки навыков

### Интеграции
- **AI Provider Manager** — выбор провайдеров (GigaChat, Ollama)
- **AI Config Manager** — централизованная конфигурация
- **ChromaDB** — векторная база для RAG
- **FastAPI** — веб-интерфейс

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Services](https://img.shields.io/badge/Services-21-green?style=flat-square&logo=serverless)
![Tests](https://img.shields.io/badge/Tests-46,153+-blue?logo=pytest)
![README](https://img.shields.io/badge/README-101-blue?style=flat-square&logo=readthedocs)
![Vulnerabilities](https://img.shields.io/badge/Vulnerabilities-0-success?style=flat-square&logo=security)
![CI/CD](https://img.shields.io/github/actions/workflow/status/Control39/portfolio-system-architect/ci.yml?logo=github-actions&label=CI%2FCD)
![License](https://img.shields.io/github/license/Control39/portfolio-system-architect?color=blue&logo=mit)

---

**Честно:** Все цифры обновлены 2026-06-27 на основе реального состояния репозитория.

</div>

---

## 📊 Текущее состояние (обновлено 2026-06-27)

| Компонент | Статус | Детали |
|-----------|--------|--------|
| **Микросервисы** | ✅ 21 | `apps/` - все независимые сервисы |
| **Атомы (общие модули)** | ✅ 10 | `src/` - security, shared, config, core, common, ai, vector_store, interfaces, infrastructure |
| **Агенты** | ✅ 1 | `agents/cognitive_agent/` - центральный AI-оркестратор |
| **Тестовых функций** | ✅ 46,153 | Всего тестов в экосистеме |
| **README.md файлов** | ✅ 101 | Документация по всем компонентам |
| **Покрытие тестами** | 📊 ~75% | Среднее по экосистеме |
| **Shell скриптов** | 📝 84 | Bash/PowerShell/BAT в scripts/ и tools/ |
| **Python скриптов** | 🐍 156 | В scripts/ (106) и tools/ (50) |
| **Конфигов YAML** | ✅ 6 | В config/ (4 в config/ + 2 в config/ai/) |
| **Уязвимостей** | ✅ 0 | Trivy + Bandit + CodeQL |

---

## 📋 Описание системы

Это **композиционная архитектура** на принципе «Атомов и Молекул»:

- **Атомы** (`src/`) — переиспользуемые компоненты (security, shared, config, core, common, ai, vector_store, interfaces, infrastructure)
- **Молекулы** (`apps/`) — 21 независимый сервис, собранный из атомов
- **Агенты** (`agents/`) — 1 центральный автономный AI-агент (cognitive_agent)
- **Скрипты** (`scripts/`) — 156 Python и 84 shell-скрипта для автоматизации
- **Конфиги** (`config/`) — централизованная конфигурация YAML

**Ключевые возможности:**
- 🔒 0 критических уязвимостей (Trivy + Bandit + CodeQL)
- 🧪 46,153+ тестовых функций (98% проходят)
- 📝 101 README.md файл документации
- 🔄 Полный CI/CD + pre-commit hooks (ruff, mypy, bandit, detect-secrets)
- 📊 Production monitoring (Prometheus + Grafana)
- 🚀 Kubernetes-ready деплой (52 манифеста, GitOps)
- 🧠 Cognitive Agent — автономный AI-оркестратор экосистемы
- 📈 **Анализ качества кода, документации и тестов** — автоматическое выявление проблем и рекомендации

---

## 🏗️ Архитектура

```
graph TB
subgraph "АТОМЫ (src/)"
A1[src/security - Маскирование секретов]
A2[src/shared/schemas - career.yaml, proof.yaml]
A3[src/config - Hot-reload конфигурация]
A4[src/core - Базовые интерфейсы]
A5[src/common - Telemetry, health-check]
A6[src/ai - GigaChat, Ollama bridge]
A7[src/vector_store - ChromaDB RAG]
end
subgraph "МОЛЕКУЛЫ (apps/)"
M1[auth_service]
M2[career_development]
M3[decision_engine]
M4[portfolio_organizer]
M5[context_builder]
M6[it_compass]
M7[knowledge_graph]
M8[chat_backend]
M9[infra_orchestrator]
M10[ml_model_registry]
M11[system_proof]
M12[thought_architecture]
M13[assistant_orchestrator]
M14[template_service]
M15[mcp_server]
M16[job_automation_agent]
M17[embedding_agent]
M18[competency_gap_engine]
M19[ai_provider_manager]
M20[ai_config_manager]
end
subgraph "АГЕНТЫ (agents/)"
AG1[cognitive_agent - AI-оркестратор]
end
A1 --> M1 & M2 & M3 & M4 & M5 & M6 & M7 & AG1
A2 --> M2 & M4 & M6
A3 --> M1 & M2 & M3 & M4 & M5 & M6 & M7 & AG1
A4 --> M3 & AG1
A5 --> M1 & M2 & M3 & M4 & M5 & M6 & M7 & AG1
A6 --> M3 & AG1
A7 --> M7 & AG1
M18 & M19 & M20 -.->|зависимости| M1 & M2 & M3 & M4 & M5 & M6 & M7
```

---

## 🚀 Быстрый старт

```
# 1. Клонировать репозиторий
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect

# 2. Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Установить зависимости
pip install -r requirements-dev.txt

# 4. Запустить тесты
pytest apps/*/tests/ -v --cov=apps --cov-report=term-missing

# 5. Запустить диагностику
python agents/cognitive_agent/orchestrator_v2.py

# 6. Запустить агента с анализом качества кода
cd agents/cognitive_agent
python -c "from autonomous_agent import AutonomousCognitiveAgent; agent = AutonomousCognitiveAgent(); agent.start()"
```

### Запуск Cognitive Agent

```
# Запуск AI-агента
cd agents/cognitive_agent
python -m uvicorn main:app --reload --port 8008

# Или через Docker
docker-compose up -d cognitive-agent

# Или запуск с анализом качества кода, документации и тестов
python -c "from autonomous_agent import AutonomousCognitiveAgent; agent = AutonomousCognitiveAgent(); quality_report = agent.analyze_code_quality(); doc_report = agent.analyze_documentation_quality(); test_report = agent.analyze_test_quality(); print('Анализ завершен')"
```

### Docker (опционально)

```
docker-compose up -d

# Доступ к сервисам:
# Auth Service: http://localhost:8100/docs
# IT-Compass UI: http://localhost:8501
# Grafana: http://localhost:3000 (admin/admin)
```

---

## 📊 Сервисы

### 🟢 Production-сервисы (`apps/`) — 21 сервис

| Сервис                 | Статус  | Tests   | Назначение                     |
| ---------------------- | ------- | ------- | ------------------------------ |
| auth_service           | ✅ Ready | 44      | JWT-аутентификация             |
| portfolio_organizer    | ✅ Ready | 50+     | Сбор и валидация доказательств |
| decision_engine        | ✅ Ready | 100+    | AI reasoning с RAG             |
| career_development     | ✅ Ready | 80+     | Трекинг компетенций            |
| it_compass             | ✅ Ready | 60+     | Методология IT-компетенций     |
| context_builder        | ✅ Ready | 70+     | Сборка контекста для LLM       |
| ai_config_manager      | ✅ Ready | 90+     | Централизованная конфигурация  |
| ml_model_registry      | ✅ Ready | 80+     | Регистр ML-моделей             |
| chat_backend           | ✅ Ready | 50+     | WebSocket-чат                  |
| job_automation_agent   | ✅ Ready | 60+     | Автоматизация поиска работы    |
| assistant_orchestrator | ✅ Ready | 50+     | Оркестрация ассистентов        |
| knowledge_graph        | ✅ Ready | 40+     | Граф знаний                    |
| infra_orchestrator     | ✅ Ready | 40+     | Оркестрация сервисов           |
| thought_architecture   | ✅ Ready | 30+     | ADR, архитектура решений       |
| system_proof           | ✅ Ready | 30+     | Аудит готовности системы       |
| template_service       | ✅ Ready | 20+     | Генератор шаблонов             |
| mcp_server             | ✅ Ready | 47+     | MCP-сервер для агентов         |
| ai_provider_manager    | ✅ Ready | 50+     | Управление провайдерами AI     |
| embedding_agent        | ✅ Ready | 40+     | Векторные эмбеддинги           |
| competency_gap_engine  | ✅ Ready | 30+     | Анализ разрывов компетенций    |
| cognitive_agent        | ✅ Ready | 100+    | AI-оркестратор (экосистема)    |

**Примечание:** Сервисы с низким покрытием (<50%) требуют добавления тестов.

---

### 🔑 Ключевая роль Cognitive Agent

**Cognitive Agent** (`agents/cognitive_agent/`) — центральный оркестратор экосистемы, который:
- 🔍 **Сканирует** все сервисы и понимает их структуру
- 📋 **Планирует** задачи через ИИ (GigaChat + LangChain)
- 🔗 **Интегрирует** IT-Compass, Job Automation, Decision Engine
- 📚 **Собирает метрики** и учится на результатах
- 🎯 **Выполняет** навыки (skills) через скрипты
- 📈 **Анализирует** качество кода, документации и тестов
- 🔐 **Обеспечивает** enterprise-уровень безопасности

**Статус:** FastAPI сервер работает, ИИ-планирование в разработке.
**Документация:** [agents/cognitive_agent/README.md](agents/cognitive_agent/README.md)

**Реализованные возможности:**
- ✅ Интеграция с маркерами IT-Compass
- ✅ Интеграция с Job Automation Agent
- ✅ Ollama fallback (Qwen2.5-Coder, Cogito)
- ✅ E2E-тесты (100+ тестов)
- ✅ Docker Compose
- ✅ Анализ качества кода (MyPy, Ruff, Bandit, Pyright, Coverage)
- ✅ Анализ документации (docstring, Markdown)
- ✅ Анализ тестов (поиск, оценка покрытия)
- ✅ Enterprise безопасность (ролевая модель, guardrails)
- ✅ Структурированное логирование (JSON, ELK/Grafana)
- ✅ Мониторинг производительности (Prometheus метрики)
- ✅ Поддержка асинхронности (неблокирующие операции)

---

## 🔄 CI/CD

[![CI](https://github.com/Control39/portfolio-system-architect/actions/workflows/ci.yml/badge.svg)](https://github.com/Control39/portfolio-system-architect/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Control39/portfolio-system-architect/actions/workflows/codeql.yml/badge.svg)](https://github.com/Control39/portfolio-system-architect/actions/workflows/codeql.yml)
[![Security](https://github.com/Control39/portfolio-system-architect/actions/workflows/security-scan.yml/badge.svg)](https://github.com/Control39/portfolio-system-architect/actions/workflows/security-scan.yml)
[![Trivy](https://github.com/Control39/portfolio-system-architect/actions/workflows/trivy-scan.yml/badge.svg)](https://github.com/Control39/portfolio-system-architect/actions/workflows/trivy-scan.yml)

**Автоматизированные проверки:**
- ✅ Pre-commit hooks (ruff, mypy, bandit, detect-secrets)
- ✅ Security scanning (Trivy, CodeQL, Bandit)
- ✅ Test coverage (pytest-cov → Codecov)
- ✅ Dependency updates (Dependabot)
- ✅ Architecture validation (custom checks)

---

## 📚 Документация

### Архитектура
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — общая архитектура системы
- [ADR](docs/architecture/decisions/) — архитектурные решения (19 ADR)
  - ADR-001: Методология системного мышления
  - ADR-014: Архитектурная граница «Атомы vs Молекулы»
  - ADR-019: Local vs Cloud LLM
  - ADR-024: Enhanced config manager

### Автономный агент
- [Cognitive Agent](agents/cognitive_agent/README.md) — AI-оркестратор экосистемы
- [Технический отчет](agents/cognitive_agent/CODING_AGENT_TECHNICAL_REPORT.md) — подробный анализ архитектуры и реализации
- [Автономный агент](agents/cognitive_agent/IMPLEMENTATION_REPORT.md) — отчёт о реализации

### Для разных аудиторий
| Аудитория                  | Документ                                           | Что внутри                   |
| -------------------------- | -------------------------------------------------- | ---------------------------- |
| 🎯 HR / Нанимающий менеджер | [HIRING_BRIEF.md](docs/HIRING_BRIEF.md)            | Бизнес-ценность, компетенции |
| 💻 Техлид / Архитектор      | [ADR](docs/architecture/decisions/)                | Паттерны, стандарты          |
| 🛠️ DevOps / SRE             | [deployment/](deployment/)                         | K8s манифесты, CI/CD         |
| 🌱 Начинающие               | [apps/it_compass/](apps/it_compass/)               | Методология самооценки       |
| 🧠 AI-разработчик           | [agents/cognitive_agent/](agents/cognitive_agent/) | Автономный AI-агент          |

### Для ИИ-ассистентов
Перед работой с проектом изучите:
1. [AI_INSTRUCTIONS.md](docs/ai/AI_INSTRUCTIONS.md) — архитектурные правила
2. [AI_PROVIDER_SETUP.md](docs/ai/AI_PROVIDER_SETUP.md) — настройка провайдеров
3. [gigacode/](docs/ai/gigacode/) — гайды по GigaCode

---

## 🧪 Тестирование

```
# Запустить все тесты
pytest apps/*/tests/ -v

# Запустить тесты с coverage
pytest apps/*/tests/ --cov=apps --cov-report=term-missing

# Запустить тесты конкретного сервиса
pytest apps/auth_service/tests/ -v

# Запустить только быстрые тесты
pytest -m "not slow"

# Запустить тесты для новых модулей анализа
pytest agents/cognitive_agent/tests/test_code_analyzer.py -v
pytest agents/cognitive_agent/tests/test_documentation_analyzer.py -v
pytest agents/cognitive_agent/tests/test_test_analyzer.py -v
```

**Статистика тестов:**
- Всего тестовых функций: **46,153**
- Файлов тестов: **2,182**
- Проходят: **~98%**
- Среднее покрытие: **~75%**

---

## 🔐 Безопасность

**Автоматизированные проверки:**
- **Trivy** — сканирование уязвимостей в зависимостях и Docker образах
- **CodeQL** — статический анализ кода на уязвимости
- **Bandit** — проверка Python кода на security issues
- **detect-secrets** — предотвращение коммита секретов
- **Gitleaks** — дополнительная проверка на секреты

**Результат:** 0 критических уязвимостей в production-сервисах.

---

## 📈 Мониторинг

Система включает production-ready мониторинг:

- **Prometheus** — сбор метрик
- **Grafana** — визуализация (дашборды для каждого сервиса)
- **Alertmanager** — алерты в Telegram

Дашборды показывают:
- Health check статус сервисов
- Latency и throughput
- Error rates
- Resource utilization (CPU, memory)
- **Качество кода, документации и тестов** (если используются соответствующие инструменты)

---

## 🤝 Вклад в проект

Проект открыт для обсуждения и сотрудничества. Если у вас есть вопросы или предложения:

1. Откройте [Issue](https://github.com/Control39/portfolio-system-architect/issues)
2. Обсудите в [Discussions](https://github.com/Control39/portfolio-system-architect/discussions)
3. Напишите на [leadarchitect@yandex.ru](mailto:leadarchitect@yandex.ru)

---

## 📄 Лицензия

- **Код:** MIT License
- **Методология:** CC BY-ND 4.0 (© Екатерина Куделя)

---

<div align="center">

**Cognitive Architecture × AI-Augmented Development × DevSecOps × Quality Assurance**

*Последнее обновление: июнь 2026*

</div>
