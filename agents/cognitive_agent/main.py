"""
Cognitive Automation Agent — автономный ИИ-агент для управления проектами.

API:
    GET /health — проверка здоровья
    POST /tasks — создание задачи
    GET /tasks/{id} — получение задачи
"""

import logging

from fastapi import FastAPI

# --- OpenTelemetry Tracing ---
try:
    from src.common.telemetry import OTEL_ENABLED
except ImportError:
    OTEL_ENABLED = False

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cognitive Automation Agent",
    description="Автономный ИИ-агент для управления проектами",
    version="1.0.0",
)

# Если трейсинг включён — инструментируем
if OTEL_ENABLED:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ OpenTelemetry FastAPI Instrumentation активировано")
    except Exception as e:
        logger.warning(f"⚠️ OpenTelemetry не настроен: {e}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cognitive_agent"}


@app.get("/")
async def root():
    return {
        "name": "Cognitive Automation Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "entry": "scripts/scanner_main.py",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
