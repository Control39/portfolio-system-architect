"""
career - Generated Pydantic Models
Source: src\shared\schemas\career.yaml
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class CompetencyMarker(BaseModel):
    id: str = Field(...) 
    title: str = Field(...) 
    status: str = Field(...) 
    evidence_url: str = Field(None)
    created_at: datetime = Field(None)

class Skill(BaseModel):
    name: str = Field(None)
    level: int = Field(None)
    markers: List[Any] = Field(None)

class UserProfile(BaseModel):
    username: str = Field(...) 
    skills: List[Any] = Field(None)
    goals: List[Any] = Field(None)
    achievements: List[Any] = Field(None)

