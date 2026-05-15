r"""
career - Generated Pydantic Models
Source: src\shared\schemas\career.yaml
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CompetencyMarker(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    status: str = Field(...)
    evidence_url: str | None = Field(None)
    created_at: datetime | None = Field(None)


class Skill(BaseModel):
    name: str | None = Field(None)
    level: int | None = Field(None)
    markers: list[Any] | None = Field(None)


class UserProfile(BaseModel):
    username: str = Field(...)
    skills: list[Any] | None = Field(None)
    goals: list[Any] | None = Field(None)
    achievements: list[Any] | None = Field(None)
