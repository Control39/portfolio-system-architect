"""Unit tests for ChromaDocumentIndexer fallback paths.

These tests are designed to increase coverage for src/embedding_agent/chroma_indexer.py
when chromadb is not installed (or is mocked away).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_chroma_indexer_add_documents_from_files_fallback(tmp_path: Path):
    """When chromadb is unavailable, add_documents_from_files should still work."""
    # Ensure chromadb is considered unavailable
    with patch.dict("sys.modules", {"chromadb": None, "chromadb.config": None}):
        # Import inside context to re-evaluate CHROMA_AVAILABLE
        from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer

        # Create a couple of small md files
        (tmp_path / "a.md").write_text("Alpha\n\nBeta", encoding="utf-8")
        (tmp_path / "b.md").write_text("Gamma", encoding="utf-8")

        indexer = ChromaDocumentIndexer(persist_directory=str(tmp_path / "db"))

        doc_ids = indexer.add_documents_from_files(file_pattern="*.md", root_dir=str(tmp_path))
        assert isinstance(doc_ids, list)
        assert len(doc_ids) >= 2

        stats = indexer.get_stats()
        assert "total_documents" in stats
        assert stats["total_documents"] == indexer.collection.count()

        indexer.close()


def test_chroma_indexer_search_empty_embedding_returns_empty(tmp_path: Path):
    """If embedder returns empty embedding, search should return empty list.

    Важно: используем простой embedder-заглушку без импорта numpy/
    sentence-transformers, чтобы не триггерить edge-case с numpy в окружении.
    """
    with patch.dict("sys.modules", {"chromadb": None, "chromadb.config": None}):
        from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer

        embedder = MagicMock()
        embedder.embed = MagicMock(return_value=[])
        embedder.model_name = "test-model"

        indexer = ChromaDocumentIndexer(
            persist_directory=str(tmp_path / "db"),
            embedder=embedder,
        )
        results = indexer.search("query", top_k=3)
        assert results == []



def test_chroma_indexer_search_filters_empty_ids(monkeypatch, tmp_path: Path):
    """If chroma returns empty ids, search should produce empty formatted results."""
    with patch.dict("sys.modules", {"chromadb": None, "chromadb.config": None}):
        from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer
        from src.embedding_agent.embedder import DocumentEmbedder

        embedder = DocumentEmbedder()
        embedder.embed = MagicMock(return_value=[0.1, 0.2, 0.3])

        indexer = ChromaDocumentIndexer(persist_directory=str(tmp_path / "db"), embedder=embedder)
        # Replace collection.query to return empty ids
        indexer.collection.query = MagicMock(return_value={"ids": [[]], "distances": [[0.0]], "metadatas": [[{}]], "documents": [[""]]})

        results = indexer.search("query", top_k=1)
        assert results == []


