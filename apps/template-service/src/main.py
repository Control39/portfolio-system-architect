"""
Основной модуль микросервиса.

Запускает FastAPI приложение с настройками из конфигурации.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from src.api import router as api_router

from src.core.config import settings
from src.core.database import init_db
from src.core.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер жизненного цикла приложения.

    Выполняет инициализацию при запуске и очистку при остановке.
    """
    # Инициализация при запуске
    logger.info("Starting Template Service...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Инициализация базы данных
    await init_db()

    yield

    # Очистка при остановке
    logger.info("Shutting down Template Service...")


def create_app() -> FastAPI:
    """
    Фабрика для создания экземпляра FastAPI приложения.

    Returns:
        FastAPI: Настроенное приложение
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Шаблон микросервиса для проекта portfolio-system-architect",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(api_router, prefix="/api/v1", tags=["api"])

    # Кастомные обработчики ошибок могут быть добавлены здесь

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
