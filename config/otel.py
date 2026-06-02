import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем имя сервиса из переменной окружения
SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")

# Проверяем, включён ли трейсинг
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() == "true"

if OTEL_ENABLED:
    # Создаём провайдер трейсов с указанием сервиса
    resource = Resource.create({"service.name": SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Настраиваем экспортёр (в OTLP Collector)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://otel-collector:4317",  # gRPC endpoint
        insecure=True  # в dev окружении
    )

    # Добавляем процессор для отправки трейсов
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    logger.info(f"OpenTelemetry включён для сервиса '{SERVICE_NAME}'")
else:
    logger.info("OpenTelemetry отключён (OTEL_ENABLED=false)")