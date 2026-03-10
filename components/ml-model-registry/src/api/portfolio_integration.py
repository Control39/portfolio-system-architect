"""
Модуль интеграции с portfolio-organizer.

Предоставляет эндпоинты для обмена данными между ml-model-registry и portfolio-organizer.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/portfolio", tags=["portfolio-integration"])
logger = logging.getLogger(__name__)

# Пример данных моделей (в реальности будет подключение к базе данных)
mock_models = [
    {"id": "model_001", "name": "ResNet50", "version": "1.0.0", "status": "production"},
    {"id": "model_002", "name": "BERT-base", "version": "2.1.0", "status": "staging"},
    {"id": "model_003", "name": "XGBoost", "version": "0.9.5", "status": "development"},
]

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_models():
    """
    Возвращает список моделей для отображения в portfolio-organizer.
    """
    logger.info("Запрос списка моделей для portfolio-organizer")
    return mock_models

@router.get("/models/{model_id}")
async def get_model_by_id(model_id: str):
    """
    Возвращает детали конкретной модели.
    """
    for model in mock_models:
        if model["id"] == model_id:
            return model
    raise HTTPException(status_code=404, detail="Модель не найдена")

@router.post("/models/{model_id}/register")
async def register_model_for_portfolio(model_id: str):
    """
    Регистрирует модель в portfolio-organizer (заглушка).
    """
    logger.info(f"Регистрация модели {model_id} в portfolio-organizer")
    # В реальности здесь будет логика интеграции с portfolio-organizer API
    return {"message": f"Модель {model_id} зарегистрирована в portfolio-organizer", "success": True}

@router.get("/health")
async def health_check():
    """
    Проверка здоровья интеграционного модуля.
    """
    return {"status": "healthy", "service": "ml-model-registry portfolio integration"}