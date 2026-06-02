import tiktoken
from typing import Dict


class TokenCounter:
    """Оценка количества токенов для разных LLM"""

    ENCODERS = {
        "gpt-4": "cl100k_base",
        "gpt-3.5": "cl100k_base",
        "deepseek": "cl100k_base",
        "claude": "cl100k_base",
        "llama": "p50k_base",
    }

    def __init__(self, model: str = "deepseek"):
        encoder_name = self.ENCODERS.get(model, "cl100k_base")
        try:
            self.encoder = tiktoken.get_encoding(encoder_name)
            self.has_tiktoken = True
        except Exception:
            self.has_tiktoken = False
            self.encoder = None

    def count(self, text: str) -> int:
        """Точный подсчёт токенов"""
        if self.has_tiktoken and self.encoder:
            return len(self.encoder.encode(text))
        # Грубая оценка: ~3 символа на токен для русского/английского
        return len(text) // 3

    def estimate_for_text(self, text: str) -> Dict:
        """Оценка для разных моделей"""
        exact = self.count(text)
        return {
            "exact_tokens": exact,
            "approx_chars": len(text),
            "approx_ratio": round(len(text) / exact, 2) if exact > 0 else 0,
            "warning": ">128K" if exact > 128000 else (">32K" if exact > 32000 else None),
        }
