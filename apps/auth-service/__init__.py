"""
Package initialization for auth-service.
This file makes Python treat the directories as packages.
"""

# Re-export application instance
from .auth_service.auth_service import app, get_app

__all__ = ["app", "get_app"]