"""Утилиты безопасности для предотвращения SSRF-атак."""

import re
import urllib.parse


def is_safe_url(url: str, allowed_hosts: set[str] | None = None) -> bool:
    """
    Проверяет URL на безопасность (защита от SSRF).

    Args:
        url: URL для проверки
        allowed_hosts: Множество разрешённых хостов (по умолчанию: localhost и внутренние домены)

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

    # Проверка схемы
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Неподдерживаемая схема URL: {parsed.scheme}. Разрешены только http/https"
        )

    # Проверка хоста
    if not parsed.hostname:
        raise ValueError("URL не содержит hostname")

    if parsed.hostname not in allowed_hosts:
        raise ValueError(
            f"SSRF protection: host '{parsed.hostname}' не разрешён. Доступные: {', '.join(allowed_hosts)}"
        )

    # Проверка порта (опционально, можно расширить)
    if parsed.port and parsed.port not in (80, 443, 8000, 8080, 5000, 3000):
        raise ValueError(f"Небезопасный порт: {parsed.port}")

    return True


def sanitize_error_message(error: Exception, url: str | None = None) -> str:
    """
    Санитизирует сообщение об ошибке, удаляя чувствительные данные.

    Args:
        error: Исключение для обработки
        url: URL, который использовался (будет удалён из сообщения)

    Returns:
        Безопасное сообщение об ошибке
    """
    message = str(error)

    # Удалить URL из сообщения
    if url:
        message = message.replace(url, "[URL_REDACTED]")

    # Удалить токены и ключи
    patterns = [
        r"(Bearer\s+)[\w\-_.]+",  # Bearer токены
        r"(api[_-]?key|token|secret|password)[\s]*[=:][\s]*['\"]?[\w\-_.]+['\"]?",  # Ключи API
        r"https?://[^\s]+",  # URL в тексте ошибки
    ]

    for pattern in patterns:
        message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)

    return message
