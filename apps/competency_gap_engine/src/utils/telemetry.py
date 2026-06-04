import os
import logging
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource


def setup_logging():
    """Настройка структурного логирования для продакшена"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Создаем форматер для JSON логов
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "timestamp": self.formatTime(record),
            }
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_record)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)


def setup_tracing(service_name: str):
    """Настройка OpenTelemetry для распределенной трассировки"""
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "dev"),
        }
    )

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # В будущем здесь добавим экспорт в Jaeger/Grafana
    # tracer_provider.add_span_processor(...)

    logging.info(f"🔌 Tracing initialized for: {service_name}")
