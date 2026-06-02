from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SkillItem(BaseModel):
    id: str
    level: int  # 0-100
    domain: str

class GapItem(BaseModel):
    skill_id: str
    skill_name: str
    current_level: int
    target_level: int
    priority_score: float  # Вес разрыва (чем выше, тем важнее закрыть)
    estimated_hours: int

class AnalysisResponse(BaseModel):
    status: str = "success"
    user_id: str
    total_gaps: int
    gaps: List[GapItem]
    generated_at: str = Field(default_factory=datetime.now().isoformat)
    trace_id: Optional[str] = None