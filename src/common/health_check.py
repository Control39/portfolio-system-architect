"""Единый модуль для health-check эндпоинтов.

Предоставляет стандартизированные health-check функции для всех сервисов.
Поддерживает различные типы checks: database, external services, etc.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthCheckResponse(BaseModel):
    """Модель ответа health-check."""

    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    version: str | None = None
    checks: dict[str, dict[str, Any]] = {}
    timestamp: str | None = None


class HealthCheckService:
    """Сервис для управления health-check функциями."""

    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.checks: dict[str, Callable] = {}
        self.required_checks: set = set()  # Checks that must pass for "healthy" status

    def register_check(
        self,
        name: str,
        check_fn: Callable,
        required: bool = False,
        timeout: int = 5,
    ):
        """Регистрирует функцию проверки.

        Args:
            name: Имя проверки (например, 'database', 'cache')
            check_fn: Async функция, которая возвращает статус
            required: Если True, сервис будет unhealthy если эта проверка не пройдена
            timeout: Таймаут в секундах

        """
        self.checks[name] = {
            "fn": check_fn,
            "timeout": timeout,
            "required": required,
        }
        if required:
            self.required_checks.add(name)

    async def get_health(self) -> HealthCheckResponse:
        """Получить полный статус здоровья сервиса."""
        from datetime import datetime

        results = {}
        failed_required = []

        for name, check_info in self.checks.items():
            check_fn = check_info["fn"]
            timeout = check_info["timeout"]
            is_required = check_info.get("required", False)

            try:
                # Выполнить проверку с таймаутом
                result = await asyncio.wait_for(check_fn(), timeout=timeout)
                results[name] = result

                if is_required and result.get("status") != "ok":
                    failed_required.append(name)

            except asyncio.TimeoutError:
                results[name] = {"status": "timeout", "error": f"Check did not complete within {timeout}s"}
                if is_required:
                    failed_required.append(name)
                logger.warning(f"Health check '{name}' timed out after {timeout}s")

            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
                if is_required:
                    failed_required.append(name)
                logger.error(f"Health check '{name}' failed: {e}")

        # Определить общий статус
        if failed_required:
            status = "unhealthy"
        elif any(r.get("status") != "ok" for r in results.values() if results):
            status = "degraded"
        else:
            status = "healthy"

        return HealthCheckResponse(
            service=self.service_name,
            status=status,
            version=self.version,
            checks=results,
            timestamp=datetime.utcnow().isoformat(),
        )


def init_health_checks(
    app,
    service_name: str,
    version: str = "1.0.0",
    db=None,
    redis_client=None,
    external_services: dict[str, str] | None = None,
) -> HealthCheckService:
    """Инициализировать health-check endpoints для сервиса.

    Args:
        app: FastAPI приложение
        service_name: Имя сервиса
        version: Версия сервиса
        db: Database connection (имеет метод ping())
        redis_client: Redis client (имеет метод ping())
        external_services: Dict с именами и URLs внешних сервисов

    Returns:
        Инициализированный HealthCheckService

    """
    router = APIRouter()
    service = HealthCheckService(service_name, version)

    # Регистрируем встроенные проверки
    if db is not None:
        async def check_db():
            try:
                # Пытаемся выполнить простую операцию
                if hasattr(db, "ping"):
                    await db.ping()
                else:
                    # Fallback для других типов подключений
                    await db.execute("SELECT 1")
                return {"status": "ok", "component": "database"}
            except Exception as e:
                logger.error(f"Database check failed: {e}")
                return {"status": "error", "component": "database", "error": str(e)}

        service.register_check("database", check_db, required=True, timeout=5)

    if redis_client is not None:
        async def check_redis():
            try:
                await redis_client.ping()
                return {"status": "ok", "component": "redis"}
            except Exception as e:
                logger.error(f"Redis check failed: {e}")
                return {"status": "error", "component": "redis", "error": str(e)}

        service.register_check("redis", check_redis, required=False, timeout=5)

    if external_services:
        import httpx

        for service_key, url in external_services.items():
            async def check_external(url=url, key=service_key):
                try:
                    async with httpx.AsyncClient(timeout=5) as client:
                        response = await client.get(f"{url}/health")
                        if response.status_code == 200:
                            return {"status": "ok", "service": key}
                        return {
                            "status": "error",
                            "service": key,
                            "http_status": response.status_code,
                        }
                except Exception as e:
                    logger.warning(f"External service check for {key} failed: {e}")
                    return {"status": "error", "service": key, "error": str(e)}

            service.register_check(f"external_{service_key}", check_external, required=False, timeout=10)

    # Регистрируем endpoints
    @router.get("/health")
    @router.get("/ready")
    @router.get("/live")
    async def health():
        """Health check endpoint - поддерживает /health, /ready и /live paths."""
        result = await service.get_health()

        # Для /live нас интересует только базовый статус
        # Для /ready нас интересует все (including external services)
        if result.status == "unhealthy":
            raise HTTPException(status_code=503, detail=result.dict())

        return result

    app.include_router(router)
    logger.info(f"Health checks initialized for service '{service_name}'")

    return service


