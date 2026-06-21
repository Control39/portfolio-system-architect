"""ChromaDB-based document indexer for RAG system."""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
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


# ============== Базовый интерфейс для vector store ==============


class VectorStore(ABC):
    """Абстрактный протокол для vector storage."""

    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Добавить документы в хранилище."""
        pass

    @abstractmethod
    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        """Выполнить поиск по хранилищу."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Вернуть количество документов в хранилище."""
        pass


class _InMemoryCollection(VectorStore):
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
        """Выполняет векторный поиск по хранилищу с поддержкой фильтрации."""
        q = query_embeddings[0] if query_embeddings else []

        # Вычисляем косинусное сходство для всех документов
        scored: list[tuple[int, float]] = []
        for idx, emb in enumerate(self._embeddings):
            sim = self._cosine_similarity(q, emb)
            # Применяем фильтрацию, если передана
            if where:
                metadata = self._metadatas[idx]
                # Простая проверка: все условия из where должны быть выполнены
                if not all(metadata.get(k) == v for k, v in where.items()):
                    sim = -1.0  # Уменьшаем релевантность для невыполненных условий
            scored.append((idx, sim))

        # Сортируем по убыванию релевантности
        scored.sort(key=lambda x: x[1], reverse=True)
        n = min(n_results, len(scored))

        top = scored[:n]
        ids = [str(i) for i, _ in top]
        # Преобразуем косинусное сходство в дистанцию (1 - сходство)
        distances = [[max(0.0, 1.0 - score) for _, score in top]]
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


class ChromaDocumentIndexer(AbstractContextManager):
    """Persistent vector index stored in ChromaDB with unified interface."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "project_docs",
        embedder: DocumentEmbedder | None = None,
    ) -> None:
        self.embedder = embedder or DocumentEmbedder()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Инициализируем основное хранилище или заглушку
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB not found. Using in-memory storage.")
            self.store: VectorStore = _InMemoryCollection()
            # Для backward compatibility: self.collection будет возвращать self.store через property
            return
        
        self.client: Any | None = None
        self.store: VectorStore | None = None
        self._initialize_chroma()

    @property
    def collection(self) -> Any | None:
        """Для backward compatibility: возвращает текущее хранилище."""
        return self.store

    @collection.setter
    def collection(self, value: Any | None) -> None:
        """Для backward compatibility: устанавливает хранилище."""
        self.store = value

    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB client and collection."""
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        try:
            if CHROMA_AVAILABLE and Settings is not None:
                self.client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(anonymized_telemetry=False),
                )
                try:
                    collection = self.client.get_collection(name=self.collection_name)
                    logger.info("Loaded existing collection: %s", self.collection_name)
                except Exception:
                    collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": "Project documentation for RAG system"},
                    )
                    logger.info("Created new collection: %s", self.collection_name)
                self.store = collection
            else:
                logger.warning("ChromaDB not available. Using in-memory storage.")
                self.store = _InMemoryCollection()
        except Exception as e:
            logger.error("Failed to connect to ChromaDB: %s. Falling back to in-memory mode.", e)
            self.store = _InMemoryCollection()

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add a single document to the index."""
        if not text or not text.strip():
            return ""

        embedding = self.embedder.embed(text)
        if not embedding:
            return ""

        doc_id = str(uuid.uuid4())

        doc_metadata = {
            "timestamp": datetime.now().isoformat(),
            "embedding_model": self.embedder.model_name,
            "text_length": len(text),
            **(metadata or {}),
        }

        # Единый вызов добавления, независимый от реализации store
        self.store.add(ids=[doc_id], embeddings=[embedding], metadatas=[doc_metadata], documents=[text.strip()])
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
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []

        results = self.store.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["metadatas", "documents", "distances"],
        )

        # Унифицированная обработка результата
        formatted = []
        for i, doc_id in enumerate(results.get("ids", [])):
            distance = results.get("distances", [[0]])[0][i]
            similarity = 1.0 - float(distance)
            formatted.append(
                {
                    "id": doc_id,
                    "score": max(0.0, min(1.0, similarity)),
                    "distance": float(distance),
                    "rank": i + 1,
                    "metadata": results.get("metadatas", [[]])[0][i] or {},
                    "text": results.get("documents", [[]])[0][i] or "",
                }
            )
        return formatted

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        try:
            count = int(self.store.count())
        except Exception:
            count = 0

        return {
            "total_documents": count,
            "total_chunks": count,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory),
            "embedding_model": self.embedder.model_name,
        }

    def close(self) -> None:
        """Корректное закрытие клиента ChromaDB."""
        if hasattr(self, "client") and self.client is not None:
            # У PersistentClient нет метода .close(), он работает с файлами напрямую.
            # Но можно вызвать сборку мусора или просто обнулить ссылку.
            del self.client
            self.client = None
            logger.info("Closed connection to ChromaDB")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
