# Developer Example

- **Путь**: `examples\cloud-reason\developer-example.md`
- **Тип**: .MD
- **Размер**: 973 байт
- **Последнее изменение**: 2026-03-11 18:54:19

## Превью

```
## Cloud Reason (RAG): Пример для разработчика

### Задача
Интегрировать новую модель YandexGPT для анализа архитектурных решений.

### Действие
1. Добавить конфигурацию модели в `components/cloud_reason/configs/models.yaml`:
   ```yaml
   models:
     yandexgpt:
       api_endpoint: "https://llm.api.yandex.net/v1"
       model_name: "yandexgpt-lite"
   ```
2. Создать адаптер в `components/cloud_reason/src/adapters/yandexgpt.py`:
   ```python
   class YandexGPTAdapter:
       def analyze(self, t
... (файл продолжается)
```

