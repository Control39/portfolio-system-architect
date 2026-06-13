"""
OpenTelemetry инициализация для всех сервисов.

Атом наблюдаемости: настраивает traces, metrics, logs для сервиса.
Используется всеми сервисами в apps/ через импорт.

Usage:
    from src.common.telemetry import setup_telemetry, get_tracer

    setup_telemetry("my-service")
    tracer = get_tracer()

    with tracer.start_as_current_span("operation"):
        # ... код ...
"""

import logging
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # type: ignore
from opentelemetry.instrumentation.requests import RequestsInstrumentor  # type: ignore
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)

# Глобальное состояние
_TELEMETRY_INITIALIZED = False


def setup_telemetry(
    service_name: str,
    service_version: str = "0.1.0",
    auto_instrument: bool = True,
) -> bool:
    """
    Инициализация OpenTelemetry для сервиса.

    Args:
        service_name: Имя сервиса (например, "auth_service")
        service_version: Версия сервиса
        auto_instrument: Автоматически инструментировать FastAPI/requests

    Returns:
        True если telemetry включена, False если отключена
    """
    global _TELEMETRY_INITIALIZED

    if _TELEMETRY_INITIALIZED:
        logger.debug(f"Telemetry already initialized for {service_name}")
        return True

    # Проверяем, включён ли трейсинг
    otel_enabled = os.getenv("OTEL_ENABLED", "true").lower() == "true"

    if not otel_enabled:
        logger.info(f"OpenTelemetry отключён для '{service_name}' (OTEL_ENABLED=false)")
        return False

    # ✅_endpoint из переменной окружения (не захардкожен!)
    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otel-collector:4317",  # дефолт для Docker
    )

    # ✅ insecure из переменной окружения
    insecure = os.getenv("OTEL_INSECURE", "true").lower() == "true"

    # ✅ Environment из переменной окружения
    environment = os.getenv("ENVIRONMENT", "development")

    # Создаём Resource с полной информацией о сервисе
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment,
            "service.namespace": "portfolio-system-architect",
        }
    )

    try:
        # === TRACES ===
        trace_provider = TracerProvider(resource=resource)
        trace_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=insecure,
            timeout=10,
        )
        span_processor = BatchSpanProcessor(
            trace_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
        trace_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(trace_provider)

        # === METRICS ===
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=otlp_endpoint,
                insecure=insecure,
                timeout=10,
            ),
            export_interval_millis=30000,  # экспорт каждые 30 секунд
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )
        metrics.set_meter_provider(meter_provider)

        # === AUTO-INSTRUMENTATION ===
        if auto_instrument:
            try:
                FastAPIInstrumentor.instrument()
                logger.debug("FastAPI instrumented")
            except Exception as e:
                logger.debug(f"FastAPI instrumentation skipped: {e}")

            try:
                RequestsInstrumentor.instrument()
                logger.debug("Requests instrumented")
            except Exception as e:
                logger.debug(f"Requests instrumentation skipped: {e}")

            try:
                LoggingInstrumentor.instrument(set_logging_format=True)
                logger.debug("Logging instrumented")
            except Exception as e:
                logger.debug(f"Logging instrumentation skipped: {e}")

        _TELEMETRY_INITIALIZED = True
        logger.info(f"✅ OpenTelemetry включён для '{service_name}' (env={environment}, endpoint={otlp_endpoint})")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации OpenTelemetry: {e}")
        return False


def get_tracer(name: str | None = None) -> trace.Tracer:
    """Получить tracer для создания спанов."""
    return trace.get_tracer(name or __name__)


def get_meter(name: str | None = None) -> metrics.Meter:
    """Получить meter для создания метрик."""
    return metrics.get_meter(name or __name__)
