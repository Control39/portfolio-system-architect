"""
Модуль для работы с базой данных.

Обеспечивает подключение к PostgreSQL и управление сессиями.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config import settings

# Базовый класс для моделей
Base = declarative_base()

# Асинхронный движок базы данных
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализация базы данных.

    Создает все таблицы, определенные в моделях.
    """
    async with engine.begin() as conn:
        # В продакшене лучше использовать миграции (Alembic)
        # Здесь создаем таблицы только для разработки
        if settings.environment == "development":
            await conn.run_sync(Base.metadata.create_all)

    print(f"Database initialized: {settings.database_url}")
