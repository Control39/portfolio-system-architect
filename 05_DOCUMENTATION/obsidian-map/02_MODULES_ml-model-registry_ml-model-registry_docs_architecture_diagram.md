# Architecture Diagram

- **Путь**: `02_MODULES\ml-model-registry\ml-model-registry\docs\architecture_diagram.md`
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
    
    D --> G[Model Versioning]
    G --> H[Git LFS]
    
    E --> I[S3 Storage]
    E --> J[Local Storage]
    
    F --> K[PostgreSQL]
    
    L[ML Training Pipelines] --> M[Model Registration]
    M --> D
    M --> E

... (файл продолжается)
```
