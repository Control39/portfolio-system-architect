"""
Pydantic модели для сущностей и связей в графе знаний.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EntityType(str, Enum):
    """Типы сущностей в графе знаний."""
    TECHNOLOGY = "technology"
    PROJECT = "project"
    PERSON = "person"
    SKILL = "skill"
    ORGANIZATION = "organization"
    DOCUMENT = "document"
    CONCEPT = "concept"
    TOOL = "tool"
    FRAMEWORK = "framework"
    LANGUAGE = "programming_language"
    DATABASE = "database"
    SERVICE = "service"
    API = "api"
    PATTERN = "pattern"
    OTHER = "other"


class RelationshipType(str, Enum):
    """Типы связей между сущностями."""
    USES = "uses"
    IMPLEMENTS = "implements"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    CREATED_BY = "created_by"
    USED_BY = "used_by"
    SIMILAR_TO = "similar_to"
    VERSION_OF = "version_of"
    EXTENDS = "extends"
    INTEGRATES_WITH = "integrates_with"
    MENTIONS = "mentions"
    REFERENCES = "references"
    FOLLOWS = "follows"
    IMPROVES = "improves"


class Entity(BaseModel):
    """Модель сущности в графе знаний."""
    id: str = Field(..., description="Уникальный идентификатор сущности")
    name: str = Field(..., description="Название сущности")
    type: EntityType = Field(..., description="Тип сущности")
    description: Optional[str] = Field(None, description="Описание сущности")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Уверенность в существовании сущности")
    source: Optional[str] = Field(None, description="Источник информации о сущности")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания")
    updated_at: datetime = Field(default_factory=datetime.now, description="Время последнего обновления")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "fastapi-001",
                "name": "FastAPI",
                "type": "framework",
                "description": "Современный веб-фреймворк для создания API с Python",
                "metadata": {"category": "web", "language": "Python"},
                "confidence": 0.95,
                "source": "api/main.py"
            }
        }


class Relationship(BaseModel):
    """Модель связи между сущностями."""
    id: str = Field(..., description="Уникальный идентификатор связи")
    source_id: str = Field(..., description="ID исходной сущности")
    target_id: str = Field(..., description="ID целевой сущности")
    type: RelationshipType = Field(..., description="Тип связи")
    description: Optional[str] = Field(None, description="Описание связи")
    weight: float = Field(1.0, ge=0.0, le=10.0, description="Вес/сила связи")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Уверенность в существовании связи")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rel-001",
                "source_id": "architect-assistant-001",
                "target_id": "fastapi-001",
                "type": "uses",
                "description": "Architect Assistant использует FastAPI для API сервера",
                "weight": 8.5,
                "confidence": 0.9
            }
        }


class GraphQuery(BaseModel):
    """Модель запроса к графу знаний."""
    query_type: str = Field(..., description="Тип запроса: find_entities, find_relationships, path, neighbors, etc.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Параметры запроса")
    limit: Optional[int] = Field(100, description="Максимальное количество результатов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_type": "find_entities",
                "parameters": {"type": "technology", "name_contains": "fast"},
                "limit": 10
            }
        }


class GraphResponse(BaseModel):
    """Модель ответа от графа знаний."""
    success: bool = Field(..., description="Успешность выполнения запроса")
    data: Optional[Dict[str, Any]] = Field(None, description="Данные результата")
    entities: Optional[List[Entity]] = Field(None, description="Список сущностей")
    relationships: Optional[List[Relationship]] = Field(None, description="Список связей")
    message: Optional[str] = Field(None, description="Сообщение об ошибке или информации")
    processing_time_ms: float = Field(..., description="Время обработки запроса в миллисекундах")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "entities": [
                    {
                        "id": "fastapi-001",
                        "name": "FastAPI",
                        "type": "framework",
                        "description": "Современный веб-фреймворк",
                        "confidence": 0.95
                    }
                ],
                "processing_time_ms": 45.2
            }
        }


class TextExtractionRequest(BaseModel):
    """Модель запроса для извлечения сущностей из текста."""
    text: str = Field(..., description="Текст для анализа")
    extract_relationships: bool = Field(True, description="Извлекать ли связи между сущностями")
    language: str = Field("ru", description="Язык текста")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Architect Assistant использует FastAPI и ChromaDB для RAG поиска.",
                "extract_relationships": True,
                "language": "ru"
            }
        }


class TextExtractionResponse(BaseModel):
    """Модель ответа с извлеченными сущностями и связями."""
    entities: List[Entity] = Field(..., description="Извлеченные сущности")
    relationships: List[Relationship] = Field(default_factory=list, description="Извлеченные связи")
    processing_time_ms: float = Field(..., description="Время обработки в миллисекундах")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entities": [
                    {
                        "id": "entity-1",
                        "name": "Architect Assistant",
                        "type": "project",
                        "confidence": 0.9
                    },
                    {
                        "id": "entity-2", 
                        "name": "FastAPI",
                        "type": "framework",
                        "confidence": 0.95
                    }
                ],
                "relationships": [
                    {
                        "id": "rel-1",
                        "source_id": "entity-1",
                        "target_id": "entity-2",
                        "type": "uses",
                        "confidence": 0.85
                    }
                ],
                "processing_time_ms": 120.5
            }
        }