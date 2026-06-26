"""
Инициализация модуля безопасности для Cognitive Agent
"""

from .guardrails import EnterpriseGuardrails, GuardrailDecorator, GuardrailRule, SecurityLevel
from .rate_limiter import (
    PredefinedRateLimiters,
    RateLimitConfig,
    RateLimiter,
    RateLimitExceededError,
    RateLimitStrategy,
    rate_limited,
)
from .secret_manager import (
    SecretManager,
    SecretManagerError,
    SecretNotFoundError,
    decrypt_secret,
    encrypt_secret,
    get_secret_manager,
)
from .secure_path import PathSecurityError, SecurePath, is_path_within_base, safe_path_join

__all__ = [
    # Guardrails
    "SecurityLevel",
    "GuardrailRule",
    "EnterpriseGuardrails",
    "GuardrailDecorator",
    # Secure Path
    "SecurePath",
    "PathSecurityError",
    "safe_path_join",
    "is_path_within_base",
    # Rate Limiter
    "RateLimiter",
    "RateLimitExceededError",
    "RateLimitConfig",
    "RateLimitStrategy",
    "PredefinedRateLimiters",
    "rate_limited",
    # Secret Manager
    "SecretManager",
    "SecretManagerError",
    "SecretNotFoundError",
    "get_secret_manager",
    "encrypt_secret",
    "decrypt_secret",
]
