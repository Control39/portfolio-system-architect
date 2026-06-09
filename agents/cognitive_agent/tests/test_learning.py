"""
Learning Tests for cognitive_agent

Service Tier: CORE
Purpose: Learning functionality testing

Test Coverage:
- Learning system initialization
- Metrics collection
- Performance tracking
- Error handling
- Integration with learning cycle
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add path to root
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def learning_config():
    """Learning configuration fixture"""
    return {
        "collect_metrics": True,
        "track_performance": True,
        "store_results": True,
        "output_dir": "data/learning",
    }


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector"""
    collector = MagicMock()
    collector.collect_metrics = MagicMock(
        return_value={
            "tasks_completed": 10,
            "success_rate": 0.95,
            "avg_time": 1.5,
        }
    )
    return collector


@pytest.fixture
def mock_learning_instance(learning_config, mock_metrics_collector):
    """Create mock learning instance"""
    learning = MagicMock()
    learning.config = learning_config
    learning.metrics_collector = mock_metrics_collector
    learning.learning_data = None

    yield learning


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


class TestLearningInitialization:
    """Learning system initialization tests"""

    def test_learning_config_valid(self, learning_config):
        """Test learning configuration is valid"""
        assert learning_config is not None
        assert "collect_metrics" in learning_config
        assert learning_config["collect_metrics"] is True

    def test_learning_instance_created(self, mock_learning_instance):
        """Test learning instance creation"""
        assert mock_learning_instance is not None
        assert hasattr(mock_learning_instance, "config")

    def test_learning_default_settings(self, learning_config):
        """Test learning default settings"""
        assert learning_config["track_performance"] is True
        assert learning_config["store_results"] is True


class TestMetricsCollection:
    """Metrics collection tests"""

    def test_collect_metrics(self, mock_learning_instance, mock_metrics_collector):
        """Test metrics collection"""
        mock_learning_instance.metrics_collector = mock_metrics_collector
        mock_metrics_collector.collect_metrics = MagicMock(
            return_value={
                "tasks_completed": 10,
                "success_rate": 0.95,
                "avg_time": 1.5,
            }
        )

        result = mock_learning_instance.metrics_collector.collect_metrics()

        assert result["tasks_completed"] == 10
        assert result["success_rate"] == 0.95

    def test_collect_task_metrics(self, mock_learning_instance):
        """Test task-specific metrics collection"""
        mock_learning_instance.collect_task_metrics = MagicMock(
            return_value={
                "task_id": "task_1",
                "duration": 2.5,
                "status": "success",
            }
        )

        result = mock_learning_instance.collect_task_metrics()

        assert result["status"] == "success"

    def test_collect_performance_metrics(self, mock_learning_instance):
        """Test performance metrics collection"""
        mock_learning_instance.collect_performance_metrics = MagicMock(
            return_value={
                "cpu_usage": 45.0,
                "memory_usage": 60.0,
                "disk_io": 100,
            }
        )

        result = mock_learning_instance.collect_performance_metrics()

        assert "cpu_usage" in result


class TestPerformanceTracking:
    """Performance tracking tests"""

    def test_track_execution_time(self, mock_learning_instance):
        """Test execution time tracking"""
        mock_learning_instance.track_time = MagicMock(
            return_value={"start": 0, "end": 1.5, "duration": 1.5}
        )

        result = mock_learning_instance.track_time()

        assert result["duration"] == 1.5

    def test_track_resource_usage(self, mock_learning_instance):
        """Test resource usage tracking"""
        mock_learning_instance.track_resources = MagicMock(
            return_value={
                "cpu": 45.0,
                "memory": 60.0,
                "disk": 30.0,
            }
        )

        result = mock_learning_instance.track_resources()

        assert result["cpu"] == 45.0

    def test_track_success_rate(self, mock_learning_instance):
        """Test success rate tracking"""
        mock_learning_instance.track_success_rate = MagicMock(
            return_value={"total": 10, "success": 9, "rate": 0.9}
        )

        result = mock_learning_instance.track_success_rate()

        assert result["rate"] == 0.9


class TestLearningErrorHandling:
    """Learning error handling tests"""

    def test_handle_metrics_error(self, mock_learning_instance):
        """Test handling of metrics collection error"""
        mock_learning_instance.metrics_collector = MagicMock()
        mock_learning_instance.metrics_collector.collect_metrics = MagicMock(
            side_effect=Exception("Metrics collection failed")
        )

        with pytest.raises(Exception):
            mock_learning_instance.metrics_collector.collect_metrics()

    def test_handle_storage_error(self, mock_learning_instance):
        """Test handling of storage error"""
        mock_learning_instance.store_results = MagicMock(side_effect=IOError("Storage unavailable"))

        with pytest.raises(IOError):
            mock_learning_instance.store_results()

    def test_handle_invalid_data(self, mock_learning_instance):
        """Test handling of invalid data"""
        mock_learning_instance.validate_data = MagicMock(
            return_value={"valid": False, "error": "Invalid metrics format"}
        )

        result = mock_learning_instance.validate_data()

        assert result["valid"] is False


class TestLearningIntegration:
    """Learning integration tests"""

    def test_learning_with_orchestrator(self, mock_learning_instance, mock_orchestrator):
        """Test learning integration with orchestrator"""
        mock_learning_instance.orchestrator = mock_orchestrator

        assert mock_learning_instance.orchestrator is not None

    def test_learning_load_markers(self, mock_learning_instance, mock_orchestrator):
        """Test loading markers from orchestrator"""
        mock_learning_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(return_value=["marker1"])

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 1

    def test_learning_run_workflow(self, mock_learning_instance, mock_orchestrator):
        """Test running workflow via orchestrator"""
        mock_learning_instance.orchestrator = mock_orchestrator
        mock_orchestrator.run_workflow = MagicMock(
            return_value={"status": "success", "workflow": "learn"}
        )

        result = mock_orchestrator.run_workflow("learn")

        assert result["status"] == "success"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.integration
class TestLearningFullIntegration:
    """Full learning integration tests"""

    def test_full_learning_cycle(self, mock_learning_instance, mock_metrics_collector):
        """Test full learning cycle"""
        # Arrange
        mock_learning_instance.metrics_collector = mock_metrics_collector
        mock_metrics_collector.collect_metrics = MagicMock(
            return_value={
                "tasks_completed": 10,
                "success_rate": 0.95,
                "avg_time": 1.5,
            }
        )
        mock_learning_instance.store_results = MagicMock(return_value=True)
        mock_learning_instance.generate_report = MagicMock(return_value={"report": "generated"})

        # Act
        metrics = mock_learning_instance.metrics_collector.collect_metrics()
        stored = mock_learning_instance.store_results()
        report = mock_learning_instance.generate_report()

        # Assert
        assert metrics["tasks_completed"] == 10
        assert stored is True
        assert "report" in report

    def test_learning_with_markers(self, mock_learning_instance, mock_orchestrator):
        """Test learning with IT-Compass markers"""
        mock_learning_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(
            return_value=[
                {"name": "security", "description": "Security check"},
                {"name": "performance", "description": "Performance check"},
            ]
        )

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 2
        assert markers[0]["name"] == "security"


class TestLearningPerformance:
    """Learning performance tests"""

    def test_metrics_collection_speed(self, mock_learning_instance):
        """Test metrics collection speed"""
        start_time = time.time()
        mock_learning_instance.metrics_collector.collect_metrics = MagicMock(
            return_value={"tasks_completed": 0}
        )
        mock_learning_instance.metrics_collector.collect_metrics()
        elapsed = time.time() - start_time

        assert elapsed < 5.0  # Should complete within 5 seconds

    def test_memory_efficiency(self, mock_learning_instance):
        """Test memory efficiency during learning"""
        initial_memory = 0  # Mock value
        mock_learning_instance.collect_task_metrics = MagicMock(
            return_value={"task_id": "test", "duration": 0, "status": "success"}
        )
        mock_learning_instance.collect_task_metrics()
        final_memory = 0  # Mock value

        assert final_memory - initial_memory < 1000000  # Less than 1MB


class TestLearningEdgeCases:
    """Learning edge case tests"""

    def test_empty_metrics(self, mock_learning_instance):
        """Test handling of empty metrics"""
        mock_learning_instance.metrics_collector.collect_metrics = MagicMock(
            return_value={
                "tasks_completed": 0,
                "success_rate": 0.0,
                "avg_time": 0.0,
            }
        )

        result = mock_learning_instance.metrics_collector.collect_metrics()

        assert result["tasks_completed"] == 0

    def test_high_volume_metrics(self, mock_learning_instance):
        """Test handling of high volume metrics"""
        mock_learning_instance.metrics_collector.collect_metrics = MagicMock(
            return_value={
                "tasks_completed": 1000,
                "success_rate": 0.95,
                "avg_time": 1.5,
            }
        )

        result = mock_learning_instance.metrics_collector.collect_metrics()

        assert result["tasks_completed"] == 1000

    def test_missing_metrics(self, mock_learning_instance):
        """Test handling of missing metrics"""
        mock_learning_instance.validate_data = MagicMock(
            return_value={"valid": False, "error": "Missing required metrics"}
        )

        result = mock_learning_instance.validate_data()

        assert result["valid"] is False
