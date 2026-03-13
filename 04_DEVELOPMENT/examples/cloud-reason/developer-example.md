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
       def analyze(self, text):
           # Интеграция с API YandexGPT
           pass
   ```
3. Добавить тесты в `components/cloud_reason/tests/test_yandexgpt.py`

### Результат
RAG-система теперь использует YandexGPT для анализа архитектурных решений.

