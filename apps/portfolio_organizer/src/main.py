"""
Portfolio Organizer Service - FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.ml_model_registry_integration import router as ml_model_registry_router
from .api.reasoning_api import router as reasoning_router


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

# Подключаем router с reasoning API
app.include_router(reasoning_router)

# Подключаем router для интеграции с ML Model Registry
app.include_router(ml_model_registry_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Portfolio Organizer",
        "status": "running",
        "version": "1.0.0",
        "integrations": {
            "reasoning_api": "✅ Available",
            "ml_model_registry": "✅ Available",
            "it_compass": "✅ Available",
            "notifications": "✅ Available",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    """Readiness check endpoint"""
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    # Биндинг на 0.0.0.0 для работы в контейнере Docker
    uvicorn.run(app, host="0.0.0.0", port=8004)  # nosec B104
