r"""
ml-registry - Generated Pydantic Models
Source: src\shared\schemas\ml-registry.yaml
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    version: str = Field(...)
    framework: str | None = Field(None)
    description: str | None = Field(None)
    accuracy: float | None = Field(None)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)


class ModelSearchResult(BaseModel):
    id: str | None = Field(None)
    name: str | None = Field(None)
    version: str | None = Field(None)
    matches: list[Any] | None = Field(None)


class ModelOperationResult(BaseModel):
    status: str | None = Field(None)
    model_id: str | None = Field(None)
    message: str | None = Field(None)
