
import numpy as np
import requests


class CodeEmbedder:
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def embed(self, text: str) -> list[float]:
        """Получить эмбеддинг для текста/кода"""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text[:2000],  # ограничиваем длину
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Ошибка при получении эмбеддинга: {e}")
            return []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Эмбеддинги для пачки текстов"""
        results = []
        for text in texts:
            embedding = self.embed(text)
            if embedding:
                results.append(embedding)
        return results

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Вычислить косинусное сходство между двумя эмбеддингами"""
        if not embedding1 or not embedding2:
            return 0.0

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
