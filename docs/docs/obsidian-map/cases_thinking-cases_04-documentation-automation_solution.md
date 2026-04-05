# Solution

- **Путь**: `cases\thinking-cases\04-documentation-automation\solution.md`
- **Тип**: .MD
- **Размер**: 4,729 байт
- **Последнее изменение**: 2026-03-12 06:53:25

## Превью

```
# Решение

## Архитектура решения

Для решения проблемы автоматизации документации была разработана система из двух основных компонентов:

```mermaid
graph TD
    subgraph Вход
        A[Исходный код] --> B[Скрипты Python]
    end
    
    subgraph Генерация
        B --> C[generate_obsidian_map.py]
        B --> D[generate_website.py]
    end
    
    subgraph Выход
        C --> E[docs/obsidian-map/]
        D --> F[docs/website/]
    end
    
    subgraph Деплой
        E --> G[GitHub Pages]

... (файл продолжается)
```

