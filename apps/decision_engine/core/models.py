"""
Models for Decision Engine.
"""

from typing import Any

from pydantic import BaseModel, Field


class DecisionContext(BaseModel):
    """Контекст для принятия решения"""

    environment: str = Field(..., description="Окружение (staging/production)")
    user_role: str = Field(..., description="Роль пользователя")
    resources_available: bool = Field(..., description="Доступность ресурсов")
    maintenance_mode: bool | None = False
    backup_verified: bool | None = False
    custom_data: dict[str, Any] | None = None


class DecisionRequest(BaseModel):
    """Запрос на принятие решения"""

    user_id: str = Field(..., description="ID пользователя")
    action: str = Field(..., description="Действие")
    context: DecisionContext = Field(..., description="Контекст")
    include_explanation: bool | None = False


class DecisionResponse(BaseModel):
    """Ответ движка решений"""

    user_id: str
    action: str
    decision: str  # allow/deny/require_approval
    confidence: float | None = None
    reason: str | None = None
    explanation: dict[str, Any] | None = None
    conditions_checked: int | None = 0
