"""Module initialization for auth-service.
"""

from .main import app, create_token, verify_token

__all__ = ["app", "create_token", "verify_token"]
