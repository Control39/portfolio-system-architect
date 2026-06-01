# -*- coding: utf-8 -*-
"""
Document indexer for building and managing vector search index.
"""

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

from .embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Index documents for vector search with persistence support."""

    def __init__(self, embedder: DocumentEmbedder | None = None) -> None:
        """
        Initialize the indexer.

        Args:
            embedder: DocumentEmbedder instance. If None, creates a default one.
        """
        self.embedder = embedder or DocumentEmbedder()
        self.documents: list[dict[str, Any]] = []
        self.embeddings: list[list[float]] = []
        self.index_path: Path | None = None

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> int:
        """
        Add a document to the index.

        Args:
            text: Document text content.
            metadata: Optional metadata (source file, line numbers, etc.)

        Returns:
            Document ID in the index, or -1 if failed.
        """
        if not text or not text.strip():
            logger.warning("Attempted to add empty document")
            return -1

        doc_id = len(self.documents)
        doc = {
            "id": doc_id,
            "text": text.strip(),
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        # Generate embedding
        embedding = self.embedder.embed(text)
        if not embedding:
            logger.warning("Failed to generate embedding for document %d", doc_id)
            return -1

        self.documents.append(doc)
        self.embeddings.append(embedding)

        logger.debug("Added document %d: %s...", doc_id, text[:50])
        return doc_id

    def add_documents_from_files(
        self, file_pattern: str = "**/*.md", root_dir: str = "."
    ) -> list[int]:
        """
        Add documents from files matching pattern.

        Args:
            file_pattern: Glob pattern for files to index.
            root_dir: Root directory to search from.

        Returns:
            List of document IDs added.
        """
        root = Path(root_dir)
        file_paths = list(root.glob(file_pattern))
        logger.info("Found %d files matching %s", len(file_paths), file_pattern)

        doc_ids: list[int] = []
        for file_path in file_paths:
            try:
                content = file_path.read_text(encoding="utf-8")
                metadata = {
                    "source": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                    "file_type": file_path.suffix,
                }

                # Split large documents into chunks
                chunks = self._chunk_text(content, max_chunk_size=1000)
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk"] = i
                    chunk_metadata["total_chunks"] = len(chunks)

                    doc_id = self.add_document(chunk, chunk_metadata)
                    if doc_id >= 0:
                        doc_ids.append(doc_id)

            except Exception as e:
                logger.error("Error processing file %s: %s", file_path, e)

        logger.info(
            "Added %d document chunks from %d files",
            len(doc_ids),
            len(file_paths),
        )
        return doc_ids

    @staticmethod
    def _chunk_text(text: str, max_chunk_size: int = 1000) -> list[str]:
        """
        Split text into chunks for better search results.

        Args:
            text: Text to chunk.
            max_chunk_size: Maximum chunk size in characters.

        Returns:
            List of text chunks.
        """
        if len(text) <= max_chunk_size:
            return [text]

        chunks: list[str] = []
        # Simple chunking by paragraphs first
        paragraphs = text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        # If still too large, fallback to character-based chunking
        if any(len(chunk) > max_chunk_size * 2 for chunk in chunks):
            chunks = [text[i : i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

        return chunks

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Search for documents similar to query.

        Args:
            query: Search query text.
            top_k: Number of top results to return.

        Returns:
            List of documents with similarity scores.
        """
        if not self.documents:
            logger.debug("Search attempted on empty index")
            return []

        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            logger.warning("Failed to generate embedding for query")
            return []

        # Compute similarities
        similarities: list[tuple[int, float]] = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self.embedder.compute_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Prepare results
        results: list[dict[str, Any]] = []
        for rank, (doc_idx, score) in enumerate(similarities[:top_k], start=1):
            doc = self.documents[doc_idx].copy()
            doc["score"] = float(score)
            doc["rank"] = rank
            results.append(doc)

        return results

    def save(self, path: str) -> None:
        """
        Save index to disk.

        Args:
            path: File path to save the index.
        """
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        index_data = {
            "documents": self.documents,
            "embeddings": self.embeddings,
            "model_name": self.embedder.model_name,
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "created_at": datetime.now().isoformat(),
            "total_documents": len(self.documents),
        }

        try:
            with open(save_path, "wb") as f:
                pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            self.index_path = save_path
            logger.info(
                "Index saved to %s with %d documents",
                save_path,
                len(self.documents),
            )
        except Exception as e:
            logger.error("Failed to save index to %s: %s", save_path, e)
            raise

    def load(self, path: str) -> None:
        """
        Load index from disk.

        Args:
            path: File path to load the index from.

        Raises:
            FileNotFoundError: If the index file doesn't exist.
            pickle.UnpicklingError: If the index file is corrupted.
        """
        load_path = Path(path)

        if not load_path.exists():
            raise FileNotFoundError(f"Index file not found: {path}")

        try:
            with open(load_path, "rb") as f:
                index_data = pickle.load(f)  # nosec: trusted local file

            self.documents = index_data["documents"]
            self.embeddings = index_data["embeddings"]
            self.index_path = load_path

            # Recreate embedder if model name doesn't match
            loaded_model = index_data.get("model_name")
            if loaded_model and self.embedder.model_name != loaded_model:
                logger.warning(
                    "Model mismatch: loaded '%s', current '%s'. " "Embeddings may be incompatible.",
                    loaded_model,
                    self.embedder.model_name,
                )

            logger.info(
                "Index loaded from %s with %d documents",
                load_path,
                len(self.documents),
            )
        except (pickle.PickleError, KeyError) as e:
            logger.error("Failed to load index from %s: %s", load_path, e)
            raise

    def get_stats(self) -> dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Dictionary with index statistics.
        """
        return {
            "total_documents": len(self.documents),
            "total_embeddings": len(self.embeddings),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "model_name": self.embedder.model_name,
            "index_path": str(self.index_path) if self.index_path else None,
            "is_empty": len(self.documents) == 0,
        }

    def clear(self) -> None:
        """
        Clear all documents and embeddings from the index.
        """
        self.documents.clear()
        self.embeddings.clear()
        self.index_path = None
        logger.info("Index cleared")

    def remove_document(self, doc_id: int) -> bool:
        """
        Remove a document by ID.

        Args:
            doc_id: Document ID to remove.

        Returns:
            True if document was removed, False otherwise.
        """
        if 0 <= doc_id < len(self.documents):
            self.documents[doc_id] = None  # type: ignore
            self.embeddings[doc_id] = None  # type: ignore
            logger.debug("Marked document %d for removal", doc_id)
            # Note: This doesn't compact the index, just marks as None
            return True
        return False

    def compact(self) -> None:
        """
        Remove None entries and reindex remaining documents.
        Call this after multiple remove_document() calls.
        """
        valid_indices = [i for i, doc in enumerate(self.documents) if doc is not None]

        if len(valid_indices) == len(self.documents):
            return

        self.documents = [self.documents[i] for i in valid_indices]  # type: ignore
        self.embeddings = [self.embeddings[i] for i in valid_indices]  # type: ignore

        # Reassign IDs
        for new_id, doc in enumerate(self.documents):
            if doc is not None:
                doc["id"] = new_id

        logger.info("Compacted index: %d documents remain", len(self.documents))
