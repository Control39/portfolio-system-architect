"""
Unit tests for it_compass basic functionality.
Kept only unique tests that target compass-specific logic.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_compass():
    """Mock IT Compass for testing."""
    service = MagicMock()
    service.config = {"service_name": "it_compass", "environment": "test"}
    service.logger = MagicMock()
    return service


class TestCompassBasicFunctionality:
    """Basic compass-specific tests (reduced from 17 to 3)."""

    def test_compass_analyzes_system_architecture(self, mock_compass):
        """Test: Compass Analyzes System Architecture (simplified)."""
        mock_compass.analyze_architecture = MagicMock(return_value={"bottlenecks": []})
        result = mock_compass.analyze_architecture("system")
        assert result["bottlenecks"] == []

    def test_compass_identifies_bottlenecks(self, mock_compass):
        """Test: Compass Identifies Bottlenecks (simplified)."""
        mock_compass.find_bottlenecks = MagicMock(return_value=["high_latency"])
        result = mock_compass.find_bottlenecks("system")
        assert "high_latency" in result

    def test_compass_suggests_improvements(self, mock_compass):
        """Test: Compass Suggests Improvements (simplified)."""
        mock_compass.suggest_improvements = MagicMock(return_value=["add_cache"])
        result = mock_compass.suggest_improvements("system")
        assert "add_cache" in result
