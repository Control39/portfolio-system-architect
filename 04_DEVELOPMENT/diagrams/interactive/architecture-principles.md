graph TD
    A[Архитектурные принципы] --> B(Модульность)
    A --> C(Масштабируемость)
    A --> D(Надежность)
    A --> E(Безопасность)
    A --> F(Поддерживаемость)

    B --> B1[Микросервисы]
    B --> B2[API Gateway]
    B --> B3[Контейнеризация]

    C --> C1[Горизонтальное масштабирование]
    C --> C2[Балансировка нагрузки]
    C --> C3[Кэширование]

    D --> D1[Резервирование]
    D --> D2[Мониторинг]
    D --> D3[Логирование]

    E --> E1[Аутентификация]
    E --> E2[Авторизация]
    E --> E3[Шифрование]

    F --> F1[Документация]
    F --> F2[Тестирование]
    F --> F3[CI/CD]

    style A fill:#FF5722,stroke:#BF360C
    style B fill:#4CAF50,stroke:#388E3C
    style C fill:#2196F3,stroke:#0D47A1
    style D fill:#9C27B0,stroke:#4A148C
    style E fill:#FF9800,stroke:#E65100
    style F fill:#795548,stroke:#3E2723

    style B1 fill:#C8E6C9,stroke:#388E3C
    style B2 fill:#C8E6C9,stroke:#388E3C
    style B3 fill:#C8E6C9,stroke:#388E3C

    style C1 fill:#BBDEFB,stroke:#0D47A1
    style C2 fill:#BBDEFB,stroke:#0D47A1
    style C3 fill:#BBDEFB,stroke:#0D47A1

    style D1 fill:#E1BEE7,stroke:#4A148C
    style D2 fill:#E1BEE7,stroke:#4A148C
    style D3 fill:#E1BEE7,stroke:#4A148C

    style E1 fill:#FFE0B2,stroke:#E65100
    style E2 fill:#FFE0B2,stroke:#E65100
    style E3 fill:#FFE0B2,stroke:#E65100

    style F1 fill:#D7CCC8,stroke:#3E2723
    style F2 fill:#D7CCC8,stroke:#3E2723
    style F3 fill:#D7CCC8,stroke:#3E2723
