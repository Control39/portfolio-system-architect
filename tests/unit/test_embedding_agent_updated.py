"""
Unit tests for embedding_agent module.
"""

from unittest.mock import MagicMock, patch


def test_document_embedder_initialization():
    """Test initialization of DocumentEmbedder."""
    from src.embedding_agent.embedder import DocumentEmbedder

    embedder = DocumentEmbedder(model_name="test-model")
    assert embedder is not None
    assert embedder.model_name == "test-model"


def test_document_embedder_embed():
    """Test embedding generation for a document."""
    from src.embedding_agent.embedder import DocumentEmbedder

    # Mock the SentenceTransformer model
    with patch("src.embedding_agent.embedder.SentenceTransformer") as mock_model:
        mock_model.return_value.encode.return_value = [0.1, 0.2, 0.3]

        embedder = DocumentEmbedder(model_name="test-model")
        result = embedder.embed("test text")

        assert isinstance(result, list)
        assert len(result) == 3
        mock_model.return_value.encode.assert_called_once_with("test text", convert_to_numpy=True)


def test_document_indexer_initialization():
    """Test initialization of DocumentIndexer."""
    from src.embedding_agent.embedder import DocumentEmbedder
    from src.embedding_agent.indexer import DocumentIndexer

    embedder = DocumentEmbedder(model_name="test-model")
    indexer = DocumentIndexer(embedder=embedder)

    assert indexer is not None
    assert indexer.embedder == embedder
    assert len(indexer.documents) == 0
    assert len(indexer.embeddings) == 0


def test_document_indexer_add_document():
    """Test adding a document to the index."""
    from src.embedding_agent.embedder import DocumentEmbedder
    from src.embedding_agent.indexer import DocumentIndexer

    # Mock the embedder
    with patch.object(DocumentEmbedder, "embed", return_value=[0.1, 0.2, 0.3]):
        indexer = DocumentIndexer()
        doc_id = indexer.add_document("test document", {"source": "test.py"})

        assert doc_id == 0
        assert len(indexer.documents) == 1
        assert len(indexer.embeddings) == 1
        assert indexer.documents[0]["text"] == "test document"
        assert indexer.documents[0]["metadata"]["source"] == "test.py"
        assert indexer.embeddings[0] == [0.1, 0.2, 0.3]


def test_document_searcher_initialization():
    """Test initialization of DocumentSearcher."""
    from src.embedding_agent.search import DocumentSearcher

    searcher = DocumentSearcher()
    assert searcher is not None
    assert searcher.indexer is not None


def test_document_searcher_build_index():
    """Test building index from files."""
    from src.embedding_agent.search import DocumentSearcher

    # Mock the add_documents_from_files method
    with patch.object(DocumentSearcher, "build_index", return_value={"total_documents": 5}):
        searcher = DocumentSearcher()
        stats = searcher.build_index()

        assert stats["total_documents"] == 5


def test_chroma_document_indexer_initialization():
    """Test initialization of ChromaDocumentIndexer."""
    from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer

    # Mock chromadb to avoid import error
    with patch.dict("sys.modules", {"chromadb": MagicMock(), "chromadb.config": MagicMock()}):
        indexer = ChromaDocumentIndexer(
            persist_directory="./test_db", collection_name="test_collection"
        )

        assert indexer is not None
        assert indexer.persist_directory.name == "test_db"
        assert indexer.collection_name == "test_collection"


def test_chroma_document_indexer_add_document():
    """Test adding a document to ChromaDocumentIndexer."""
    from src.embedding_agent.chroma_indexer import ChromaDocumentIndexer

    # Mock dependencies
    with patch.dict("sys.modules", {"chromadb": MagicMock(), "chromadb.config": MagicMock()}):
        with patch("uuid.uuid4", return_value="test-uuid"):
            with patch("src.embedding_agent.chroma_indexer.DocumentEmbedder") as mock_embedder:
                mock_embedder.return_value.embed.return_value = [0.1, 0.2, 0.3]

                indexer = ChromaDocumentIndexer(persist_directory="./test_db")
                doc_id = indexer.add_document("test text", {"source": "test.py"})

                assert doc_id == "test-uuid"
                # Collection.add should be called with correct parameters
                indexer.collection.add.assert_called_once_with(
                    ids=["test-uuid"],
                    embeddings=[[0.1, 0.2, 0.3]],
                    metadatas=[
                        {
                            "source": "test.py",
                            "timestamp": (
                                indexer.collection.add.call_args[1]["metadatas"][0]["timestamp"]
                            ),
                            "embedding_model": mock_embedder.return_value.model_name,
                            "text_length": 9,
                        }
                    ],
                    documents=["test text"],
                )
