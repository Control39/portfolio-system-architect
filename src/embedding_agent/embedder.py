"""
Document embedder using sentence-transformers for RAG search.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class DocumentEmbedder:
    """Embed documents using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence-transformers model.
                Default: "all-MiniLM-L6-v2" (good balance of speed/quality)
        """
        self.model_name = model_name
        logger.info(f"Loading sentence-transformers model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded, embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        if not text or not text.strip():
            return []
        
        # Clean text
        text = text.strip()
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts."""
        if not texts:
            return []
        
        # Filter empty texts
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        # Generate embeddings
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        if not embedding1 or not embedding2:
            return 0.0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()