"""
Модуль интеграции между ML Model Registry и Portfolio Organizer.

Обеспечивает двусторонний обмен данными между сервисами.
Поддерживает экспорт моделей, получение информации и синхронизацию статусов.
"""

import logging
import os
import re
import sys
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


# Валидация model_id для предотвращения SSRF (CodeQL #51)
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# Валидация endpoint для предотвращения partial SSRF
ENDPOINT_PATH_PATTERN = re.compile(r"^/[A-Za-z0-9/_-]{1,512}$")


def validate_model_id(model_id: str) -> str:
    """Проверка model_id: только безопасные символы для URL."""
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise HTTPException(status_code=400, detail="Неверный формат model_id")
    return model_id


# Импортируем async helpers (требуется после sys.path.insert)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.common.async_helpers import fetch_parallel  # noqa: E402


# Настройка логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/portfolio", tags=["portfolio-integration"])

# Конфигурация из переменных окружения
ML_MODEL_REGISTRY_URL = os.environ.get("ML_MODEL_REGISTRY_URL", "http://ml-model-registry:8000")

PORTFOLIO_ORGANIZER_URL = os.environ.get("PORTFOLIO_ORGANIZER_URL", "http://portfolio-organizer:8001")

API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))
ASYNC_TIMEOUT = httpx.Timeout(API_TIMEOUT)


# Pydantic модели для валидации
class ExportRequest(BaseModel):
    format: str = "json"
    include_metrics: bool = True
    include_artifacts: bool = False


class ModelPortfolioInfo(BaseModel):
    model_id: str
    name: str
    version: str
    description: str | None = None
    status: str
    created_at: str | None = None
    metrics: dict[str, Any] = {}
    portfolio_integration: dict[str, Any]


class ExportResponse(BaseModel):
    status: str
    model_id: str
    format: str
    portfolio_id: str | None = None
    message: str | None = None


# Вспомогательные функции
def validate_registry_endpoint(endpoint: str) -> str:
    """Проверка endpoint для запросов к ML Model Registry (защита от partial SSRF)."""
    if not endpoint or not isinstance(endpoint, str):
        raise HTTPException(status_code=400, detail="Invalid endpoint")

    # Блокируем попытки выйти за пределы path-компонента URL или подменить схему/хост.
    if any(token in endpoint for token in ("://", "..", "\\", "?", "#", "@")):
        raise HTTPException(status_code=400, detail="Invalid endpoint")

    if not ENDPOINT_PATH_PATTERN.fullmatch(endpoint):
        raise HTTPException(status_code=400, detail="Invalid endpoint")

    return endpoint


async def fetch_from_registry(endpoint: str, method: str = "GET", data: dict | None = None):
    """Выполнить запрос к ML Model Registry."""
    safe_endpoint = validate_registry_endpoint(endpoint)
    url = f"{ML_MODEL_REGISTRY_URL}{safe_endpoint}"

    async with httpx.AsyncClient(timeout=ASYNC_TIMEOUT) as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения к реестру моделей: {e}")
            raise HTTPException(status_code=503, detail="ML Model Registry is not accessible") from e
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к реестру моделей: {e}")
            raise HTTPException(
                status_code=504,
                detail=f"ML Model Registry did not respond within {API_TIMEOUT}s",
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка от реестра моделей: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Registry error: {e!s}") from e


async def send_to_portfolio(endpoint: str, data: dict):
    """Отправить данные в Portfolio Organizer."""
    url = f"{PORTFOLIO_ORGANIZER_URL}{endpoint}"

    async with httpx.AsyncClient(timeout=ASYNC_TIMEOUT) as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()

        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения к Portfolio Organizer: {e}")
            raise HTTPException(status_code=503, detail="Portfolio Organizer is not accessible") from e
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к Portfolio Organizer: {e}")
            raise HTTPException(
                status_code=504,
                detail=f"Portfolio Organizer did not respond within {API_TIMEOUT}s",
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка от Portfolio Organizer: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Portfolio error: {e!s}") from e


# Мок-данные для разработки (когда реестр недоступен)
MOCK_MODELS = [
    {
        "id": "model_001",
        "name": "ResNet50",
        "version": "1.0.0",
        "status": "production",
        "description": "Computer vision model",
    },
    {
        "id": "model_002",
        "name": "BERT-base",
        "version": "2.1.0",
        "status": "staging",
        "description": "NLP model",
    },
    {
        "id": "model_003",
        "name": "XGBoost",
        "version": "0.9.5",
        "status": "development",
        "description": "Gradient boosting",
    },
]




@router.get("/models", response_model=list[dict[str, Any]])
async def get_models(use_mock: bool = False):
    """
    Возвращает список моделей для отображения в portfolio-organizer.

    Args:
        use_mock: Использовать мок-данные (для разработки)
    """
    logger.info("Запрос списка моделей для portfolio-organizer")

    if use_mock:
        logger.info("Используются мок-данные")
        return MOCK_MODELS

    try:
        # Реальный запрос к ML Model Registry
        return await fetch_from_registry("/api/models")
    except HTTPException:
        # Если реестр недоступен, возвращаем мок-данные c предупреждением
        logger.warning("Реестр моделей недоступен, используются мок-данные")
        return [{"...mock": True, **model} for model in MOCK_MODELS]




@router.get("/models/{model_id}", response_model=ModelPortfolioInfo)
async def get_model_portfolio_info(model_id: str):
    """
    Получить информацию o модели для портфолио.

    Args:
        model_id: Идентификатор модели
    """
    # Валидация model_id для предотвращения SSRF
    validate_model_id(model_id)
    logger.info(f"Запрос информации o модели {model_id} для портфолио")

    # Проверяем мок-данные (для разработки)
    for model in MOCK_MODELS:
        if model["id"] == model_id:
            return {
                **model,
                "portfolio_integration": {
                    "can_export": True,
                    "supported_formats": ["json", "yaml", "markdown"],
                    "api_endpoint": f"{ML_MODEL_REGISTRY_URL}/api/models/{model_id}/export",
                },
            }

    # Реальный запрос к реестру
    model_data = await fetch_from_registry(f"/api/models/{model_id}")

    # Форматирование данных для портфолио
    return {
        "model_id": model_data.get("id"),
        "name": model_data.get("name"),
        "version": model_data.get("version"),
        "description": model_data.get("description"),
        "status": model_data.get("status"),
        "created_at": model_data.get("created_at"),
        "metrics": model_data.get("metrics", {}),
        "portfolio_integration": {
            "can_export": True,
            "supported_formats": ["json", "yaml", "markdown"],
            "api_endpoint": f"{ML_MODEL_REGISTRY_URL}/api/models/{model_id}/export",
        },
    }





@router.post("/models/{model_id}/export", response_model=ExportResponse)
async def export_model_to_portfolio(model_id: str, request: ExportRequest):
    """
    Экспортировать модель в портфолио.

    Args:
        model_id: Идентификатор модели
        request: Параметры экспорта
    """
    # Валидация model_id для предотвращения SSRF
    validate_model_id(model_id)
    logger.info(f"Экспорт модели {model_id} в формате {request.format}")

    # Получаем данные модели и экспортируем в нужном формате ПАРАЛЛЕЛЬНО
    # (вместо последовательного выполнения, экономим ~15 сек на большых моделях)
    model_data, export_data = await fetch_parallel(
        fetch_from_registry(f"/api/models/{model_id}"),
        fetch_from_registry(
            f"/api/models/{model_id}/export",
            method="POST",
            data={"format": request.format},
        ),
    )

    # Отправляем в Portfolio Organizer
    portfolio_response = await send_to_portfolio(
        "/api/portfolio/import/model",
        data={
            "model_id": model_id,
            "format": request.format,
            "data": export_data,
            "metadata": {
                "name": model_data.get("name"),
                "version": model_data.get("version"),
                "include_metrics": request.include_metrics,
                "include_artifacts": request.include_artifacts,
            },
            "source": "ml-model-registry",
        },
    )

    return ExportResponse(
        status="success",
        model_id=model_id,
        format=request.format,
        portfolio_id=portfolio_response.get("portfolio_id"),
        message=f"Модель {model_id} успешно экспортирована в портфолио",
    )




@router.post("/models/{model_id}/register")
async def register_model_for_portfolio(model_id: str):
    """
    Регистрирует модель в portfolio-organizer.

    Args:
        model_id: Идентификатор модели
    """
    # Валидация model_id для предотвращения SSRF
    validate_model_id(model_id)
    logger.info(f"Регистрация модели {model_id} в portfolio-organizer")

    # Проверяем существование модели
    try:
        model_data = await fetch_from_registry(f"/api/models/{model_id}")
    except HTTPException:
        # Проверяем мок-данные
        for model in MOCK_MODELS:
            if model["id"] == model_id:
                return {
                    "message": f"Модель {model_id} зарегистрирована в portfolio-organizer (mock)",
                    "success": True,
                    "model": model,
                }
        raise HTTPException(status_code=404, detail="Модель не найдена")  # noqa: B904

    # Регистрируем в портфолио
    portfolio_response = await send_to_portfolio(
        "/api/portfolio/register",
        data={
            "model_id": model_id,
            "name": model_data.get("name"),
            "version": model_data.get("version"),
            "source": "ml-model-registry",
        },
    )

    return {
        "message": f"Модель {model_id} зарегистрирована в portfolio-organizer",
        "success": True,
        "portfolio_id": portfolio_response.get("portfolio_id"),
    }




@router.get("/health")
async def health_check():
    """
    Проверка здоровья интеграционного модуля.
    """
    # Проверяем доступность связанных сервисов
    services_status = {}

    # Проверка ML Model Registry
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ML_MODEL_REGISTRY_URL}/health")
            services_status["ml_model_registry"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.warning(f"ML Model Registry health check failed: {e}")
        services_status["ml_model_registry"] = "unreachable"

    # Проверка Portfolio Organizer
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PORTFOLIO_ORGANIZER_URL}/health")
            services_status["portfolio_organizer"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.warning(f"Portfolio Organizer health check failed: {e}")
        services_status["portfolio_organizer"] = "unreachable"

    return {
        "status": "healthy",
        "service": "ml-model-registry-portfolio-integration",
        "config": {
            "ml_registry_url": ML_MODEL_REGISTRY_URL,
            "portfolio_url": PORTFOLIO_ORGANIZER_URL,
            "api_timeout": API_TIMEOUT,
        },
        "services": services_status,
    }


@router.get("/sync/status")
async def get_sync_status():
    """
    Получить статус синхронизации между сервисами.
    """
    try:
        # Получаем модели из реестра
        registry_models = await fetch_from_registry("/api/models")

        # Получаем модели из портфолио
        portfolio_models = await send_to_portfolio("/api/portfolio/models", data={})

        # Сравниваем и находим расхождения
        registry_ids = {m["id"] for m in registry_models}
        portfolio_ids = {m["model_id"] for m in portfolio_models}

        not_in_portfolio = list(registry_ids - portfolio_ids)
        not_in_registry = list(portfolio_ids - registry_ids)

        return {
            "total_registry_models": len(registry_models),
            "total_portfolio_models": len(portfolio_models),
            "synced_models": len(registry_ids & portfolio_ids),
            "not_in_portfolio": not_in_portfolio,
            "not_in_registry": not_in_registry,
        }

    except Exception as e:
        logger.error(f"Ошибка при проверке синхронизации: {e}")
        return {"status": "error", "detail": str(e)}
