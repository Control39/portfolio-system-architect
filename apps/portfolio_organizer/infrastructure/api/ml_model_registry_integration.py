"""
Интеграция с ML Model Registry для Portfolio Organizer.
Предоставляет эндпоинты для взаимодействия с реестром моделей.
"""

import os
import re
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/ml-model-registry", tags=["ml-model-registry"])

# Конфигурация
ML_MODEL_REGISTRY_URL = os.environ.get("ML_MODEL_REGISTRY_URL", "http://localhost:8000")

ALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "ml-registry.internal",
    "api.trusted-domain.com",
}

# Регулярное выражение для валидации model_id
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class MLModelResponse(BaseModel):
    """Ответ от ML Model Registry"""

    models: list[dict[str, Any]] | None = None
    model: dict[str, Any] | None = None
    prediction: Any = None
    error: str | None = None


class PortfolioAnalysisRequest(BaseModel):
    """Запрос для анализа портфолио"""

    projects: list[dict[str, Any]] = Field(..., description="Список проектов для анализа")


def _is_safe_url(url: str, allowed_hosts: set[str]) -> bool:
    """Проверяет URL на безопасность (защита от SSRF)"""
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        host = parsed.hostname

        if not host:
            return False

        # Разрешённые хосты
        if host in allowed_hosts:
            return True

        # Блокировка localhost и private IP ranges
        if host in ["localhost", "127.0.0.1", "::1"]:
            return False

        # Блокировка private IP диапазонов
        if host.startswith(("10.", "172.16.", "172.31.", "192.168.", "169.254.")):
            return False

        # Блокировка cloud metadata endpoints
        return not any(meta in host.lower() for meta in ["metadata", "instance-data"])
    except Exception:
        return False


async def _make_request(method: str, url: str, **kwargs) -> dict[str, Any]:
    """Выполняет HTTP-запрос с SSRF-защитой"""
    # SSRF защита: валидация URL
    if not _is_safe_url(url, ALLOWED_HOSTS):
        raise HTTPException(status_code=400, detail=f"Небезопасный URL: {url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e)) from e
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Ошибка подключения: {e!s}") from e


@router.get("/models")
async def list_models() -> dict[str, Any]:
    """Получение списка моделей из ML Model Registry"""
    url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models"
    return await _make_request("GET", url)


@router.get("/models/{model_id}")
async def get_model(model_id: str) -> dict[str, Any]:
    """Получение информации о конкретной модели"""
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise HTTPException(status_code=400, detail="Invalid model_id format")

    url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}"
    return await _make_request("GET", url)


@router.post("/models/{model_id}/predict")
async def predict(model_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Выполнение предсказания с использованием модели"""
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise HTTPException(status_code=400, detail="Invalid model_id format")

    url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}/predict"
    return await _make_request("POST", url, json=data)


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Проверка состояния интеграции с ML Model Registry"""
    url = f"{ML_MODEL_REGISTRY_URL}/health"
    try:
        result = await _make_request("GET", url)
        return {
            "status": "healthy",
            "ml_model_registry": "connected",
            "url": ML_MODEL_REGISTRY_URL,
            "details": result,
        }
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "ml_model_registry": "unreachable",
            "url": ML_MODEL_REGISTRY_URL,
            "error": e.detail,
        }


@router.post("/portfolio-analysis")
async def portfolio_analysis(request: PortfolioAnalysisRequest) -> dict[str, Any]:
    """
    Анализ портфолио с использованием моделей машинного обучения.
    Принимает данные проектов, применяет модели для оценки рисков и рекомендаций.
    """
    url = f"{ML_MODEL_REGISTRY_URL}/portfolio/analyze"
    return await _make_request("POST", url, json=request.model_dump())
