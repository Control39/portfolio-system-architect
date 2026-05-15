"""
Module initialization for auth-service.
Lazy imports to allow environment variables to be set before loading main.
"""


def __getattr__(name):
    """Lazy loading of main module components"""
    if name in ("app", "create_token", "verify_token"):
        from .main import app, create_token, verify_token

        return {"app": app, "create_token": create_token, "verify_token": verify_token}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app", "create_token", "verify_token"]
