"""
Portfolio Organizer Service - FastAPI application
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Добавляем корень проекта в PYTHONPATH для импорта из src/
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.common.health_check import init_health_checks
from src.security.secret_masking import create_fastapi_secret_middleware
from .api.ml_model_registry_integration import router as ml_model_registry_router
from .api.reasoning_api import router as reasoning_router
from apps.portfolio_organizer.api.v1.portfolios import router as portfolios_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portfolio Organizer API",
    description="API для управления портфолио проектов и анализа компетенций",
    version="1.0.0",
)

# CORS middleware (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для маскировки секретов
app.add_middleware(create_fastapi_secret_middleware())
logger.info("Secret masking middleware added")

# Health Checks
health_service = init_health_checks(
    app,
    service_name="portfolio-organizer",
    version="1.0.0",
)
logger.info("Health checks initialized")

# Основной роутер для API v1
api_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Подключаем ресурсные роутеры к основному
api_v1_router.include_router(portfolios_router)


# Root endpoint
@api_v1_router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Organizer API",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
    }


# Подключаем существующие роутеры
app.include_router(reasoning_router)
app.include_router(ml_model_registry_router)
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn

    # Биндинг на 0.0.0.0 для работы в контейнере Docker
    uvicorn.run(app, host="0.0.0.0", port=8004)  # nosec B104
