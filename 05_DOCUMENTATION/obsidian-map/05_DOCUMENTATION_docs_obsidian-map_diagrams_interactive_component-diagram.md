# Diagrams Interactive Component Diagram

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\diagrams_interactive_component-diagram.md`
- **Тип**: .MD
- **Размер**: 996 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
# Component Diagram

- **Путь**: `diagrams\interactive\component-diagram.md`
- **Тип**: .MD
- **Размер**: 1,487 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
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

... (файл продолжается)
```
