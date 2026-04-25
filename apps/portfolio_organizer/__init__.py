"""Module initialization for portfolio_organizer.
"""

from .src.app import app
from .src.core.ITCompassAPI import ITCompassAPI
from .src.core.notification_service import NotificationService

# Ensure the module is treated as a package
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__all__ = ["ITCompassAPI", "NotificationService"]

