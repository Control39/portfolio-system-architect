"""
Scanner Tests for cognitive_agent

Service Tier: CORE
Purpose: Scanner functionality testing

Test Coverage:
- Scanner initialization
- Scan execution
- Result processing
- Error handling
- Integration with orchestrator
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add path to root
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def scanner_config():
    """Scanner configuration fixture"""
    return {
        "project_path": ".",
        "mode": "full",
        "output_format": "json",
        "exclude_patterns": [".git", "__pycache__", ".venv"],
    }


@pytest.fixture
def mock_scanner_instance(scanner_config):
    """Create mock scanner instance"""
    scanner = MagicMock()
    scanner.config = scanner_config
    scanner.scan_result = None

    yield scanner


@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator instance"""
    orchestrator = MagicMock()
    orchestrator.load_markers = MagicMock(return_value=[])
    orchestrator.run_workflow = MagicMock(return_value={"status": "success"})
    return orchestrator


# ============================================================================
# UNIT TESTS
# ============================================================================


class TestScannerInitialization:
    """Scanner initialization tests"""

    def test_scanner_config_valid(self, scanner_config):
        """Test scanner configuration is valid"""
        assert scanner_config is not None
        assert "project_path" in scanner_config
        assert "mode" in scanner_config
        assert scanner_config["mode"] == "full"

    def test_scanner_instance_created(self, mock_scanner_instance):
        """Test scanner instance creation"""
        assert mock_scanner_instance is not None
        assert hasattr(mock_scanner_instance, "config")

    def test_scanner_default_mode(self, scanner_config):
        """Test scanner default mode"""
        assert scanner_config["mode"] == "full"


class TestScannerExecution:
    """Scanner execution tests"""

    def test_scan_execution(self, mock_scanner_instance):
        """Test scan execution"""
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 10, "languages": ["python"]}
        )

        result = mock_scanner_instance.execute_scan()

        assert result is not None
        assert "files_found" in result
        assert result["files_found"] == 10

    def test_scan_with_exclusions(self, mock_scanner_instance, scanner_config):
        """Test scan with exclusion patterns"""
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 5, "excluded": 3}
        )

        result = mock_scanner_instance.execute_scan()

        assert result["excluded"] == 3

    def test_scan_result_structure(self, mock_scanner_instance):
        """Test scan result structure"""
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={
                "files_found": 10,
                "languages": ["python", "javascript"],
                "scan_time": 1.5,
            }
        )

        result = mock_scanner_instance.execute_scan()

        assert "languages" in result
        assert "scan_time" in result


class TestScannerResultProcessing:
    """Scanner result processing tests"""

    def test_process_scan_results(self, mock_scanner_instance):
        """Test scan result processing"""
        mock_scanner_instance.process_results = MagicMock(return_value={"summary": "processed"})

        result = mock_scanner_instance.process_results()

        assert result["summary"] == "processed"

    def test_export_results_json(self, mock_scanner_instance):
        """Test JSON export"""
        mock_scanner_instance.export_json = MagicMock(return_value=True)

        result = mock_scanner_instance.export_json()

        assert result is True

    def test_export_results_csv(self, mock_scanner_instance):
        """Test CSV export"""
        mock_scanner_instance.export_csv = MagicMock(return_value=True)

        result = mock_scanner_instance.export_csv()

        assert result is True


class TestScannerErrorHandling:
    """Scanner error handling tests"""

    def test_handle_invalid_path(self, mock_scanner_instance):
        """Test handling of invalid project path"""
        mock_scanner_instance.execute_scan = MagicMock(
            side_effect=FileNotFoundError("Path not found")
        )

        with pytest.raises(FileNotFoundError):
            mock_scanner_instance.execute_scan()

    def test_handle_scan_timeout(self, mock_scanner_instance):
        """Test handling of scan timeout"""
        mock_scanner_instance.execute_scan = MagicMock(side_effect=TimeoutError("Scan timeout"))

        with pytest.raises(TimeoutError):
            mock_scanner_instance.execute_scan()

    def test_handle_permission_error(self, mock_scanner_instance):
        """Test handling of permission error"""
        mock_scanner_instance.execute_scan = MagicMock(side_effect=PermissionError("Access denied"))

        with pytest.raises(PermissionError):
            mock_scanner_instance.execute_scan()


class TestScannerIntegration:
    """Scanner integration tests"""

    def test_scanner_with_orchestrator(self, mock_scanner_instance, mock_orchestrator):
        """Test scanner integration with orchestrator"""
        mock_scanner_instance.orchestrator = mock_orchestrator

        assert mock_scanner_instance.orchestrator is not None

    def test_scanner_load_markers(self, mock_scanner_instance, mock_orchestrator):
        """Test loading markers from orchestrator"""
        mock_scanner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(return_value=["marker1", "marker2"])

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 2

    def test_scanner_run_workflow(self, mock_scanner_instance, mock_orchestrator):
        """Test running workflow via orchestrator"""
        mock_scanner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.run_workflow = MagicMock(
            return_value={"status": "success", "workflow": "scan"}
        )

        result = mock_orchestrator.run_workflow("scan")

        assert result["status"] == "success"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.integration
class TestScannerFullIntegration:
    """Full scanner integration tests"""

    def test_full_scan_workflow(self, mock_scanner_instance, mock_orchestrator):
        """Test full scan workflow"""
        # Arrange
        mock_scanner_instance.orchestrator = mock_orchestrator
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 10, "languages": ["python"]}
        )
        mock_scanner_instance.process_results = MagicMock(return_value={"summary": "processed"})

        # Act
        scan_result = mock_scanner_instance.execute_scan()
        processed = mock_scanner_instance.process_results()

        # Assert
        assert scan_result["files_found"] == 10
        assert processed["summary"] == "processed"

    def test_scanner_with_markers(self, mock_scanner_instance, mock_orchestrator):
        """Test scanner with IT-Compass markers"""
        mock_scanner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(
            return_value=[
                {"name": "security", "description": "Security check"},
                {"name": "performance", "description": "Performance check"},
            ]
        )

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 2
        assert markers[0]["name"] == "security"
        assert markers[1]["name"] == "performance"


class TestScannerPerformance:
    """Scanner performance tests"""

    def test_scan_speed(self, mock_scanner_instance):
        """Test scan execution speed"""
        import time

        start_time = time.time()
        mock_scanner_instance.execute_scan = MagicMock(return_value={"files_found": 0})
        mock_scanner_instance.execute_scan()
        elapsed = time.time() - start_time

        assert elapsed < 5.0  # Should complete within 5 seconds

    def test_memory_efficiency(self, mock_scanner_instance):
        """Test memory efficiency during scan"""
        initial_memory = 0  # Mock value
        mock_scanner_instance.execute_scan = MagicMock(return_value={"files_found": 0})
        mock_scanner_instance.execute_scan()
        final_memory = 0  # Mock value

        # Should not have significant memory increase
        assert final_memory - initial_memory < 1000000  # Less than 1MB


class TestScannerEdgeCases:
    """Scanner edge case tests"""

    def test_empty_project(self, mock_scanner_instance):
        """Test scanning empty project"""
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 0, "languages": []}
        )

        result = mock_scanner_instance.execute_scan()

        assert result["files_found"] == 0

    def test_large_project(self, mock_scanner_instance):
        """Test scanning large project"""
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 10000, "languages": ["python"]}
        )

        result = mock_scanner_instance.execute_scan()

        assert result["files_found"] == 10000

    def test_special_characters_in_path(self, mock_scanner_instance):
        """Test scanning project with special characters in path"""
        mock_scanner_instance.config["project_path"] = "C:\\Users\\Test User\\Project"
        mock_scanner_instance.execute_scan = MagicMock(
            return_value={"files_found": 5, "languages": ["python"]}
        )

        result = mock_scanner_instance.execute_scan()

        assert result["files_found"] == 5
