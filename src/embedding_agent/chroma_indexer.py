"""
ChromaDB-based document indexer for RAG system.
Replaces the simple in-memory indexer with persistent vector storage.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None

from .embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class ChromaDocumentIndexer:
    """Document indexer using ChromaDB for persistent vector storage."""
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "project_docs",
                 embedder: Optional[DocumentEmbedder] = None):
        """
        Initialize ChromaDB indexer.
        
        Args:
            persist_directory: Directory to store ChromaDB data
            collection_name: Name of the collection in ChromaDB
            embedder: DocumentEmbedder instance. If None, creates a default one.
        """
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is not available. Install with: pip install chromadb>=0.4.22")
        
        self.embedder = embedder or DocumentEmbedder()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Project documentation for RAG system"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a document to ChromaDB index.
        
        Args:
            text: Document text content.
            metadata: Optional metadata (source file, line numbers, etc.)
            
        Returns:
            Document ID in ChromaDB.
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
        doc_metadata.update({
            "timestamp": datetime.now().isoformat(),
            "embedding_model": self.embedder.model_name,
            "text_length": len(text)
        })
        
        # Add to ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[doc_metadata],
            documents=[text.strip()]
        )
        
        logger.debug(f"Added document {doc_id}: {text[:50]}...")
        return doc_id
    
    def add_documents_from_files(self, file_pattern: str = "**/*.md", 
                                 root_dir: str = ".") -> List[str]:
        """
        Add documents from files matching pattern.
        
        Args:
            file_pattern: Glob pattern for files to index.
            root_dir: Root directory to search from.
            
        Returns:
            List of document IDs added.
        """
        from pathlib import Path
        
        root = Path(root_dir)
        file_paths = list(root.glob(file_pattern))
        logger.info(f"Found {len(file_paths)} files matching {file_pattern}")
        
        doc_ids = []
        for file_path in file_paths:
            try:
                content = file_path.read_text(encoding='utf-8')
                metadata = {
                    "source": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                    "file_type": file_path.suffix
                }
                
                # Split large documents into chunks
                chunks = self._chunk_text(content, max_chunk_size=1000)
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    
                    doc_id = self.add_document(chunk, chunk_metadata)
                    if doc_id:
                        doc_ids.append(doc_id)
                        
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Added {len(doc_ids)} document chunks from {len(file_paths)} files")
        return doc_ids
    
    def _chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for better search results."""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        # Simple chunking by paragraphs first
        paragraphs = text.split('\n\n')
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
        
        # If still too large, split by sentences
        if any(len(chunk) > max_chunk_size * 2 for chunk in chunks):
            # Fallback to character-based chunking
            chunks = []
            for i in range(0, len(text), max_chunk_size):
                chunks.append(text[i:i + max_chunk_size])
        
        return chunks
    
    def search(self, query: str, top_k: int = 5, 
               where_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to query using ChromaDB.
        
        Args:
            query: Search query text.
            top_k: Number of top results to return.
            where_filter: Optional filter for metadata (e.g., {"source": "*.md"})
            
        Returns:
            List of documents with similarity scores.
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
                include=["metadatas", "documents", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    doc_id = results["ids"][0][i]
                    distance = results["distances"][0][i]
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    text = results["documents"][0][i] if results["documents"] else ""
                    
                    # Convert distance to similarity score (ChromaDB uses distance, not similarity)
                    # Smaller distance = more similar, so we invert it
                    similarity_score = 1.0 / (1.0 + distance) if distance > 0 else 1.0
                    
                    formatted_results.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata,
                        "score": float(similarity_score),
                        "distance": float(distance),
                        "rank": i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics from ChromaDB."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory),
                "embedding_model": self.embedder.model_name,
                "embedding_dimension": self.embedder.model.get_sentence_embedding_dimension()
            }
        except Exception as e:
            logger.error(f"Error getting ChromaDB stats: {e}")
            return {"error": str(e)}
    
    def delete_collection(self):
        """Delete the entire collection (use with caution!)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            # Reinitialize
            self._initialize_chroma()
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def migrate_from_pickle(self, pickle_path: str) -> List[str]:
        """
        Migrate documents from pickle-based index to ChromaDB.
        
        ⚠️ SECURITY WARNING: This method uses pickle for legacy data migration only.
        Never use this with untrusted input. For production, use JSON format.
        
        Args:
            pickle_path: Path to pickle file from old indexer.
            
        Returns:
            List of migrated document IDs.
        """
        import pickle
        from pathlib import Path
        
        pickle_file = Path(pickle_path)
        if not pickle_file.exists():
            logger.error(f"Pickle file not found: {pickle_path}")
            return []
        
        try:
            # SECURITY: Only load from trusted local path
            with open(pickle_file, 'rb') as f:
                index_data = pickle.load(f)  # nosec: trusted local file for migration only
            
            documents = index_data.get("documents", [])
            embeddings = index_data.get("embeddings", [])
            
            logger.info(f"Migrating {len(documents)} documents from pickle index")
            
            migrated_ids = []
            for i, doc in enumerate(documents):
                if i < len(embeddings):
                    # For migration, we need to add with existing embedding
                    doc_id = str(uuid.uuid4())
                    metadata = doc.get("metadata", {})
                    metadata.update({
                        "migrated_from_pickle": True,
                        "original_timestamp": doc.get("timestamp", ""),
                        "migration_timestamp": datetime.now().isoformat()
                    })
                    
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embeddings[i]],
                        metadatas=[metadata],
                        documents=[doc.get("text", "")]
                    )
                    migrated_ids.append(doc_id)
            
            logger.info(f"Successfully migrated {len(migrated_ids)} documents to ChromaDB")
            return migrated_ids
            
        except Exception as e:
            logger.error(f"Error migrating from pickle: {e}")
            return []
