"""Утилиты безопасности для Portfolio Organizer."""
import re
import urllib.parse
from typing import Set


def is_safe_url(url: str, allowed_hosts: Set[str] | None = None) -> bool:
    """
    Проверяет URL на безопасность (защита от SSRF).

    Args:
        url: URL для проверки
        allowed_hosts: Множество разрешённых хостов

    Returns:
        True если URL безопасен, False иначе

    Raises:
        ValueError: Если URL небезопасен
    """
    if not allowed_hosts:
        allowed_hosts = {
            "localhost",
            "127.0.0.1",
            "::1",
        }

    if not url:
        raise ValueError("URL не может быть пустым")

    parsed = urllib.parse.urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Неподдерживаемая схема URL: {parsed.scheme}")

    if not parsed.hostname:
        raise ValueError("URL не содержит hostname")

    if parsed.hostname not in allowed_hosts:
        raise ValueError(
            f"SSRF protection: host '{parsed.hostname}' не разрешён. "
            f"Доступные: {', '.join(allowed_hosts)}"
        )

    return True


def sanitize_error_message(error: Exception, url: str | None = None) -> str:
    """Санитизирует сообщение об ошибке, удаляя чувствительные данные."""
    message = str(error)

    if url:
        message = message.replace(url, "[URL_REDACTED]")

    patterns = [
        r"(Bearer\s+)[\w\-_.]+",
        r"(api[_-]?key|token|secret|password)[\s]*[=:][\s]*['\"]?[\w\-_.]+['\"]?",
        r"https?://[^\s]+",
    ]

    for pattern in patterns:
        message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)

    return message