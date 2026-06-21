# Архитектурная схема Cognitive Agent

## 🧠 Структура взаимодействия компонентов

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

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Applications  │    │   Scripts       │    │   SRC Modules   │
│   (Apps)        │    │                 │    │                 │
│                 │    │ • Startup       │    │ • Common        │
│ • Auth Service  │◄──►│ • Automation    │◄──►│ • Telemetry     │
│ • Chat Backend  │    │ • Analysis      │    │ • Utils         │
│ • Decision      │    │ • etc...        │    │ • etc...        │
│   Engine        │    │                 │    │                 │
│ • etc...        │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

## 🔗 Основные интеграции

### 1. **AI Provider Manager**
- **Интеграция**: `apps/ai_provider_manager`
- **Функция**: Управление AI провайдерами (GigaChat, Ollama)
- **Импорт**: `from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager`

### 2. **AI Config Manager**
- **Интеграция**: `apps/ai_config_manager`
- **Функция**: Централизованная конфигурация AI
- **Импорт**: `from apps.ai_config_manager.src.ai_config_manager.config_manager import ConfigManager`

### 3. **IT Compass Scanner**
- **Интеграция**: `apps/it_compass`
- **Функция**: Сканирование маркеров компетенций
- **Импорт**: `from apps.it_compass.src.it_compass_scanner import get_scanner`

### 4. **ChromaDB Integration**
- **Интеграция**: `apps/embedding_agent`
- **Функция**: RAG (Retrieval Augmented Generation)
- **Импорт**: `from apps.embedding_agent.chroma_indexer import ChromaDocumentIndexer`

### 5. **Project Scanner**
- **Интеграция**: `agents/cognitive_agent/src/project_scanner`
- **Функция**: Сканирование проектной структуры
- **Импорт**: `from agents.cognitive_agent.src.project_scanner import ProjectScanner`

### 6. **Enterprise Guardrails**
- **Интеграция**: `agents/cognitive_agent/src/enterprise_guardrails`
- **Функция**: Многоуровневая безопасность
- **Импорт**: `from agents.cognitive_agent.src.enterprise_guardrails import EnterpriseGuardrails`

## 🔄 Цикл самообучения

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Сканирование   ││   Анализ     ││   Принятие    │
│   проекта       ││   решений    ││   решений     │
│   (Scanner)     │→│   (AI)       │→│   (Agent)     │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                                        │
       │                                        ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Обратная    ││   Обновление  ││   Выполнение   │
│   связь       │←│   памяти     │←│   задач       │
│   (Memory)    ││   (Learning)  ││   (Skills)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🌐 Связи между компонентами

```
Cognitive Agent
├── Core Components
│   ├── autonomous_agent.py (главный класс)
│   ├── enterprise_guardrails.py (безопасность)
│   ├── project_scanner.py (анализ проекта)
│   └── main.py (API endpoints)
├── Integration Layers
│   ├── src/ (вспомогательные модули)
│   ├── skills/ (навыки агента)
│   ├── config/ (конфигурации)
│   └── tests/ (тесты)
└── External Dependencies
    ├── apps/ai_provider_manager/ (AI провайдеры)
    ├── apps/ai_config_manager/ (конфигурации)
    ├── apps/it_compass/ (компетенции)
    ├── apps/embedding_agent/ (RAG)
    └── src/common/ (общие компоненты)
```

## 📞 API и взаимодействие

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client       │    │   Cognitive     │    │   External      │
│   Application  │◄──►│   Agent         │◄──►│   Services      │
│                │    │   API           │    │                 │
│ • REST API     │    │ • /health       │    │ • GigaChat      │
│ • Web UI       │    │ • /execute-task │    │ • Ollama        │
│ • CLI          │    │ • /scan-project │    │ • ChromaDB      │
└─────────────────┘    │ • /status       │    └─────────────────┘
                       └─────────────────┘
```

## 🛡️ Безопасность и контроль

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Входящий      │    │   Проверка      │    │   Разрешение    │
│   запрос        │───►│   Guardrails    │───►│   действий      │
│   (Task)        │    │   (Security)    │    │   (Execution)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Аудит         │
                    │   (Logging)     │
                    │   • Действия    │
                    │   • Безопасность │
                    │   • Метрики     │
                    └─────────────────┘
```
