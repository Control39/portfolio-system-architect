from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CompetencyMarker(BaseModel):
    """Объективный маркер компетенции."""
    id: str = Field(..., description="Уникальный UUID")
    title: str = Field(..., description="Краткое название маркера")
    status: str = Field(
        "not_started",
        description="Статус: not_started | in_progress | completed",
    )
    evidence_url: Optional[str] = Field(
        None, description="Ссылка на доказательство (PDF, скриншот и т.п.)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Skill(BaseModel):
    """Навык и набор связанных маркеров."""
    name: str
    level: int = Field(0, ge=0, le=5, description="Уровень от 0 до 5")
    markers: List[CompetencyMarker] = []


class UserProfile(BaseModel):
    """Профиль пользователя."""
    username: str
    skills: List[Skill] = []
    goals: List[dict] = []          # простая структура целей
    achievements: List[dict] = []   # исторические достижения

