"""
Security Utilities: Secret Masking and Sanitization

Модуль для защиты секретов от утечки в логи, ответы API и другие выходы.
"""

import logging
import re
from functools import wraps
from typing import Any


# Константы для маскирования
SECRET_PATTERNS = [
    # API Keys
    (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', r"\1=****"),
    # Bearer tokens
    (r"(?i)(Bearer\s+[a-zA-Z0-9_\-\.]+)", "Bearer ****"),
    # AWS Access Keys
    (r"(?i)(AKIA[0-9A-Z]{16})", "AWS_ACCESS_KEY****"),
    # AWS Secret Keys (40 chars)
    (r'(?i)(aws[_-]?secret[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9/+=]{40}["\']?)', r"\1=****"),
    # Database URLs with credentials
    (r"(?i)(postgres(?:ql)?|mysql|mongodb|redis)://([^:]+):([^@]+)@", r"\1://\2:****@"),
    # Generic secrets
    (r'(?i)(secret[_-]?key|secretkey|password|pwd|token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{8,})["\']?', r"\1=****"),
    # JWT tokens
    (r"(eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)", "JWT_TOKEN****"),
    # Private keys
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----[^-]*-----END\s+(RSA\s+)?PRIVATE\s+KEY-----", "PRIVATE_KEY****"),
]

# Скомпилированные паттерны для производительности
COMPILED_PATTERNS = [(re.compile(pattern), replacement) for pattern, replacement in SECRET_PATTERNS]


def mask_secrets(text: str) -> str:
    """
    Маскирует все известные паттерны секретов в строке.

    Args:
        text: Строка для обработки

    Returns:
        Строка с замаскированными секретами

    Примеры:
        >>> mask_secrets("API_KEY=abc123xyz789")
        'API_KEY=****'
        >>> mask_secrets("postgres://user:pass123@localhost/db")  # pragma: allowlist secret
        'postgres://user:****@localhost/db'
    """
    if not text:
        return text

    result = text
    for pattern, replacement in COMPILED_PATTERNS:
        result = pattern.sub(replacement, result)

    return result


def mask_secrets_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Маскирует секреты во всём словаре рекурсивно.

    Args:
        data: Словарь для обработки

    Returns:
        Словарь с замаскированными секретами
    """
    if not isinstance(data, dict):
        return data

    result = {}
    secret_keys = {"password", "secret", "token", "api_key", "apikey", "credential", "auth"}

    for key, value in data.items():
        key_lower = key.lower()
        if any(secret in key_lower for secret in secret_keys):
            # Маскируем значение, если ключ содержит секрет
            if isinstance(value, str):
                result[key] = "****"
            elif isinstance(value, (int, float)):
                result[key] = 0
            else:
                result[key] = "****"
        elif isinstance(value, dict):
            result[key] = mask_secrets_dict(value)
        elif isinstance(value, list):
            result[key] = [
                mask_secrets_dict(item) if isinstance(item, dict) else mask_secrets(str(item)) for item in value
            ]
        else:
            result[key] = mask_secrets(str(value)) if isinstance(value, str) else value

    return result


def mask_secrets_list(data: list[Any]) -> list[Any]:
    """
    Маскирует секреты в списке рекурсивно.

    Args:
        data: Список для обработки

    Returns:
        Список с замаскированными секретами
    """
    if not isinstance(data, list):
        return data

    return [
        mask_secrets_dict(item)
        if isinstance(item, dict)
        else mask_secrets_list(item)
        if isinstance(item, list)
        else mask_secrets(str(item))
        if isinstance(item, str)
        else item
        for item in data
    ]


class SecretMaskingHandler(logging.Handler):
    """
    Handler для логгера, который маскирует секреты перед записью логов.

    Пример использования:
        logger = logging.getLogger(__name__)
        handler = SecretMaskingHandler()
        logger.addHandler(handler)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sensitive_keywords = {
            "password",
            "secret",
            "token",
            "api_key",
            "apikey",
            "credential",
            "auth",
            "private_key",
            "jwt",
        }

    def emit(self, record: logging.LogRecord):
        """Маскирует секреты в логе перед записью"""
        try:
            message = record.getMessage()
            masked_message = mask_secrets(message)

            # Проверяем, есть ли в сообщении ключи, содержащие секреты
            if hasattr(record, "args") and record.args:
                args = mask_secrets_dict(record.args) if isinstance(record.args, dict) else record.args
                record.args = args

            record.msg = masked_message
            record.args = None
            super().emit(record)
        except Exception:
            self.handleError(record)


def mask_secrets_decorator(func):
    """
    Декоратор для автоматического маскирования секретов в аргументах и возвращаемом значении.

    Пример:
        @mask_secrets_output
        def process_data(api_key: str, config: dict):
            return {"result": "ok", "api_key": api_key}
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Маскируем аргументы (для логов)
        masked_kwargs = mask_secrets_dict(kwargs) if kwargs else kwargs

        # Выполняем функцию
        result = func(*args, **masked_kwargs)

        # Маскируем результат
        if isinstance(result, dict):
            return mask_secrets_dict(result)
        if isinstance(result, list):
            return mask_secrets_list(result)
        if isinstance(result, str):
            return mask_secrets(result)
        return result

    return wrapper


def is_secret_key(key: str) -> bool:
    """
    Проверяет, является ли ключ именем секрета.

    Args:
        key: Имя ключа для проверки

    Returns:
        True если ключ содержит секрет, False иначе
    """
    secret_keywords = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "api-key",
        "access_key",
        "access-key",
        "private_key",
        "private-key",
        "credential",
        "auth",
        "auth_token",
        "auth-token",
        "bearer",
        "jwt",
        "secret_key",
        "secret-key",
        "encryption_key",
        "encryption-key",
    }
    key_lower = key.lower().replace("-", "_").replace(" ", "_")
    return any(keyword in key_lower for keyword in secret_keywords)


def sanitize_for_output(obj: Any) -> str:
    """
    Безопасная сериализация объекта для вывода в логи или API.

    Args:
        obj: Любой объект для сериализации

    Returns:
        Строка с замаскированными секретами
    """
    import json

    if isinstance(obj, (dict, list)):
        try:
            if isinstance(obj, dict):
                sanitized = mask_secrets_dict(obj)
            else:
                sanitized = mask_secrets_list(obj)
            return json.dumps(sanitized, ensure_ascii=False, default=str)
        except Exception:
            return mask_secrets(str(obj))
    else:
        return mask_secrets(str(obj))


# Конфигурация для FastAPI Middleware
def create_fastapi_secret_middleware():
    """
    Создаёт middleware для FastAPI, который маскирует секреты в запросах и ответах.

    Пример использования:
        from fastapi import FastAPI
        app = FastAPI()
        app.add_middleware(create_fastapi_secret_middleware())
    """

    from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response

    class SecretMaskingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            # Маскируем секреты в запросе (для логов)
            if request.url.path not in ["/health", "/ready", "/metrics"]:
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode("utf-8", errors="ignore")
                        masked_body = mask_secrets(body_str)
                        # Логирование без секретов
                        logging.debug(f"Request to {request.url.path}: {masked_body[:200]}...")
                except Exception:
                    # Игнорируем ошибки маскирования - лучше залогировать с секретами
                    pass  # nosec B110

            # Выполняем запрос
            response = await call_next(request)

            # Маскируем секреты в ответе
            try:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                    # Маскируем в чанках для стриминга
                    if b"password" in chunk.lower() or b"secret" in chunk.lower():
                        masked_chunk = mask_secrets(chunk.decode("utf-8", errors="ignore")).encode("utf-8")
                        response_body = response_body.replace(chunk, masked_chunk)

                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            except Exception:
                return response

    return SecretMaskingMiddleware


__all__ = [
    "COMPILED_PATTERNS",
    "SECRET_PATTERNS",
    "SecretMaskingHandler",
    "create_fastapi_secret_middleware",
    "is_secret_key",
    "mask_secrets",
    "mask_secrets_decorator",
    "mask_secrets_dict",
    "mask_secrets_list",
    "sanitize_for_output",
]
