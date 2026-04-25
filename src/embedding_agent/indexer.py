"""
Document indexer for building and managing vector search index.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Index documents for vector search."""
    
    def __init__(self, embedder: Optional[DocumentEmbedder] = None):
        """
        Initialize the indexer.
        
        Args:
            embedder: DocumentEmbedder instance. If None, creates a default one.
        """
        self.embedder = embedder or DocumentEmbedder()
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.index_path: Optional[Path] = None
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a document to the index.
        
        Args:
            text: Document text content.
            metadata: Optional metadata (source file, line numbers, etc.)
            
        Returns:
            Document ID in the index.
        """
        if not text or not text.strip():
            return -1
        
        doc_id = len(self.documents)
        doc = {
            "id": doc_id,
            "text": text.strip(),
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate embedding
        embedding = self.embedder.embed(text)
        if not embedding:
            logger.warning(f"Failed to generate embedding for document {doc_id}")
            return -1
        
        self.documents.append(doc)
        self.embeddings.append(embedding)
        
        logger.debug(f"Added document {doc_id}: {text[:50]}...")
        return doc_id
    
    def add_documents_from_files(self, file_pattern: str = "**/*.md", 
                                 root_dir: str = ".") -> List[int]:
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
                    "last_modified": file_path.stat().st_mtime
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
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to query.
        
        Args:
            query: Search query text.
            top_k: Number of top results to return.
            
        Returns:
            List of documents with similarity scores.
        """
        if not self.documents:
            return []
        
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            return []
        
        # Compute similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self.embedder.compute_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Prepare results
        results = []
        for i, (doc_idx, score) in enumerate(similarities[:top_k]):
            doc = self.documents[doc_idx].copy()
            doc["score"] = float(score)
            doc["rank"] = i + 1
            results.append(doc)
        
        return results
    
    def save(self, path: str) -> None:
        """Save index to disk."""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        index_data = {
            "documents": self.documents,
            "embeddings": self.embeddings,
            "model_name": self.embedder.model_name,
            "created_at": datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        self.index_path = save_path
        logger.info(f"Index saved to {save_path} with {len(self.documents)} documents")
    
    def load(self, path: str) -> None:
        """Load index from disk."""
        load_path = Path(path)
        
        # SECURITY: Only load from trusted local path
        with open(load_path, 'rb') as f:
            index_data = pickle.load(f)  # nosec: trusted local file
        
        self.documents = index_data["documents"]
        self.embeddings = index_data["embeddings"]
        self.index_path = load_path
        
        # Recreate embedder if model name doesn't match
        if hasattr(self.embedder, 'model_name') and self.embedder.model_name != index_data.get("model_name"):
            logger.warning(f"Model mismatch: loaded {index_data.get('model_name')}, current {self.embedder.model_name}")
        
        logger.info(f"Index loaded from {load_path} with {len(self.documents)} documents")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_documents": len(self.documents),
            "total_embeddings": len(self.embeddings),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "model_name": self.embedder.model_name,
            "index_path": str(self.index_path) if self.index_path else None
        }
