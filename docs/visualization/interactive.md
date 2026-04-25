# Интерактивная визуализация reasoning-графа

Этот документ содержит интерактивную визуализацию reasoning-графа с использованием Mermaid.js.

## Reasoning-граф

```mermaid
graph TD
    A[Источник] --> B[Задача]
    B --> C[Инструмент]
    C --> D[Направление]
    D --> E[Подтверждение]
    E --> F[Результат]
```

## Фильтрация по направлениям

```mermaid
graph TD
    classDef analytics fill:#4285F4,stroke:#333;
    classDef devops fill:#FBBC05,stroke:#333;
    classDef mlops fill:#34A853,stroke:#333;
    classDef documentation fill:#A142F4,stroke:#333;
    classDef ai fill:#EA4335,stroke:#333;
    classDef systems fill:#F4B400,stroke:#333;
    
    A[Источник] --> B[Задача]
    B --> C[Инструмент]
    C --> D[Направление]
    D --> E[Подтверждение]
    E --> F[Результат]
    
    class A,B,C,D,E,F analytics;
```

## Фильтрация по уровням сложности

```mermaid
graph TD
    classDef high fill:#ff6b6b,stroke:#333;
    classDef medium fill:#4ecdc4,stroke:#333;
    classDef low fill:#45b7d1,stroke:#333;
    
    A[Источник] --> B[Задача]
    B --> C[Инструмент]
    C --> D[Направление]
    D --> E[Подтверждение]
    E --> F[Результат]
    
    class A,B,C,D,E,F high;
```