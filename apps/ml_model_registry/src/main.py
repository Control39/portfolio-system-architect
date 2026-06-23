import os
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.ml_model_registry.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    ml_config = config_manager.get_config()
    print("✅ ML Model Registry: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  ML Model Registry: AI Config Manager недоступен ({e}), используется локальный конфиг")
    ml_config = {}

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# Пробуем импорт с разными путями
try:
    from src.common.health_check import init_health_checks
except ImportError:
    # Fallback для Docker-окружения
    from src.common.health_check import init_health_checks

# Добавляем путь к корню проекта (shared_src) и к текущему каталогу
current_dir = os.path.dirname(os.path.abspath(__file__))

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
