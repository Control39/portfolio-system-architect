"""Auth Service Module
"""

from .main import app, create_token, verify_token

# Re-export main app and functions for easier import
__all__ = ["app", "create_token", "verify_token"]
