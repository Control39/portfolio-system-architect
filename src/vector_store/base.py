"""
Abstract base interface for vector stores.
"""

from abc import ABC, abstractmethod
from typing import Any


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
    def search(self, query: str, top_k: int = 5, where_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
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
