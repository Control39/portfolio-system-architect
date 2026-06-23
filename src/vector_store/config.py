"""
Configuration for vector stores.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class VectorStoreType(StrEnum):
    """Types of supported vector stores."""

    CHROMA = "chroma"
    OPENAI = "openai"
    OLLAMA = "ollama"


class VectorStoreConfig(BaseModel):
    """Configuration for vector store."""

    store_type: VectorStoreType = Field(default=VectorStoreType.CHROMA, description="Type of vector store")
    persist_directory: str = Field(default="./chroma_db", description="Directory for persistent storage (ChromaDB)")
    collection_name: str = Field(default="cognitive_agent_docs", description="Collection name")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Embedding model name")
    embedding_dimension: int = Field(default=384, description="Embedding dimension")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key (for OpenAI Vector Stores)")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    custom_params: dict[str, Any] = Field(default_factory=dict, description="Additional custom parameters")

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "store_type": "chroma",
                "persist_directory": "./chroma_db",
                "collection_name": "project_docs",
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384,
            }
        }
