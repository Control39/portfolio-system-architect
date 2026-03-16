import uuid
import re


def generate_id() -> str:
    """Генерирует UUID‑v4 в виде строки."""
    return str(uuid.uuid4())


def validate_evidence_link(url: str) -> bool:
    """Быстрая проверка, что ссылка выглядит как URL."""
    pattern = re.compile(r&#39;^https?://.+&#39;)
    return bool(pattern.match(url))

