# Components Ml Model Registry Docs Architecture Diagram

- **Путь**: `docs\obsidian-map\components_ml-model-registry_docs_architecture_diagram.md`
- **Тип**: .MD
- **Размер**: 909 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Architecture Diagram

- **Путь**: `components\ml-model-registry\docs\architecture_diagram.md`
- **Тип**: .MD
- **Размер**: 2,985 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# Архитектурная диаграмма системы версионирования ML-моделей

## Общая архитектура

```mermaid
graph TD
    A[Клиентские приложения] --> B[API Gateway]
    B --> C[ML Model Registry API]
    
    C --> D[Model Registry]
    C --> E[Model Storage]
    C --> F[Metadata Store]
    
    D --> G[Model Ver
... (файл продолжается)
```

