"""
Vector store abstraction for RAG system.

This module provides a unified interface for different vector store implementations:
- ChromaDB (local persistent storage)
- OpenAI Vector Stores (cloud API)
- Future: Ollama + custom embeddings

Usage:
    from src.vector_store import VectorStoreInterface, get_vector_store

    store = get_vector_store("chroma")
    store.add_document("Some text", metadata={"source": "file.md"})
    results = store.search("query", top_k=5)
"""

from abc import ABC, abstractmethod
from typing import Any

from .chroma_impl import ChromaVectorStore
from .config import VectorStoreConfig, VectorStoreType
from .document_utils import DocumentChunker, DocumentLoader
from .embedder import DocumentEmbedder
from .ollama_embedder import OllamaEmbedder


class VectorStoreInterface(ABC):
    """Abstract interface for vector store implementations."""

    @abstractmethod
    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a document to the vector store.

        Args:
            text: Document text content.
            metadata: Optional metadata (source, timestamps, etc.)

        Returns:
            Document ID.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: list[dict[str, Any]]) -> list[str]:
        """
        Add multiple documents to the vector store.

        Args:
            documents: List of dicts with 'text' and optional 'metadata' keys.

        Returns:
            List of document IDs.
        """
        pass

    @abstractmethod
    def search(
        self, query: str, top_k: int = 5, where_filter: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query text.
            top_k: Number of top results to return.
            where_filter: Optional metadata filter.

        Returns:
            List of documents with similarity scores.
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the vector store connection."""
        pass

    @abstractmethod
    def delete_all(self) -> int:
        """
        Delete all documents from the store.

        Returns:
            Number of deleted documents.
        """
        pass


def get_vector_store(
    store_type: VectorStoreType = "chroma", config: VectorStoreConfig | None = None
) -> VectorStoreInterface:
    """
    Factory function to get a vector store instance.

    Args:
        store_type: Type of vector store ("chroma", "openai").
        config: Configuration for the vector store.

    Returns:
        Vector store instance.

    Raises:
        ValueError: If store_type is not supported.
    """
    if config is None:
        config = VectorStoreConfig()

    if store_type == "chroma":
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
    "VectorStoreConfig",
    "VectorStoreType",
    "ChromaVectorStore",
    "DocumentEmbedder",
    "OllamaEmbedder",
    "DocumentChunker",
    "DocumentLoader",
]
