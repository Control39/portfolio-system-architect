import os
import sys

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from . import portfolio_integration

# Импортируем общие модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.common.health_check import init_health_checks

app = FastAPI(
    title="ML Model Registry API",
    version="1.0.0",
    description="Registry for machine learning models with portfolio integration",
)

# Инициализируем health-check
init_health_checks(app, service_name="ml-model-registry", version="1.0.0")

# Instrumentator для метрик
Instrumentator().instrument(app).expose(app)

# Включаем роутеры
app.include_router(portfolio_integration.router)


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "ML Model Registry",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /ready": "Readiness probe",
            "GET /live": "Liveness probe",
            "GET /api/models": "List all models",
            "POST /portfolio/*": "Portfolio integration endpoints",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
