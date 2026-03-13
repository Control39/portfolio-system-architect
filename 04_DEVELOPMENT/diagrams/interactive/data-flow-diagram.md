graph LR
    A[Пользователь] --> B(Веб-интерфейс)
    B --> C{API Gateway}
    C --> D[Сервис авторизации]
    D --> E[(БД пользователей)]
    C --> F[Сервис портфолио]
    F --> G[(БД портфолио)]
    C --> H[Сервис компетенций]
    H --> I[(БД компетенций)]
    C --> J[Сервис визуализации]
    J --> K[(БД визуализаций)]

    L[Внешние API] --> C
    M[Система аналитики] --> F
    M --> H

    subgraph "Пользовательский поток"
        A --> B --> C --> D --> E
        C --> F --> G
        C --> H --> I
        C --> J --> K
    end

    subgraph "Аналитический поток"
        F --> M
        H --> M
    end

    subgraph "Внешние интеграции"
        L --> C
    end

    style A fill:#4CAF50,stroke:#388E3C
    style B fill:#2196F3,stroke:#0D47A1
    style C fill:#FF9800,stroke:#E65100
    style D fill:#9C27B0,stroke:#4A148C
    style E fill:#795548,stroke:#3E2723
    style F fill:#9C27B0,stroke:#4A148C
    style G fill:#795548,stroke:#3E2723
    style H fill:#9C27B0,stroke:#4A148C
    style I fill:#795548,stroke:#3E2723
    style J fill:#9C27B0,stroke:#4A148C
    style K fill:#795548,stroke:#3E2723
    style L fill:#607D8B,stroke:#263238
    style M fill:#607D8B,stroke:#263238
