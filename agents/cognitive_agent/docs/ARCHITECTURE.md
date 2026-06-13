# Архитектура Cognitive Agent

## 🏗️ Компонентная схема

```mermaid
graph TB
    subgraph "Cognitive Agent"
        A[Scanner<br/>🔍 Project Scanner] --> B[Planner<br/>📋 Task Planner]
        B --> C[Skills<br/>⚡ 16+ навыков]
        C --> D[Learning System<br/>📚 Метрики и обучение]
        D --> E[Reports & Logs<br/>📂 Отчёты]
    end

    subgraph "External Services"
        F[Knowledge Graph<br/>🕸️ Восстанавливается]
        G[Decision Engine<br/>🎯 Рекомендации]
        H[AI Config Manager<br/>⚙️ Конфигурация]
        I[Auth Service<br/>🔐 JWT]
    end

    subgraph "Monitoring"
        J[Trigger Processor<br/>🔔 Обработчик]
        K[Alert System<br/>⚠️ Оповещения]
        L[Quota Monitor<br/>📊 Мониторинг квот]
    end

    A -.->|Конфиг| H
    B -.->|Контекст| F
    C -.->|Рекомендации| G
    D -->|Метрики| L
    J -->|События| K
    I -.->|Авторизация| A
```

## 📊 Поток данных

```mermaid
sequenceDiagram
    participant U as User
    participant S as Scanner
    participant P as Planner
    participant Sk as Skills
    participant L as Learning
    participant R as Reports

    U->>S: Цель/Триггер
    S->>S: Сканирование проекта
    S->>P: Результаты сканирования
    P->>P: Приоритизация задач
    P->>Sk: План задач
    Sk->>Sk: Выполнение навыков
    Sk->>L: Метрики выполнения
    L->>L: Анализ и обучение
    L->>R: Генерация отчётов
    R->>U: Результат
```

## 🔄 Цикл работы

```mermaid
flowchart TD
    Start([Запуск агента]) --> Scan[🔍 Сканирование]
    Scan --> Plan[📋 Планирование]
    Plan --> Execute[⚡ Выполнение задач]
    Execute --> Collect[📊 Сбор метрик]
    Collect --> Analyze[📈 Анализ эффективности]
    Analyze --> Improve[🎯 Генерация улучшений]
    Improve --> Report[📝 Отчёт]
    Report --> Decision{Автоприменение?}
    Decision -->|Да| Apply[✅ Применение]
    Decision -->|Нет| Wait[⏳ Ожидание]
    Apply --> Loop{Продолжить?}
    Wait --> Loop
    Loop -->|Да| Scan
    Loop -->|Нет| End([Завершение])
```

## 📁 Структура файлов

```
agents/cognitive_agent/
├── scripts/
│   ├── scanner_main.py          # 🔍 Сканирование проекта
│   ├── planner_main.py          # 📋 Планировщик задач
│   ├── learning_main.py         # 📚 Система обучения
│   ├── trigger-processor.py     # 🔔 Обработчик триггеров
│   ├── alert-system.py          # ⚠️ Система оповещений
│   ├── quota-monitor.py         # 📊 Мониторинг квот
│   ├── scheduled-monitor.py     # ⏰ Плановый мониторинг
│   └── ... (ещё 10+ скриптов)
│
├── config/
│   ├── scanner.yaml             # Конфиг сканера
│   ├── planner.yaml             # Конфиг планировщика
│   ├── learning.yaml            # Конфиг обучения
│   └── alerts.yaml              # Конфиг оповещений
│
├── data/
│   └── learning/
│       ├── metrics/             # Метрики задач
│       ├── models/              # ML-модели
│       └── reports/             # Отчёты
│
└── logs/                        # Логи (создаётся кодом)
    ├── scanner.log
    ├── planner.log
    └── alerts.log
```

## 🔌 Интеграции

| Компонент             | Тип        | Статус              | Протокол   |
| --------------------- | ---------- | ------------------- | ---------- |
| **Knowledge Graph**   | Внутренний | 🟡 Восстанавливается | API        |
| **Decision Engine**   | Внутренний | 🟡 Stub              | API        |
| **AI Config Manager** | Внутренний | ✅ Работает          | Filesystem |
| **Auth Service**      | Внешний    | ✅ Работает          | JWT        |
| **GigaChat/Ollama**   | Внешний    | ⚪ В планах          | API        |

## 🎯 Статус реализации

| Компонент          | Реализовано | Описание                           |
| ------------------ | ----------- | ---------------------------------- |
| **Scanner**        | ✅ 100%      | Сканирование проекта, анализ стека |
| **Planner**        | ✅ 70%       | Планирование без ИИ (заглушка)     |
| **Learning**       | ✅ 100%      | Сбор метрик, анализ, отчёты        |
| **Skills**         | ✅ 100%      | 16+ навыков автоматизации          |
| **Monitoring**     | ✅ 100%      | 3 монитора + оповещения            |
| **AI Integration** | ❌ 0%        | LangChain/GigaChat не подключены   |
| **API Server**     | ❌ 0%        | FastAPI не реализован              |

---

**Автор:** Екатерина Куделя
**Дата:** 13 июня 2026
**Версия:** 0.1.0 (MVP + Восстановление)
