"""
Models for Decision Engine and Cognitive Agent.
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


class ScanRequest(BaseModel):
    """Запрос на сканирование проекта"""

    project_path: str = Field(..., description="Путь к проекту для сканирования")
    mode: str = Field(default="full", description="Режим сканирования: full, git_diff, paths")
    paths: list[str] | None = Field(default=None, description="Пути для выборочного сканирования")


class ScanResponse(BaseModel):
    """Ответ сканирования проекта"""

    status: str = Field(..., description="Статус операции: pending, success, error")
    files_found: int = Field(..., description="Количество найденных файлов")
    languages_detected: list[str] = Field(..., description="Обнаруженные языки программирования")
    message: str | None = Field(default=None, description="Сообщение о результатах")
    scan_time: float | None = Field(default=None, description="Время сканирования в секундах")


class PlanRequest(BaseModel):
    """Запрос на планирование задач"""

    goals: str = Field(..., description="Цели для планирования")
    project_path: str = Field(default=".", description="Путь к проекту")
    constraints: dict[str, Any] | None = Field(default=None, description="Ограничения для планирования")


class PlanResponse(BaseModel):
    """Ответ планирования задач"""

    tasks: list[dict[str, Any]] = Field(..., description="Список задач")
    estimated_duration: int = Field(..., description="Оценочная длительность в минутах")
    message: str | None = Field(default=None, description="Сообщение о результатах")
    priority_score: float | None = Field(default=None, description="Общая оценка приоритета")
