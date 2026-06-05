import os
import sys
import logging

import uvicorn

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- OpenTelemetry Tracing ---
try:
    from config.otel import OTEL_ENABLED
except ImportError:
    OTEL_ENABLED = False

from api.endpoints import app
from configs.loader import COMPONENT_CONFIG

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
    # Берём команду запуска из конфигурации
    api_script = next(
        script
        for script in COMPONENT_CONFIG.get("automation", {}).get("scripts", [])
        if script.get("name") == "run_api"
    )

    print(f"Запуск API: {api_script['command']}")

    # Извлекаем порт из команды (если указан)
    port = 8008  # порт cognitive agent
    if "--port" in api_script.get("command", ""):
        port_str = api_script["command"].split("--port")[1].strip().split()[0]
        port = int(port_str)

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run_server()
