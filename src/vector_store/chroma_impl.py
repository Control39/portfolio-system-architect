"""
ChromaDB implementation of vector store.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import chromadb
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None


from .base import VectorStoreInterface
from .embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStoreInterface):
    """ChromaDB implementation of VectorStoreInterface."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "project_docs",
        embedder: DocumentEmbedder | None = None,
    ):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_directory: Directory to store ChromaDB data.
            collection_name: Name of the collection.
            embedder: DocumentEmbedder instance. If None, creates default one.
        """
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is not available. Install with: pip install chromadb>=0.4.22")

        self.embedder = embedder or DocumentEmbedder()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.client = None
        self.collection = None

        self._initialize_chroma()

    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            self.persist_directory.mkdir(parents=True, exist_ok=True)

            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False),
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Cognitive Agent RAG knowledge base"},
                )
                logger.info(f"Created new collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a document to ChromaDB.

        Args:
            text: Document text content.
            metadata: Optional metadata.

        Returns:
            Document ID.
        """
        if not text or not text.strip():
            return ""

        # Generate embedding
        embedding = self.embedder.embed(text)
        if not embedding:
            logger.warning("Failed to generate embedding for document")
            return ""

        # Generate unique ID
        doc_id = str(uuid.uuid4())

        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata.update(
            {
                "timestamp": datetime.now().isoformat(),
                "embedding_model": self.embedder.model_name,
                "text_length": len(text),
            }
        )

        # Add to ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[text.strip()],
        )

        logger.debug(f"Added document {doc_id}: {text[:50]}...")
        return doc_id

    def add_documents(self, documents: list[dict[str, Any]]) -> list[str]:
        """
        Add multiple documents.

        Args:
            documents: List of dicts with 'text' and optional 'metadata'.

        Returns:
            List of document IDs.
        """
        doc_ids = []
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            doc_id = self.add_document(text, metadata)
            if doc_id:
                doc_ids.append(doc_id)

        logger.info(f"Added {len(doc_ids)} documents")
        return doc_ids

    def search(self, query: str, top_k: int = 5, where_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query.
            top_k: Number of results.
            where_filter: Optional metadata filter.

        Returns:
            List of documents with scores.
        """
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []

        # Query ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "documents", "distances"],
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    doc_id = results["ids"][0][i]
                    distance = results["distances"][0][i]
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    text = results["documents"][0][i] if results["documents"] else ""

                    # Convert distance to similarity score
                    similarity_score = 1.0 / (1.0 + distance) if distance > 0 else 1.0

                    formatted_results.append(
                        {
                            "id": doc_id,
                            "text": text,
                            "metadata": metadata,
                            "score": float(similarity_score),
                            "distance": float(distance),
                            "rank": i + 1,
                        }
                    )

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory),
                "embedding_model": self.embedder.model_name,
                "embedding_dimension": self.embedder.model.get_sentence_embedding_dimension(),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    def close(self) -> None:
        """Close ChromaDB client."""
        self.collection = None
        self.client = None
        logger.info("ChromaDB client closed")

    def delete_all(self) -> int:
        """
        Delete all documents by recreating the collection.

        Returns:
            Number of deleted documents.
        """
        try:
            count = self.collection.count()
            self.client.delete_collection(name=self.collection_name)
            self._initialize_chroma()
            logger.info(f"Deleted {count} documents from collection")
            return count
        except Exception as e:
            logger.error(f"Error deleting all documents: {e}")
            return 0
