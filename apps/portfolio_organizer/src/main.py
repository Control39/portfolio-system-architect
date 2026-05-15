"""
Portfolio Organizer Service - FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Portfolio Organizer",
        "status": "running",
        "version": "1.0.0",
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

    uvicorn.run(app, host="0.0.0.0", port=8004)
