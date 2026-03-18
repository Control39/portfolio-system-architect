"""
ml-registry - Generated Pydantic Models
Source: src\shared\schemas\ml-registry.yaml
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class ModelMetadata(BaseModel):
    id: str = Field(...) 
    name: str = Field(...) 
    version: str = Field(...) 
    framework: str = Field(None)
    description: str = Field(None)
    accuracy: float = Field(None)
    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)

class ModelSearchResult(BaseModel):
    id: str = Field(None)
    name: str = Field(None)
    version: str = Field(None)
    matches: List[Any] = Field(None)

class ModelOperationResult(BaseModel):
    status: str = Field(None)
    model_id: str = Field(None)
    message: str = Field(None)

