# Diagrams Interactive Data Flow Diagram

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\diagrams_interactive_data-flow-diagram.md`
- **Тип**: .MD
- **Размер**: 986 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
# Data Flow Diagram

- **Путь**: `diagrams\interactive\data-flow-diagram.md`
- **Тип**: .MD
- **Размер**: 1,463 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
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
    J --> K[(БД визуализаций
... (файл продолжается)
```
