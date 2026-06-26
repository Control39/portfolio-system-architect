"""Маскирование секретов для безопасного логирования и вывода."""

import logging
import re
from typing import Any

# Шаблоны для обнаружения секретов
SECRET_PATTERNS = {
    "api_key": re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?'),
    "bearer_token": re.compile(r"(?i)bearer\s+[a-zA-Z0-9_-]+"),
    "password": re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^\s"\']+?["\']?'),
    "secret": re.compile(r'(?i)(secret|secret_key)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{10,}["\']?'),
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY-----"),
    "database_url": re.compile(r'(?i)(postgres(?:ql)?|mysql|mongodb|redis)://[^\s"\'<>]+'),
    "jwt_token": re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
}

MASK_VALUE = "***"


def mask_string(value: str) -> str:
    """
    Маскирование секретов в строке.

    Args:
        value: Строка для обработки

    Returns:
        Строка с замаскированными секретами
    """
    result = value
    for _pattern_name, pattern in SECRET_PATTERNS.items():
        result = pattern.sub(MASK_VALUE, result)
    return result


def mask_dict(data: dict[str, Any], keys_to_mask: list[str] | None = None) -> dict[str, Any]:
    """
    Маскирование секретов в словаре.

    Args:
        data: Словарь для обработки
        keys_to_mask: Список ключей для маскирования (если None - автоопределение)

    Returns:
        Словарь с замаскированными секретами
    """
    sensitive_keys = keys_to_mask or [
        "api_key",
        "apikey",
        "password",
        "secret",
        "token",
        "auth",
        "private_key",
        "connection_string",
        "database_url",
    ]

    result: dict[str, Any] = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            result[key] = MASK_VALUE  # type: ignore
        elif isinstance(value, dict):
            result[key] = mask_dict(value, keys_to_mask)
        elif isinstance(value, str):
            result[key] = mask_string(value)
        else:
            result[key] = value
    return result


def mask_sensitive(value: Any) -> Any:
    """
    Универсальная функция маскирования секретов.

    Args:
        value: Любое значение (строка, словарь, список)

    Returns:
        Значение с замаскированными секретами
    """
    if isinstance(value, str):
        return mask_string(value)
    if isinstance(value, dict):
        return mask_dict(value)
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    return value


class SecretMaskingHandler(logging.Handler):
    """
    Логгер, автоматически маскирующий секреты.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        try:
            message = record.getMessage()
            masked_message = mask_string(message)
            record.msg = masked_message
            if record.args:
                try:
                    record.args = tuple(mask_sensitive(str(arg)) for arg in record.args)
                except Exception:
                    # При ошибке приведения к строке пропускаем маскирование аргументов
                    # чтобы избежать раскрытия чувствительных данных через repr()
                    logger = logging.getLogger(__name__)
                    logger.warning("Failed to mask log arguments, skipping masking for safety")
                    record.args = tuple(mask_sensitive(arg) for arg in record.args)
            super().emit(record)
        except Exception:
            self.handleError(record)


# Глобальный экземпляр маскирующего логгера
def get_masking_logger(name: str = "masked_logger") -> logging.Logger:
    """
    Получить логгер с маскированием секретов.

    Args:
        name: Имя логгера

    Returns:
        Logger с маскированием
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = SecretMaskingHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
