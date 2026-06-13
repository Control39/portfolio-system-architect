"""
Portfolio Organizer Service - FastAPI application
Объединённая конфигурация (Clean Architecture)
"""

import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Endpoints layer
from apps.portfolio_organizer.endpoints.routes import app as portfolios_app

# Infrastructure layer (бывший src/)
from apps.portfolio_organizer.infrastructure.api.ml_model_registry_integration import router as ml_model_registry_router
from apps.portfolio_organizer.infrastructure.api.reasoning_api import router as reasoning_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portfolio Organizer API",
    description="API для управления портфолио проектов и анализа компетенций",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health checks
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio-organizer"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Portfolio Organizer API",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
    }


# API v1 router
api_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
api_v1_router.include_router(portfolios_app.router)

# Подключаем все роутеры
app.include_router(reasoning_router)
app.include_router(ml_model_registry_router)
app.include_router(api_v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
