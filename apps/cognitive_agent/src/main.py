import os
import sys
import logging

import uvicorn

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- OpenTelemetry Tracing ---
try:
    from src.core.otel import OTEL_ENABLED
except ImportError:
    OTEL_ENABLED = False

from apps.cognitive_agent.src.api.endpoints import app

logger = logging.getLogger(__name__)

# Если трейсинг включён — инструментируем
if OTEL_ENABLED:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ OpenTelemetry FastAPI Instrumentation активировано")
    except Exception as e:
        logger.warning(f"⚠️ OpenTelemetry не настроен: {e}")


def run_server():
    port = 8008  # порт cognitive agent
    print(f"Запуск Cognitive Agent API на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run_server()
