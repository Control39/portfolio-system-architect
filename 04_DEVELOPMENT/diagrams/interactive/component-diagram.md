graph TD
    A[Пользователь] --> B(Веб-интерфейс)
    B --> C{API Gateway}
    C --> D[Сервис авторизации]
    C --> E[Сервис портфолио]
    C --> F[Сервис компетенций]
    C --> G[Сервис визуализации]

    D --> H[(База данных пользователей)]
    E --> I[(База данных портфолио)]
    F --> J[(База данных компетенций)]
    G --> K[(База данных визуализаций)]

    L[Внешние API] --> C
    M[Система аналитики] --> E
    M --> F

    style A fill:#4CAF50,stroke:#388E3C
    style B fill:#2196F3,stroke:#0D47A1
    style C fill:#FF9800,stroke:#E65100
    style D fill:#9C27B0,stroke:#4A148C
    style E fill:#9C27B0,stroke:#4A148C
    style F fill:#9C27B0,stroke:#4A148C
    style G fill:#9C27B0,stroke:#4A148C
    style H fill:#795548,stroke:#3E2723
    style I fill:#795548,stroke:#3E2723
    style J fill:#795548,stroke:#3E2723
    style K fill:#795548,stroke:#3E2723
    style L fill:#607D8B,stroke:#263238
    style M fill:#607D8B,stroke:#263238

    classDef user fill:#4CAF50,stroke:#388E3C;
    classDef frontend fill:#2196F3,stroke:#0D47A1;
    classDef gateway fill:#FF9800,stroke:#E65100;
    classDef service fill:#9C27B0,stroke:#4A148C;
    classDef database fill:#795548,stroke:#3E2723;
    classDef external fill:#607D8B,stroke:#263238;
