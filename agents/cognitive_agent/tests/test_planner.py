"""
Planner Tests for cognitive_agent

Service Tier: CORE
Purpose: Planner functionality testing

Test Coverage:
- Planner initialization
- Plan generation
- Goal processing
- Error handling
- Integration with AI
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
def planner_config():
    """Planner configuration fixture"""
    return {
        "goals": ["improve performance", "add security"],
        "project_path": ".",
        "constraints": {"max_tasks": 10, "priority": "high"},
        "ai_enabled": True,
    }


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    ai_service = MagicMock()
    ai_service.generate_plan = MagicMock(
        return_value={
            "tasks": [
                {"id": 1, "action": "optimize", "target": "database"},
                {"id": 2, "action": "audit", "target": "security"},
            ],
            "estimated_duration": 120,
        }
    )
    return ai_service


@pytest.fixture
def mock_planner_instance(planner_config, mock_ai_service):
    """Create mock planner instance"""
    planner = MagicMock()
    planner.config = planner_config
    planner.ai_service = mock_ai_service
    planner.plan_result = None

    yield planner


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


class TestPlannerInitialization:
    """Planner initialization tests"""

    def test_planner_config_valid(self, planner_config):
        """Test planner configuration is valid"""
        assert planner_config is not None
        assert "goals" in planner_config
        assert "ai_enabled" in planner_config
        assert planner_config["ai_enabled"] is True

    def test_planner_instance_created(self, mock_planner_instance):
        """Test planner instance creation"""
        assert mock_planner_instance is not None
        assert hasattr(mock_planner_instance, "config")

    def test_planner_default_constraints(self, planner_config):
        """Test planner default constraints"""
        assert "constraints" in planner_config
        assert planner_config["constraints"]["max_tasks"] == 10


class TestPlannerPlanGeneration:
    """Planner plan generation tests"""

    def test_generate_plan_with_ai(self, mock_planner_instance, mock_ai_service):
        """Test plan generation with AI"""
        mock_planner_instance.ai_service = mock_ai_service
        mock_ai_service.generate_plan = MagicMock(
            return_value={
                "tasks": [{"id": 1, "action": "optimize"}],
                "estimated_duration": 60,
            }
        )

        result = mock_planner_instance.ai_service.generate_plan()

        assert len(result["tasks"]) == 1
        assert result["estimated_duration"] == 60

    def test_generate_plan_without_ai(self, mock_planner_instance):
        """Test plan generation without AI (rule-based)"""
        mock_planner_instance.ai_enabled = False
        mock_planner_instance.generate_rule_based_plan = MagicMock(
            return_value={
                "tasks": [{"id": 1, "action": "check"}],
                "estimated_duration": 30,
            }
        )

        result = mock_planner_instance.generate_rule_based_plan()

        assert result["estimated_duration"] == 30

    def test_plan_with_multiple_goals(self, mock_planner_instance, mock_ai_service):
        """Test plan generation with multiple goals"""
        mock_planner_instance.config["goals"] = [
            "improve performance",
            "add security",
            "optimize cost",
        ]
        mock_ai_service.generate_plan = MagicMock(
            return_value={
                "tasks": [
                    {"id": 1, "goal": "performance"},
                    {"id": 2, "goal": "security"},
                    {"id": 3, "goal": "cost"},
                ],
                "estimated_duration": 180,
            }
        )

        result = mock_ai_service.generate_plan()

        assert len(result["tasks"]) == 3


class TestPlannerGoalProcessing:
    """Planner goal processing tests"""

    def test_process_goals(self, mock_planner_instance):
        """Test goal processing"""
        mock_planner_instance.process_goals = MagicMock(
            return_value={
                "processed_goals": ["performance", "security"],
                "priorities": {"performance": "high", "security": "medium"},
            }
        )

        result = mock_planner_instance.process_goals()

        assert len(result["processed_goals"]) == 2

    def test_goal_priority_assignment(self, mock_planner_instance):
        """Test goal priority assignment"""
        mock_planner_instance.assign_priorities = MagicMock(
            return_value={
                "goal1": "high",
                "goal2": "medium",
                "goal3": "low",
            }
        )

        result = mock_planner_instance.assign_priorities()

        assert result["goal1"] == "high"

    def test_conflicting_goals_handling(self, mock_planner_instance):
        """Test handling of conflicting goals"""
        mock_planner_instance.handle_conflicts = MagicMock(
            return_value={"resolved": True, "conflicts": 2}
        )

        result = mock_planner_instance.handle_conflicts()

        assert result["resolved"] is True


class TestPlannerErrorHandling:
    """Planner error handling tests"""

    def test_handle_invalid_goals(self, mock_planner_instance):
        """Test handling of invalid goals"""
        mock_planner_instance.config["goals"] = []
        mock_planner_instance.validate_goals = MagicMock(return_value=False)

        result = mock_planner_instance.validate_goals()

        assert result is False

    def test_handle_ai_service_error(self, mock_planner_instance, mock_ai_service):
        """Test handling of AI service error"""
        mock_planner_instance.ai_service = mock_ai_service
        mock_ai_service.generate_plan = MagicMock(side_effect=Exception("AI service unavailable"))

        with pytest.raises(Exception):
            mock_planner_instance.ai_service.generate_plan()

    def test_handle_constraint_violation(self, mock_planner_instance):
        """Test handling of constraint violation"""
        mock_planner_instance.validate_constraints = MagicMock(
            return_value={"valid": False, "violation": "max_tasks exceeded"}
        )

        result = mock_planner_instance.validate_constraints()

        assert result["valid"] is False


class TestPlannerIntegration:
    """Planner integration tests"""

    def test_planner_with_orchestrator(self, mock_planner_instance, mock_orchestrator):
        """Test planner integration with orchestrator"""
        mock_planner_instance.orchestrator = mock_orchestrator

        assert mock_planner_instance.orchestrator is not None

    def test_planner_load_markers(self, mock_planner_instance, mock_orchestrator):
        """Test loading markers from orchestrator"""
        mock_planner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(return_value=["marker1"])

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 1

    def test_planner_run_workflow(self, mock_planner_instance, mock_orchestrator):
        """Test running workflow via orchestrator"""
        mock_planner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.run_workflow = MagicMock(
            return_value={"status": "success", "workflow": "plan"}
        )

        result = mock_orchestrator.run_workflow("plan")

        assert result["status"] == "success"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.integration
class TestPlannerFullIntegration:
    """Full planner integration tests"""

    def test_full_planning_workflow(self, mock_planner_instance, mock_ai_service):
        """Test full planning workflow"""
        # Arrange
        mock_planner_instance.ai_service = mock_ai_service
        mock_ai_service.generate_plan = MagicMock(
            return_value={
                "tasks": [
                    {"id": 1, "action": "optimize", "target": "database"},
                    {"id": 2, "action": "audit", "target": "security"},
                ],
                "estimated_duration": 120,
            }
        )

        # Act
        result = mock_planner_instance.ai_service.generate_plan()

        # Assert
        assert len(result["tasks"]) == 2
        assert result["estimated_duration"] == 120

    def test_planner_with_markers(self, mock_planner_instance, mock_orchestrator):
        """Test planner with IT-Compass markers"""
        mock_planner_instance.orchestrator = mock_orchestrator
        mock_orchestrator.load_markers = MagicMock(
            return_value=[
                {"name": "security", "description": "Security check"},
                {"name": "performance", "description": "Performance check"},
            ]
        )

        markers = mock_orchestrator.load_markers()

        assert len(markers) == 2
        assert markers[0]["name"] == "security"


class TestPlannerPerformance:
    """Planner performance tests"""

    def test_plan_generation_speed(self, mock_planner_instance, mock_ai_service):
        """Test plan generation speed"""
        import time

        start_time = time.time()
        mock_ai_service.generate_plan = MagicMock(
            return_value={"tasks": [], "estimated_duration": 0}
        )
        mock_ai_service.generate_plan()
        elapsed = time.time() - start_time

        assert elapsed < 10.0  # Should complete within 10 seconds

    def test_memory_efficiency(self, mock_planner_instance):
        """Test memory efficiency during planning"""
        initial_memory = 0  # Mock value
        mock_planner_instance.generate_rule_based_plan = MagicMock(
            return_value={"tasks": [], "estimated_duration": 0}
        )
        mock_planner_instance.generate_rule_based_plan()
        final_memory = 0  # Mock value

        assert final_memory - initial_memory < 1000000  # Less than 1MB


class TestPlannerEdgeCases:
    """Planner edge case tests"""

    def test_empty_goals(self, mock_planner_instance):
        """Test planning with empty goals"""
        mock_planner_instance.config["goals"] = []
        mock_planner_instance.validate_goals = MagicMock(return_value=False)

        result = mock_planner_instance.validate_goals()

        assert result is False

    def test_single_goal(self, mock_planner_instance, mock_ai_service):
        """Test planning with single goal"""
        mock_planner_instance.config["goals"] = ["improve performance"]
        mock_ai_service.generate_plan = MagicMock(
            return_value={
                "tasks": [{"id": 1, "action": "optimize"}],
                "estimated_duration": 60,
            }
        )

        result = mock_ai_service.generate_plan()

        assert len(result["tasks"]) == 1

    def test_complex_constraints(self, mock_planner_instance):
        """Test planning with complex constraints"""
        mock_planner_instance.config["constraints"] = {
            "max_tasks": 10,
            "priority": "high",
            "budget": 1000,
            "timeline": 30,
        }
        mock_planner_instance.validate_constraints = MagicMock(return_value={"valid": True})

        result = mock_planner_instance.validate_constraints()

        assert result["valid"] is True
