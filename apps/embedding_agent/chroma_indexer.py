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
            self._docs.append(doc)
            self._embeddings.append(embeddings[i] if i < len(embeddings) else [])
            self._metadatas.append(metadatas[i] if i < len(metadatas) else {})

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        q = query_embeddings[0] if query_embeddings else []

        q_str = "".join(str(x) for x in q) if q else ""

        scored: list[tuple[int, float]] = []
        for idx, emb in enumerate(self._embeddings):
            doc_text = self._docs[idx] or ""
            doc_l = doc_text.lower()

            overlap = 0.0
            if q_str:
                if doc_l.find(q_str[:12].lower()) != -1:
                    overlap = 1.0

            sim = self._cosine_similarity(q, emb)
            scored.append((idx, float(sim) + overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        n = min(n_results, len(scored))

        top = scored[:n]
        ids = [str(i) for i, _ in top]
        distances = [[0.0 for _ in range(n)]]
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
        # Fallback storage (used when Chroma is present but not working)
        self._fallback_docs: list[tuple[str, dict[str, Any], list[float]]] = []

        self.embedder = embedder or DocumentEmbedder()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        if not CHROMA_AVAILABLE:
            self.client = None
            self.collection = None
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
                metadata={"description": "Project documentation for RAG system"},
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

        # Always add to fallback storage for consistency
        self._fallback_docs.append((text.strip(), doc_metadata, embedding))

        # Try to add to Chroma if available
        if self.collection is not None and CHROMA_AVAILABLE:
            try:
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[doc_metadata],
                    documents=[text.strip()],
                )
                return doc_id
            except Exception:
                # If Chroma fails, fall back to in-memory collection
                if not isinstance(self.collection, _InMemoryCollection):
                    self.collection = _InMemoryCollection()
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[doc_metadata],
                    documents=[text.strip()],
                )
            return doc_id

        # If no Chroma collection, use in-memory
        if self.collection is None:
            self.collection = _InMemoryCollection()
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[text.strip()],
        )
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
        """Split text into overlapping chunks."""
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
        # Use fallback keyword search if no real embeddings available
        if self._fallback_docs and not CHROMA_AVAILABLE:
            q = query.lower().strip()
            scored: list[tuple[float, str, dict[str, Any]]] = []
            for text, meta, _emb in self._fallback_docs:
                t = text.lower()
                score = 1.0 if q and q in t else 0.0
                scored.append((score, text, meta))
            scored.sort(key=lambda x: x[0], reverse=True)
            top = scored[:top_k]
            return [
                {
                    "id": str(idx),
                    "text": text,
                    "metadata": meta or {},
                    "score": float(s),
                    "distance": 0.0,
                    "rank": idx + 1,
                }
                for idx, (s, text, meta) in enumerate(top)
            ]

        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []

        if self.collection is None:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["metadatas", "documents", "distances"],
        )

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

                similarity = 1.0 / (1.0 + distance) if distance is not None and distance >= 0 else 0.0

                formatted.append(
                    {
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata or {},
                        "score": float(similarity),
                        "distance": float(distance) if distance is not None else 0.0,
                        "rank": i + 1,
                    }
                )

        return formatted

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        try:
            if self.collection is not None and CHROMA_AVAILABLE:
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
        }

    def close(self) -> None:
        """Close ChromaDB connection."""
        self.collection = None
        self.client = None
