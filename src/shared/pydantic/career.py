r"""career - Generated Pydantic Models
Source: src\shared\schemas\career.yaml
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CompetencyMarker(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    status: str = Field(...)
    evidence_url: str = Field(None)
    created_at: datetime = Field(None)

class Skill(BaseModel):
    name: str = Field(None)
    level: int = Field(None)
    markers: list[Any] = Field(None)

class UserProfile(BaseModel):
    username: str = Field(...)
    skills: list[Any] = Field(None)
    goals: list[Any] = Field(None)
    achievements: list[Any] = Field(None)



