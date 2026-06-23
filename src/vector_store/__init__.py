# src/vector_store/__init__.py

from abc import ABC, abstractmethod
from typing import Any, Union

try:
    from src.vector_store.chroma_impl import ChromaVectorStore
except ImportError:
    ChromaVectorStore = None

try:
    from src.vector_store.config import VectorStoreConfig, VectorStoreType
except ImportError:
    VectorStoreConfig = VectorStoreType = None

try:
    from src.vector_store.embedder import DocumentEmbedder
except ImportError:
    DocumentEmbedder = None

try:
    from src.vector_store.ollama_embedder import OllamaEmbedder
except ImportError:
    OllamaEmbedder = None

try:
    from src.vector_store.document_utils import DocumentChunker, DocumentLoader
except ImportError:
    DocumentChunker = DocumentLoader = None


class VectorStoreInterface(ABC):
    # ... (как раньше) ...
    pass


def get_vector_store(store_type: str = "chroma", config=None):
    if config is None:
        from src.vector_store.config import VectorStoreConfig

        config = VectorStoreConfig()

    if store_type == "chroma":
        if ChromaVectorStore is None:
            raise RuntimeError("ChromaDB not installed. Install with: pip install chromadb")
        return ChromaVectorStore(
            persist_directory=config.persist_directory,
            collection_name=config.collection_name,
        )
    elif store_type == "openai":
        raise NotImplementedError("OpenAI Vector Stores not yet implemented")
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")


__all__ = [
    "VectorStoreInterface",
    "get_vector_store",
    "ChromaVectorStore",
    "DocumentEmbedder",
    "OllamaEmbedder",
    "DocumentChunker",
    "DocumentLoader",
    "VectorStoreConfig",
    "VectorStoreType",
]
