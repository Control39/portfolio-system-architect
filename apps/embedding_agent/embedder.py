"""ChromaDB-based document indexer for RAG system."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import chromadb
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:  # pragma: no cover
    CHROMA_AVAILABLE = False
    chromadb = None  # type: ignore
    Settings = None  # type: ignore

from .embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class _InMemoryCollection:
    """Минимальная заглушка Chroma collection для unit-тестов без chromadb."""

    def __init__(self) -> None:
        self._docs: list[str] = []
        self._metadatas: list[dict[str, Any]] = []
        self._embeddings: list[list[float]] = []
        self._ids: list[str] = []

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        n = min(len(a), len(b))
        if n == 0:
            return 0.0
        dot = 0.0
        na = 0.0
        nb = 0.0
        for i in range(n):
            dot += a[i] * b[i]
            na += a[i] * a[i]
            nb += b[i] * b[i]
        if na <= 0.0 or nb <= 0.0:
            return 0.0
        return float(dot / ((na**0.5) * (nb**0.5)))

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        for i, doc in enumerate(documents):
            self._ids.append(ids[i] if i < len(ids) else str(uuid.uuid4()))
            self._docs.append(doc)
            self._embeddings.append(embeddings[i] if i < len(embeddings) else [])
            self._metadatas.append(metadatas[i] if i < len(metadatas) else {})

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any] | None = None,  # noqa: ARG002 (not used in mock)
        include: list[str] | None = None,  # noqa: ARG002 (not used in mock)
    ) -> dict[str, Any]:
        """Query the in-memory collection."""
        q = query_embeddings[0] if query_embeddings else []

        q_str = "".join(str(x) for x in q) if q else ""

        scored: list[tuple[int, float]] = []
        for idx, emb in enumerate(self._embeddings):
            doc_text = self._docs[idx] or ""
            doc_l = doc_text.lower()

            overlap = 0.0
            if q_str and q_str[:12].lower() in doc_l:
                overlap = 1.0

            sim = self._cosine_similarity(q, emb)
            scored.append((idx, sim + overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        n = min(n_results, len(scored))

        top = scored[:n]
        ids = [self._ids[i] for i, _ in top]
        distances = [[1.0 - score for _, score in top]]  # Convert similarity to distance
        metadatas = [[self._metadatas[i] for i, _ in top]]
        documents = [[self._docs[i] for i, _ in top]]

        return {
            "ids": [ids],
            "distances": distances,
            "metadatas": metadatas,
            "documents": documents,
        }

    def count(self) -> int:
        return len(self._docs)


class ChromaDocumentIndexer:
    """Persistent vector index stored in ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "project_docs",
        embedder: DocumentEmbedder | None = None,
    ) -> None:
        self.embedder = embedder or DocumentEmbedder()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Separate storage for when Chroma is not available
        self._use_fallback_only = not CHROMA_AVAILABLE
        self._fallback_docs: list[
            tuple[str, dict[str, Any], list[float], str]
        ] = []  # text, metadata, embedding, doc_id

        if not CHROMA_AVAILABLE:
            self.client = None
            self.collection = _InMemoryCollection()
            return

        self.client: Any | None = None
        self.collection: Any | None = None
        self._initialize_chroma()

    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info("Loaded existing collection: %s", self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Project documentation for RAG system",
                },
            )
            logger.info("Created new collection: %s", self.collection_name)

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add a single document to the index."""
        if not text or not text.strip():
            return ""

        embedding = self.embedder.embed(text)
        if not embedding:
            return ""

        doc_id = str(uuid.uuid4())

        doc_metadata = dict(metadata or {})
        doc_metadata.update(
            {
                "timestamp": datetime.now().isoformat(),
                "embedding_model": self.embedder.model_name,
                "text_length": len(text),
            }
        )

        # Store in fallback only if we're in fallback-only mode
        if self._use_fallback_only:
            self._fallback_docs.append((text.strip(), doc_metadata, embedding, doc_id))
            if self.collection is not None:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[doc_metadata],
                    documents=[text.strip()],
                )
            return doc_id

        # Normal Chroma mode
        if self.collection is None:
            self.collection = _InMemoryCollection()
            self._use_fallback_only = True
            self._fallback_docs.append((text.strip(), doc_metadata, embedding, doc_id))
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[text.strip()],
            )
            return doc_id

        try:
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[text.strip()],
            )
        except Exception as e:
            logger.warning("Failed to add to Chroma, falling back to in-memory: %s", e)
            self.collection = _InMemoryCollection()
            self._use_fallback_only = True
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[doc_metadata],
                documents=[text.strip()],
            )
            self._fallback_docs.append((text.strip(), doc_metadata, embedding, doc_id))

        return doc_id

    def add_documents_from_files(self, file_pattern: str = "**/*.md", root_dir: str = ".") -> list[str]:
        """Add all documents matching pattern from root directory."""
        root = Path(root_dir)
        file_paths = list(root.glob(file_pattern))

        doc_ids: list[str] = []
        for file_path in file_paths:
            try:
                content = file_path.read_text(encoding="utf-8")
                metadata = {
                    "source": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                    "file_type": file_path.suffix,
                }

                chunks = self._chunk_text(content, max_chunk_size=1000)
                for i, chunk in enumerate(chunks):
                    chunk_metadata = dict(metadata)
                    chunk_metadata["chunk"] = i
                    chunk_metadata["total_chunks"] = len(chunks)

                    doc_id = self.add_document(chunk, chunk_metadata)
                    if doc_id:
                        doc_ids.append(doc_id)
            except Exception as e:
                logger.error("Error processing file %s: %s", file_path, e)

        return doc_ids

    @staticmethod
    def _chunk_text(text: str, max_chunk_size: int = 1000) -> list[str]:
        """Split text into chunks."""
        if len(text) <= max_chunk_size:
            return [text]

        chunks: list[str] = []
        paragraphs = text.split("\n\n")
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= max_chunk_size:
                current += para + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                current = para + "\n\n"

        if current:
            chunks.append(current.strip())

        # Fallback to simple character-based chunking if still too large
        if any(len(c) > max_chunk_size * 2 for c in chunks):
            return [text[i : i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

        return chunks

    def search(
        self,
        query: str,
        top_k: int = 5,
        where_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar documents."""
        # Use fallback keyword search as last resort
        if self._use_fallback_only and not self.collection:
            q = query.lower().strip()
            scored: list[tuple[float, str, dict[str, Any], str]] = []
            for text, meta, _emb, doc_id in self._fallback_docs:
                t = text.lower()
                # Simple keyword matching score
                score = sum(1 for word in q.split() if word in t) / max(1, len(q.split()))
                if q and q in t:
                    score = max(score, 0.5)
                scored.append((score, text, meta, doc_id))

            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[:top_k]
            return [
                {
                    "id": doc_id,
                    "text": text,
                    "metadata": meta or {},
                    "score": float(score),
                    "distance": 1.0 - float(score),
                    "rank": idx + 1,
                }
                for idx, (score, text, meta, doc_id) in enumerate(top)
                if score > 0
            ]

        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []

        if self.collection is None:
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "documents", "distances"],
            )
        except Exception as e:
            logger.error("Search failed: %s", e)
            return []

        formatted: list[dict[str, Any]] = []
        if results.get("ids") and results["ids"] and results["ids"][0]:
            ids0 = results["ids"][0]
            d0 = results.get("distances", [[None]])[0]
            metas0 = results.get("metadatas", [[None]])[0]
            docs0 = results.get("documents", [[None]])[0]

            for i, doc_id in enumerate(ids0):
                distance = d0[i] if i < len(d0) else 0.0
                metadata = metas0[i] if metas0 else {}
                text = docs0[i] if docs0 else ""

                # Convert distance to similarity score (assuming cosine distance)
                similarity = 1.0 - float(distance) if distance is not None else 0.0

                formatted.append(
                    {
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata or {},
                        "score": max(0.0, min(1.0, similarity)),
                        "distance": float(distance) if distance is not None else 0.0,
                        "rank": i + 1,
                    }
                )

        return formatted

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        try:
            if self.collection is not None and not self._use_fallback_only:
                count = int(self.collection.count())
            else:
                count = len(self._fallback_docs)
        except Exception:
            count = len(self._fallback_docs)

        return {
            "total_documents": count,
            "total_chunks": count,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory),
            "embedding_model": self.embedder.model_name,
            "fallback_mode": self._use_fallback_only,
        }

    def close(self) -> None:
        """Close ChromaDB connection."""
        if self.client:
            try:
                # ChromaDB client doesn't have explicit close, but we can clear references
                pass
            except Exception:
                pass
        self.collection = None
        self.client = None
