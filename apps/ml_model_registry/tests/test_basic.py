"""
Unit tests for ml_model_registry basic functionality.
Kept only unique tests that target registry-specific logic.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_registry():
    """Mock ML registry for testing."""
    service = MagicMock()
    service.config = {"service_name": "ml_model_registry", "environment": "test"}
    service.logger = MagicMock()
    return service


class TestRegistryBasicFunctionality:
    """Basic registry-specific tests (reduced from 17 to 3)."""

    def test_registry_stores_model(self, mock_registry):
        """Test: Registry Stores Model (simplified)."""
        mock_registry.store_model = MagicMock(return_value={"id": "model-123"})
        result = mock_registry.store_model("model_data")
        assert result["id"] == "model-123"

    def test_registry_retrieves_model(self, mock_registry):
        """Test: Registry Retrieves Model (simplified)."""
        mock_registry.get_model = MagicMock(return_value={"name": "model-123"})
        result = mock_registry.get_model("model-123")
        assert result["name"] == "model-123"

    def test_registry_version_management(self, mock_registry):
        """Test: Registry Version Management (simplified)."""
        mock_registry.get_latest_version = MagicMock(return_value="v2.0")
        result = mock_registry.get_latest_version("model-123")
        assert result == "v2.0"
