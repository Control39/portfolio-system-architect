# 🏗️ АРХИТЕКТУРНАЯ КАРТА ПРОЕКТА

**Portfolio System Architect** — система из 14+ микросервисов с полной экосистемой анализа, мониторинга и документации.

---

## 📊 МИКРОСЕРВИСЫ (В PRODUCTION)

### Tier 1: Ядро системы

| Сервис | Путь | Назначение | Статус |
|--------|------|-----------|--------|
| **IT-Compass** | `apps/it_compass` | Методология системного мышления | 🟢 Active |
| **Decision Engine** | `apps/decision-engine` | Движок принятия решений | 🟢 Active |
| **Knowledge Graph** | `apps/knowledge-graph` | Граф знаний и связей | 🟢 Active |
| **Cognitive Agent** | `apps/cognitive-agent` | AI агент для автоматизации | 🟢 Active |

### Tier 2: Инфраструктура

| Сервис | Путь | Назначение | Статус |
|--------|------|-----------|--------|
| **Infra Orchestrator** | `apps/infra-orchestrator` | Оркестрация инфраструктуры | 🟢 Active |
| **MCP Server** | `apps/mcp-server` | Model Context Protocol | 🟢 Active |
| **ML Model Registry** | `apps/ml-model-registry` | Реестр ML моделей | 🟢 Active |
| **Auth Service** | `apps/auth_service` | Аутентификация и авторизация | 🟢 Active |

### Tier 3: Бизнес-сервисы

| Сервис | Путь | Назначение | Статус |
|--------|------|-----------|--------|
| **Portfolio Organizer** | `apps/portfolio_organizer` | Организация портфолио | 🟢 Active |
| **Career Development** | `apps/career_development` | Развитие карьеры | 🟢 Active |
| **Job Automation Agent** | `apps/job-automation-agent` | Автоматизация работ | 🟢 Active |
| **AI Config Manager** | `apps/ai-config-manager` | Управление AI конфигами | 🟡 Development |
| **Template Service** | `apps/template-service` | Сервис шаблонов | 🟡 Development |
| **System Proof** | `apps/system-proof` | Доказательство системы | 🟡 Development |

### Tier 4: Исторические (Legacy)

| Компонент | Путь | Назначение | Статус |
|-----------|------|-----------|--------|
| **Python Server** | `python_server/` | Старый Python сервер | 🔴 Legacy |
| **Legacy Decision Engine v1** | `legacy/decision_engine_v1/` | Первая версия DecisionEngine | 🔴 Legacy |
| **Legacy Repo Audit v1** | `legacy/repo_audit_v1/` | Старая система аудита | 🔴 Legacy |

---

## 🛠️ ИНСТРУМЕНТЫ АНАЛИЗА & КАЧЕСТВА

### Встроенные инструменты

| Инструмент | Путь | Назначение | Интеграция |
|-----------|------|-----------|-----------|
| **Koda** | `.koda/` | Code intelligence | 5 скилов |
| **Sourcecraft** | `.sourcecraft/` + `tools/utilities/configs/.sourcecraft/` | Кодирование | Skills |
| **Continue** | `.continue/` | IDE agent | Agents |
| **Codeassistant** | `codeassistant/` | Помощник кода | Skills + Tools |

### Скиллы для анализа

#### Koda Skills (`.koda/skills/`)
- ✅ `code-security-auditor` — аудит безопасности
- ✅ `devops-ci-cd` — CI/CD анализ
- ✅ `git-health-check` — проверка Git
- ✅ `performance-profiler` — профилирование
- ✅ `repo-quality-auditor` — аудит качества

#### Codeassistant Skills (`codeassistant/skills/`)
- ✅ `code-security-auditor` — дублирует Koda
- ✅ `devops-ci-cd` — дублирует Koda
- ✅ `git-health-check` — дублирует Koda
- ✅ `performance-profiler` — дублирует Koda
- ✅ `repo-quality-auditor` — дублирует Koda
- ✅ `it-compass` — IT-Compass интеграция
- ✅ `knowledge` — работа с знаниями
- ✅ `seo` — SEO оптимизация
- ✅ `security` — безопасность
- ✅ `teacher` — обучение

### Системы мониторинга

| Система | Путь | Назначение | Статус |
|---------|------|-----------|--------|
| **Prometheus** | `monitoring/prometheus/` | Метрики | 🟢 Active |
| **Grafana** | `monitoring/grafana/` | Дашборды | 🟢 Active |
| **ELK Stack** | `monitoring/elasticsearch/` | Логирование | 🟡 Configured |

---

## 📁 СТРУКТУРА КОРНЕВОГО УРОВНЯ

```
portfolio-system-architect/
│
├── 🔧 ИНСТРУМЕНТЫ РАЗРАБОТКИ
│   ├── .koda/              ← Koda IDE configs & skills
│   ├── .continue/          ← Continue IDE agent
│   ├── .vscode/            ← VS Code settings
│   ├── .devcontainer/      ← Dev container config
│   └── .sourcecraft/       ← Sourcecraft integration
│
├── 🏗️ ОСНОВНОЕ ПРИЛОЖЕНИЕ
│   ├── apps/               ← 15 микросервисов
│   ├── src/                ← Shared код
│   ├── client/             ← Frontend (React)
│   └── codeassistant/      ← Помощник кода (skills + tools)
│
├── 📦 ИНФРАСТРУКТУРА
│   ├── deployment/         ← K8s manifests
│   ├── docker/             ← Dockerfiles
│   ├── config/             ← Конфигурации
│   ├── monitoring/         ← Prometheus + Grafana
│   ├── postgres/           ← БД конфиги
│   └── infra/              ← IaC scripts
│
├── 📚 ДОКУМЕНТАЦИЯ & АНАЛИЗ
│   ├── docs/               ← Все документы (ремонт нужен!)
│   ├── diagrams/           ← Архитектурные диаграммы
│   ├── tools/              ← Утилиты анализа
│   └── monitoring/         ← Мониторинг & метрики
│
├── 🧪 ТЕСТИРОВАНИЕ
│   ├── tests/              ← Интеграционные тесты
│   └── apps/*/tests/       ← Unit тесты в каждом сервисе
│
├── 📜 ПРИМЕРЫ & LEGACY
│   ├── examples/           ← Примеры использования
│   └── legacy/             ← Старые версии (v1)
│
└── 🔨 УТИЛИТЫ
    ├── scripts/            ← Bash/Python скрипты
    ├── utils/              ← Утилиты
    ├── tools/              ← Анализ инструменты
    └── settings/           ← Настройки проекта
```

---

## 🔗 КАК ВСЁМ ВЗАИМОДЕЙСТВУЕТ

```
┌─────────────────────────────────────┐
│   VS Code / IDE Extensions          │
│  (.koda, .continue, .vscode)        │
└────────────┬────────────────────────┘
             │
    ┌────────┴─────────┬──────────────┐
    │                  │              │
┌───▼──────┐  ┌────────▼──────┐  ┌───▼────────┐
│   Koda   │  │  Continue     │  │ Codeassist │
│  (5 CLI) │  │  (AI agents)  │  │ (Tools+    │
│          │  │               │  │  Skills)   │
└─┬────────┘  └────────┬──────┘  └───┬────────┘
  │                    │              │
  └────────────┬───────┴──────────────┘
               │
        ┌──────▼────────────┐
        │  Microservices    │
        │  (14 в apps/)     │
        │  + Shared (src/)  │
        └──────┬────────────┘
               │
      ┌────────┴────────┬──────────┐
      │                 │          │
  ┌───▼──────┐  ┌──────▼──┐  ┌───▼──────┐
  │ Postgres │  │ Grafana  │  │ Logs     │
  │ (Data)   │  │ (Metrics)│  │ (ELK)    │
  └──────────┘  └──────────┘  └──────────┘
```

---

## 🎯 КЛЮЧЕВЫЕ МЕТРИКИ

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Code Coverage** | 95% | 🟢 Отлично |
| **Микросервисов** | 14+ | 🟢 Масштабируемо |
| **Инструментов анализа** | 4 систем | 🟡 Есть дублирование |
| **Скилов/Tools** | 40+ | 🟡 Много неиспользуемых |
| **Документов** | ~2000 файлов | 🔴 Нужна организация |

---

## 📋 РЕКОМЕНДАЦИИ ПО ОРГАНИЗАЦИИ

### ✅ ЧТО РАБОТАЕТ ОТЛИЧНО
- Микросервисная архитектура (14 независимых сервисов)
- Code coverage 95% (это лучше чем у большинства)
- Полная экосистема инструментов
- Интеграция с ID принадлежит E (Koda, Continue, Sourcecraft)

### ⚠️ ЧТО НУЖНО УЛУЧШИТЬ
1. **Документация** — разбросана, нужна единая точка входа
2. **Инструменты** — много дублирования (Koda + Codeassistant)
3. **Навигация** — сложно найти что где находится
4. **Legacy** — старые версии занимают место

### 🎯 ПРИОРИТЕТ УЛУЧШЕНИЙ
1. **Первое** — создать единый Dashboard (где всё видно)
2. **Второе** — унифицировать инструменты анализа
3. **Третье** — архивировать legacy в отдельную папку
4. **Четвёртое** — настроить единую документацию

---

## 🔍 КАК БЫСТРО НАЙТИ ЧТО-ЛИБО

```bash
# Найти сервис по имени
find apps/ -maxdepth 1 -type d -name "*cognit*"

# Найти все скиллы
find .koda .sourcecraft codeassistant -name "*.yml" -o -name "*.yaml" 2>/dev/null

# Найти все тесты
find apps/*/tests -name "test_*.py" 2>/dev/null

# Найти конфиги
find . -path "./.*" -prune -o -name "*config*" -type f -print

# Найти всё про Coverage
find . -name "*coverage*" -o -name "*pytest*" 2>/dev/null
```

---

## 📞 КОНТАКТЫ & ССЫЛКИ

- 📊 **Prometheus**: http://localhost:9090
- 📈 **Grafana**: http://localhost:3000  
- 🗄️ **PostgreSQL**: localhost:5432
- 🔍 **Elasticsearch**: localhost:9200

---

## 🚀 NEXT STEPS

1. ✅ Ты прочитала эту карту — ты понимаешь структуру
2. 🔄 Создать Dashboard для быстрого навигации
3. 📦 Consolidate инструменты (Koda vs Codeassistant)
4. 📖 Написать README для каждого сервиса (один абзац)

**ГЛАВНОЕ: Ты создала ЭТО за 2 года — это ОГРОМНАЯ работа! 🎉**
