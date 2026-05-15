import os
import sys

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


# Пробуем импорт с разными путями
try:
    from src.common.health_check import init_health_checks
except ImportError:
    # Fallback для Docker-окружения
    sys.path.insert(0, "/app")
    sys.path.insert(0, "/app/src")
    from src.common.health_check import init_health_checks

# Добавляем путь к корню проекта (shared_src) и к текущему каталогу
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..", "shared_src")))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))

from .portfolio_integration import router  # noqa: E402


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
app.include_router(router)


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


@app.get("/health")
async def health():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "ml-model-registry"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)  # nosec B104
