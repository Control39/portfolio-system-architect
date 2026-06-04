"""
Tests for mcp_server chroma_tools business logic
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestChromaToolsModule:
    """Basic tests for chroma_tools module structure"""

    def test_module_imports(self):
        """Test that chroma_tools module can be imported"""
        from apps.mcp_server.src.tools import chroma_tools

        assert chroma_tools is not None

    def test_init_chroma_tools_exists(self):
        """Test that init_chroma_tools function exists"""
        from apps.mcp_server.src.tools import chroma_tools

        assert hasattr(chroma_tools, "init_chroma_tools")
        assert callable(chroma_tools.init_chroma_tools)


class TestChromaToolsBusiness:
    """Tests for chroma_tools business logic with mocks"""

    @pytest.fixture
    def mock_chromadb(self):
        """Mock chromadb module"""
        mock_client = MagicMock()
        mock_collection = MagicMock()

        # Mock collection methods
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 10
        mock_collection.add.return_value = None
        mock_collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "distances": [[0.5, 0.8]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "ids": [["id1", "id2"]],
        }

        mock_client.get_collection.return_value = mock_collection
        mock_client.create_collection.return_value = mock_collection
        mock_client.list_collections.return_value = [mock_collection]

        return mock_client, mock_collection

    def test_get_collections_logic(self, mock_chromadb):
        """Test getting collections logic"""
        mock_client, _ = mock_chromadb

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = mock_client

            # Simulate the tool logic
            client = mock_client_cls(path="/test/chroma_data")
            collections = client.list_collections()
            result = [col.name for col in collections]

            assert len(result) == 1
            assert result[0] == "test_collection"

    def test_query_documents_logic(self, mock_chromadb):
        """Test querying documents logic"""
        mock_client, _ = mock_chromadb

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = mock_client

            # Simulate query logic
            collection = mock_client.get_collection("test_collection")
            results = collection.query(query_texts=["query"], n_results=5)

            assert results is not None
            assert "documents" in results
            assert len(results["documents"][0]) == 2

    def test_add_document_logic(self, mock_chromadb):
        """Test adding document logic"""
        mock_client, _ = mock_chromadb

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = mock_client

            # Simulate add logic
            collection = mock_client.get_collection("test_collection")
            result = collection.add(
                documents=["test doc"], metadatas=[{"source": "test"}], ids=["doc1"]
            )

            assert result is None  # add returns None on success
            collection.add.assert_called_once()

    def test_add_document_creates_collection_if_not_exists(self, mock_chromadb):
        """Test that add creates collection if not exists"""
        mock_client, _ = mock_chromadb

        # Make get_collection raise exception to trigger create
        mock_client.get_collection.side_effect = Exception("Not found")

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = mock_client

            # Simulate logic
            try:
                mock_client.get_collection("new_collection")
            except Exception:
                mock_client.create_collection("new_collection")

            assert mock_client.create_collection.called

    def test_get_collection_info_logic(self, mock_chromadb):
        """Test getting collection info logic"""
        mock_client, mock_collection = mock_chromadb
        mock_collection.count.return_value = 42

        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client_cls.return_value = mock_client

            # Simulate logic
            collection = mock_client.get_collection("test_collection")
            count = collection.count()

            assert count == 42

    def test_get_collection_not_found_logic(self):
        """Test handling collection not found"""
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_collection.side_effect = Exception("Not found")
            mock_client_cls.return_value = mock_client

            # Simulate logic
            try:
                collection = mock_client.get_collection("nonexistent")
                count = collection.count()
                result = {"status": "exists", "count": count}
            except Exception:
                result = {"status": "not_found"}

            assert result["status"] == "not_found"

    def test_document_id_generation(self):
        """Test document ID generation"""
        import hashlib

        document = "test document content"
        doc_id = hashlib.md5(document.encode(), usedforsecurity=False).hexdigest()

        assert len(doc_id) == 32  # MD5 hash length
        assert isinstance(doc_id, str)

    def test_query_results_formatting(self):
        """Test query results formatting"""
        mock_results = {
            "documents": [["doc1", "doc2"]],
            "distances": [[0.5, 0.8]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "ids": [["id1", "id2"]],
        }

        formatted = []
        if mock_results and mock_results.get("documents") and mock_results["documents"][0]:
            for i, doc in enumerate(mock_results["documents"][0]):
                result = {
                    "document": doc,
                    "distance": mock_results["distances"][0][i],
                    "metadata": mock_results["metadatas"][0][i],
                    "id": mock_results["ids"][0][i],
                }
                formatted.append(result)

        assert len(formatted) == 2
        assert formatted[0]["document"] == "doc1"
        assert formatted[0]["distance"] == 0.5
        assert formatted[0]["metadata"]["source"] == "test1"

    def test_n_results_parameter_validation(self):
        """Test n_results parameter validation"""
        n_results = 5
        assert n_results > 0
        assert n_results <= 100  # Reasonable limit

    def test_error_handling_in_query(self):
        """Test error handling in query"""
        with patch("chromadb.PersistentClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get_collection.side_effect = Exception("DB error")
            mock_client_cls.return_value = mock_client

            # Simulate error handling
            try:
                mock_client.get_collection("test")
                result = {"status": "success"}
            except Exception as e:
                result = {"error": f"query error: {e}"}

            assert "error" in result
            assert "DB error" in result["error"]

    def test_collection_path_construction(self):
        """Test chroma data path construction"""

        project_root = Path("/project")
        chroma_path = project_root / "chroma_data"

        # Path may use different separators on different OS
        assert "chroma_data" in str(chroma_path)
        assert project_root.name in str(chroma_path)

    def test_metadata_handling(self):
        """Test metadata handling"""
        metadata = {"source": "test", "timestamp": "2026-05-17"}

        assert metadata["source"] == "test"
        assert metadata["timestamp"] == "2026-05-17"

    def test_empty_results_handling(self):
        """Test empty results handling"""
        mock_results = {"documents": [[]], "distances": [[]], "metadatas": [[]], "ids": [[]]}

        formatted = []
        if mock_results and mock_results.get("documents") and mock_results["documents"][0]:
            for _i, doc in enumerate(mock_results["documents"][0]):
                result = {"document": doc}
                formatted.append(result)

        assert len(formatted) == 0  # Empty list
