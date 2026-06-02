"""
Portfolio Organizer API Endpoints.
Основной FastAPI приложение с health-check и security middleware.
"""

import logging
from fastapi import FastAPI

from src.common.health_check import init_health_checks
from src.security.secret_masking import create_fastapi_secret_middleware

logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Portfolio Organizer",
    description="API для управления портфолио и координации агентов",
    version="1.0.0",
)

# Добавление middleware для маскировки секретов
app.add_middleware(create_fastapi_secret_middleware())
logger.info("Secret masking middleware added")

# Инициализация health-check endpoints
health_service = init_health_checks(
    app,
    service_name="portfolio-organizer",
    version="1.0.0",
    # db=your_db_connection,  # когда появится
    # redis_client=your_redis,  # когда появится
    # external_services={
    #     "cognitive-agent": "http://localhost:8001",
    # },
)
logger.info("Health checks initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Organizer API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint (дубликат для совместимости)."""
    return {"status": "healthy", "service": "portfolio-organizer"}
