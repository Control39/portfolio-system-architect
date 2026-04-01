# Архитектурная интеграция проектов

## Общая схема экосистемы

```mermaid
graph TB
    subgraph "Платформа Portfolio System Architect"
        PO[Portfolio-Organizer<br/>Web UI]
        IT[IT-Compass<br/>Трекинг навыков]
        CDS[Career Development<br/>Карьерные маркеры]
    end

    subgraph "AI & Reasoning"
        CR[Cloud-Reason<br/>Reasoning API]
        YGPT[YandexGPT / GigaChat]
        RAG[RAG с ChromaDB]
        SP[System-Proof<br/>Верификация]
    end

    subgraph "Infrastructure & Automation"
        ARCH[Arch-Compass<br/>PowerShell Framework]
        SEC[Security Scanner<br/>Secret Manager]
        CI[CI/CD SourceCraft]
        K8S[Kubernetes Deployment]
    end

    subgraph "Data & Models"
        MLR[ML Model Registry]
        OS[Object Storage<br/>Файлы контекста]
        DB[(PostgreSQL<br/>Career Data)]
    end

    %% Connections
    PO --> IT
    PO --> CR
    IT --> CDS
    CDS --> CR
    CR --> YGPT
    CR --> RAG
    CR --> SP
    ARCH --> SEC
    ARCH --> CI
    CI --> K8S
    K8S --> PO
    K8S --> CR
    K8S --> MLR
    MLR --> OS
    CR --> OS
    IT --> DB
```

## Детализация Cloud-Reason API

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant API as Cloud-Reason API
    participant LLM as YandexGPT
    participant Storage as Object Storage
    participant RAG as ChromaDB

    User->>API: POST /chat {message, context}
    API->>Storage: Загрузить контекстные файлы
    Storage-->>API: Контекст
    API->>RAG: Поиск релевантных чанков
    RAG-->>API: Релевантные документы
    API->>LLM: Запрос с контекстом
    LLM-->>API: Reasoning ответ
    API-->>User: Ответ + trace
```

## Интеграция Arch-Compass с Cloud-Reason

Arch-Compass использует Cloud-Reason для анализа архитектурных решений через PowerShell модуль.

```powershell
# Пример использования
$analysis = Invoke-CloudReasonAnalysis -Config "architecture.yaml" -ReasoningAPI "https://cloud-reason.api.yandexcloud.net"
```

## Планируемые улучшения

1. **Расширение Cloud-Reason**:
   - Добавление эндпоинтов `/health`, `/chat`, `/api/v1/reason`, `/api/v1/status`
   - Интеграция с YandexGPT API
   - Загрузка файлов в Object Storage

2. **Расширение Arch-Compass**:
   - Модуль генерации архитектурных диаграмм
   - Интеграция с reasoning API для валидации
   - Поддержка MCP (Model Context Protocol)

3. **Унификация документации**:
   - Единый портал документации с MkDocs
   - Интерактивные диаграммы архитектуры
   - Примеры использования для enterprise

## Следующие шаги

- [ ] Реализовать недостающие эндпоинты в Cloud-Reason
- [ ] Создать PowerShell модуль для интеграции
- [ ] Настроить автоматическое развертывание через SourceCraft
- [ ] Обновить README проектов с новыми возможностями
