"""
Ollama-based embedder for offline/fallback mode.

This provides an alternative to sentence-transformers using Ollama's embedding API.
Useful when you want to avoid local model downloads or use larger models.
"""

import logging

import requests


logger = logging.getLogger(__name__)


class OllamaEmbedder:
    """Embed documents using Ollama's embedding API."""

    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        timeout: int = 30,
    ):
        """
        Initialize Ollama embedder.

        Args:
            model_name: Ollama model name (e.g., "nomic-embed-text", "mxbai-embed-large").
            base_url: Ollama base URL.
            timeout: Request timeout in seconds.
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._embedding_dimension = None

        logger.info(f"Initializing Ollama embedder: {model_name} @ {self.base_url}")

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension (cached)."""
        if self._embedding_dimension is not None:
            return self._embedding_dimension

        # Try to get dimension from a test embedding
        test_embedding = self.embed("test")
        if test_embedding:
            self._embedding_dimension = len(test_embedding)
            return self._embedding_dimension

        # Default dimensions for common models
        default_dims = {
            "nomic-embed-text": 768,
            "mxbai-embed-large": 1024,
            "all-minilm": 384,
        }
        self._embedding_dimension = default_dims.get(self.model_name, 768)
        return self._embedding_dimension

    def embed(self, text: str) -> list[float]:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector, or empty list on error.
        """
        if not text or not text.strip():
            return []

        text = text.strip()

        # Check if Ollama is available
        if not self._check_ollama_available():
            logger.warning("Ollama not available, returning empty embedding")
            return []

        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text,
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return []

            result = response.json()
            embedding = result.get("embedding", [])
            return embedding

        except requests.RequestException as e:
            logger.error(f"Request to Ollama failed: {e}")
            return []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts.

        Note: Ollama doesn't support batch embeddings via API, so we call it multiple times.
        For better performance, consider using sentence-transformers instead.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []

        embeddings = []
        for text in texts:
            embedding = self.embed(text)
            if embedding:
                embeddings.append(embedding)
            else:
                embeddings.append([])

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self._get_embedding_dimension()

    def is_available(self) -> bool:
        """Check if Ollama is available and model is loaded."""
        return self._check_ollama_available()
