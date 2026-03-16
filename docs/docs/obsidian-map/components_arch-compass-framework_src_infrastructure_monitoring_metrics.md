# Metrics

- **Путь**: `components\arch-compass-framework\src\infrastructure\monitoring\metrics.py`
- **Тип**: .PY
- **Размер**: 640 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
from prometheus_client import Counter, Histogram, start_http_server
from functools import wraps

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'Request latency')

def track_latency(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        REQUEST_COUNT.labels(method='POST', endpoint=func.__name__).inc()
        with REQUEST_LATENCY.time():
            return func(*args, **kwargs)
   
... (файл продолжается)
```
