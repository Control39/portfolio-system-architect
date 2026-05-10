"""
Модуль health check для мониторинга состояния сервиса.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, str]:
    """
    Базовый health check endpoint.

    Returns:
        Dict с информацией о состоянии сервиса
    """
    return {
        "status": "healthy",
        "service": "template-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Readiness check с проверкой зависимостей.

    Проверяет доступность базы данных и других критичных зависимостей.

    Args:
        db: Сессия базы данных

    Returns:
        Dict с информацией о готовности сервиса
    """
    try:
        # Проверка подключения к базе данных
        await db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e!s}"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Liveness check для Kubernetes.

    Проверяет, что процесс сервиса работает.

    Returns:
        Dict с информацией о жизнеспособности сервиса
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
