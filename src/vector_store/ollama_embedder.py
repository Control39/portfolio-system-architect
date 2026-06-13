"""
Embedder using Ollama API (local LLM with embedding models).
"""

import logging

import requests

logger = logging.getLogger(__name__)


class OllamaEmbedder:
    """Embed text using Ollama's /api/embed endpoint (or similar)."""

    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        logger.info(f"Ollama embedder initialized: {self.model_name} at {self.base_url}")

    def embed(self, text: str) -> list[float]:
        """Embed a single text via Ollama."""
        if not text.strip():
            return []

        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
        except Exception as e:
            logger.warning(f"Ollama embed error: {e}")
            return []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts (naive sequential)."""
        return [self.embed(t) for t in texts if t.strip()]
