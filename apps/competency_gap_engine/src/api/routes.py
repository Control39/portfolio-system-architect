from fastapi import APIRouter, Depends, Request
from opentelemetry import trace

from src.core.gap_calculator import GapCalculator
from src.models.responses import AnalysisResponse

router = APIRouter()


def get_calculator(request: Request):
    """Dependency Injection для калькулятора"""
    config = request.app.state.config
    weights = config.get("gap_analysis", {}).get("domain_weights", {"default": 1.0})
    return GapCalculator(domain_weights=weights)


@router.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_gaps(request: Request, calculator: GapCalculator = Depends(get_calculator)):
    """
    Основной эндпоинт: Принимает навыки пользователя и целевую роль,
    возвращает приоритизированный список разрывов.
    """
    # Трассировка запроса
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id or 0

    # Заглушка данных (в будущем здесь будет HTTP-запрос к it_compass)
    # Сейчас принимаем данные напрямую в теле запроса для простоты MVP
    body = await request.json()

    user_skills = body.get("current_skills", {})
    target_skills = body.get("target_skills", {})
    user_id = body.get("user_id", "unknown")

    # 1. Считаем разрывы
    gaps = calculator.calculate(current_skills=user_skills, target_skills=target_skills)

    # 2. Формируем ответ
    response = AnalysisResponse(
        user_id=user_id,
        total_gaps=len(gaps),
        gaps=gaps,
        trace_id=f"{trace_id:032x}",  # Hex trace_id
    )

    return response
