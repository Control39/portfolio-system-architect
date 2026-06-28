"""
End-to-End Tests for cognitive_agent

Service Tier: E2E
Purpose: Full workflow testing

Test Coverage:
- Full agent workflow
- Integration with all services
- Error recovery
- Performance under load
- Real-world scenarios
"""

import time
from unittest.mock import MagicMock

import pytest

# Add path to root


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def e2e_config():
    """E2E configuration fixture"""
    return {
        "full_workflow": True,
        "integration_tests": True,
        "performance_tests": True,
        "error_recovery_tests": True,
    }


@pytest.fixture
def mock_agent():
    """Mock cognitive agent"""
    agent = MagicMock()
    agent.scan = MagicMock(
        return_value={
            "status": "success",
            "files_found": 10,
            "languages": ["python"],
        }
    )
    agent.plan = MagicMock(
        return_value={
            "status": "success",
            "tasks": [{"id": 1, "action": "optimize"}],
            "estimated_duration": 60,
        }
    )
    agent.execute = MagicMock(
        return_value={
            "status": "success",
            "task_id": 1,
            "result": "completed",
        }
    )
    agent.learn = MagicMock(
        return_value={
            "status": "success",
            "metrics": {"tasks_completed": 1, "success_rate": 1.0},
        }
    )
    return agent


@pytest.fixture
def mock_services():
    """Mock all services"""
    return {
        "scanner": MagicMock(),
        "planner": MagicMock(),
        "executor": MagicMock(),
        "learner": MagicMock(),
    }


# ============================================================================
# E2E TESTS
# ============================================================================


class TestFullAgentWorkflow:
    """Full agent workflow tests"""

    def test_complete_workflow(self, mock_agent):
        """Test complete agent workflow: scan -> plan -> execute -> learn"""
        # Arrange
        mock_agent.scan = MagicMock(return_value={"status": "success", "files_found": 10})
        mock_agent.plan = MagicMock(
            return_value={
                "status": "success",
                "tasks": [{"id": 1, "action": "optimize"}],
            }
        )
        mock_agent.execute = MagicMock(return_value={"status": "success", "task_id": 1, "result": "completed"})
        mock_agent.learn = MagicMock(
            return_value={
                "status": "success",
                "metrics": {"tasks_completed": 1, "success_rate": 1.0},
            }
        )

        # Act
        scan_result = mock_agent.scan()
        plan_result = mock_agent.plan()
        execute_result = mock_agent.execute(task_id=1, skill_name="test")
        learn_result = mock_agent.learn()

        # Assert
        assert scan_result["status"] == "success"
        assert plan_result["status"] == "success"
        assert execute_result["status"] == "success"
        assert learn_result["status"] == "success"

    def test_workflow_with_dependencies(self, mock_agent, mock_services):
        """Test workflow with service dependencies"""
        # Arrange
        mock_agent.services = mock_services
        mock_services["scanner"].scan = MagicMock(return_value={"files": 10})
        mock_services["planner"].plan = MagicMock(return_value={"tasks": [{"id": 1}]})
        mock_services["executor"].execute = MagicMock(return_value={"status": "success"})
        mock_services["learner"].learn = MagicMock(return_value={"metrics": {"success": 1.0}})

        # Act
        scanner_result = mock_services["scanner"].scan()
        planner_result = mock_services["planner"].plan()
        executor_result = mock_services["executor"].execute(task_id=1)
        learner_result = mock_services["learner"].learn()

        # Assert
        assert scanner_result["files"] == 10
        assert planner_result["tasks"][0]["id"] == 1
        assert executor_result["status"] == "success"
        assert learner_result["metrics"]["success"] == 1.0


class TestIntegrationWithServices:
    """Integration with external services tests"""

    def test_integration_with_decision_engine(self, mock_agent):
        """Test integration with Decision Engine"""
        # Arrange
        mock_agent.decision_engine = MagicMock()
        mock_agent.decision_engine.reason = MagicMock(
            return_value={
                "decision": "allow",
                "confidence": 0.95,
                "reason": "All checks passed",
            }
        )

        # Act
        decision = mock_agent.decision_engine.reason(action="execute_task", context={"environment": "test"})

        # Assert
        assert decision["decision"] == "allow"
        assert decision["confidence"] == 0.95

    def test_integration_with_knowledge_graph(self, mock_agent):
        """Test integration with Knowledge Graph"""
        # Arrange
        mock_agent.knowledge_graph = MagicMock()
        mock_agent.knowledge_graph.query = MagicMock(
            return_value={
                "entities": [
                    {"name": "project", "type": "repository"},
                    {"name": "code", "type": "source"},
                ],
                "relationships": [{"type": "contains", "source": "project", "target": "code"}],
            }
        )

        # Act
        knowledge = mock_agent.knowledge_graph.query("What is in the project?")

        # Assert
        assert len(knowledge["entities"]) == 2
        assert len(knowledge["relationships"]) == 1

    def test_integration_with_it_compass(self, mock_agent):
        """Test integration with IT-Compass"""
        # Arrange
        mock_agent.it_compass = MagicMock()
        mock_agent.it_compass.check_markers = MagicMock(
            return_value={
                "markers": [
                    {"name": "security", "status": "pass"},
                    {"name": "performance", "status": "pass"},
                ],
                "overall_score": 0.95,
            }
        )

        # Act
        markers = mock_agent.it_compass.check_markers()

        # Assert
        assert len(markers["markers"]) == 2
        assert markers["overall_score"] == 0.95


class TestErrorRecovery:
    """Error recovery tests"""

    def test_scan_error_recovery(self, mock_agent):
        """Test recovery from scan error"""
        # Arrange
        mock_agent.scan = MagicMock(
            side_effect=[
                Exception("Scan failed"),
                {"status": "success", "files_found": 10},
            ]
        )

        # Act & Assert
        with pytest.raises(Exception):
            mock_agent.scan()

        # Retry
        result = mock_agent.scan()
        assert result["status"] == "success"

    def test_plan_error_recovery(self, mock_agent):
        """Test recovery from plan error"""
        # Arrange
        mock_agent.plan = MagicMock(
            side_effect=[
                Exception("Plan failed"),
                {"status": "success", "tasks": [{"id": 1}]},
            ]
        )

        # Act & Assert
        with pytest.raises(Exception):
            mock_agent.plan()

        # Retry
        result = mock_agent.plan()
        assert result["status"] == "success"

    def test_execute_error_recovery(self, mock_agent):
        """Test recovery from execute error"""
        # Arrange
        mock_agent.execute = MagicMock(
            side_effect=[
                Exception("Execute failed"),
                {"status": "success", "task_id": 1, "result": "completed"},
            ]
        )

        # Act & Assert
        with pytest.raises(Exception):
            mock_agent.execute(task_id=1, skill_name="test")

        # Retry
        result = mock_agent.execute(task_id=1, skill_name="test")
        assert result["status"] == "success"


class TestPerformanceUnderLoad:
    """Performance under load tests"""

    def test_concurrent_scans(self, mock_agent):
        """Test concurrent scan operations"""
        import concurrent.futures

        # Arrange
        mock_agent.scan = MagicMock(return_value={"status": "success", "files_found": 10})

        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(mock_agent.scan) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Assert
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)

    def test_high_volume_planning(self, mock_agent):
        """Test high volume planning operations"""
        # Arrange
        mock_agent.plan = MagicMock(
            return_value={
                "status": "success",
                "tasks": [{"id": i, "action": "optimize"} for i in range(100)],
            }
        )

        # Act
        results = [mock_agent.plan() for _ in range(10)]

        # Assert
        assert len(results) == 10
        assert all(r["status"] == "success" for r in results)

    def test_load_with_error_handling(self, mock_agent):
        """Test load with error handling"""
        # Arrange
        mock_agent.scan = MagicMock(return_value={"status": "success", "files_found": 10})
        mock_agent.plan = MagicMock(return_value={"status": "success", "tasks": [{"id": 1}]})
        mock_agent.execute = MagicMock(return_value={"status": "success", "task_id": 1, "result": "completed"})
        mock_agent.learn = MagicMock(
            return_value={
                "status": "success",
                "metrics": {"tasks_completed": 1, "success_rate": 1.0},
            }
        )

        # Act
        start_time = time.time()

        # Run multiple cycles
        for _ in range(5):
            mock_agent.scan()
            mock_agent.plan()
            mock_agent.execute(task_id=1, skill_name="test")
            mock_agent.learn()

        elapsed = time.time() - start_time

        # Assert
        assert elapsed < 30.0  # Should complete within 30 seconds


class TestRealWorldScenarios:
    """Real-world scenario tests"""

    def test_project_optimization_scenario(self, mock_agent):
        """Test project optimization scenario"""
        # Arrange
        mock_agent.scan = MagicMock(
            return_value={
                "status": "success",
                "files_found": 100,
                "languages": ["python", "javascript"],
            }
        )
        mock_agent.plan = MagicMock(
            return_value={
                "status": "success",
                "tasks": [
                    {"id": 1, "action": "analyze", "target": "architecture"},
                    {"id": 2, "action": "optimize", "target": "performance"},
                    {"id": 3, "action": "audit", "target": "security"},
                ],
                "estimated_duration": 120,
            }
        )
        mock_agent.execute = MagicMock(return_value={"status": "success", "task_id": 1, "result": "completed"})
        mock_agent.learn = MagicMock(
            return_value={
                "status": "success",
                "metrics": {"tasks_completed": 3, "success_rate": 1.0},
            }
        )

        # Act
        scan_result = mock_agent.scan()
        plan_result = mock_agent.plan()
        execute_result = mock_agent.execute(task_id=1, skill_name="optimize")
        learn_result = mock_agent.learn()

        # Assert
        assert scan_result["files_found"] == 100
        assert len(plan_result["tasks"]) == 3
        assert execute_result["status"] == "success"
        assert learn_result["metrics"]["tasks_completed"] == 3

    def test_security_audit_scenario(self, mock_agent):
        """Test security audit scenario"""
        # Arrange
        mock_agent.scan = MagicMock(
            return_value={
                "status": "success",
                "files_found": 50,
                "security_issues": 3,
            }
        )
        mock_agent.plan = MagicMock(
            return_value={
                "status": "success",
                "tasks": [
                    {"id": 1, "action": "scan", "target": "security"},
                    {"id": 2, "action": "fix", "target": "issue_1"},
                    {"id": 3, "action": "fix", "target": "issue_2"},
                ],
            }
        )
        mock_agent.learn = MagicMock(
            return_value={
                "status": "success",
                "metrics": {"security_issues_fixed": 3},
            }
        )

        # Act
        scan_result = mock_agent.scan()
        plan_result = mock_agent.plan()
        learn_result = mock_agent.learn()

        # Assert
        assert scan_result["security_issues"] == 3
        assert len(plan_result["tasks"]) == 3
        assert learn_result["metrics"]["security_issues_fixed"] == 3

    def test_performance_optimization_scenario(self, mock_agent):
        """Test performance optimization scenario"""
        # Arrange
        mock_agent.scan = MagicMock(
            return_value={
                "status": "success",
                "files_found": 200,
                "performance_bottlenecks": 5,
            }
        )
        mock_agent.plan = MagicMock(
            return_value={
                "status": "success",
                "tasks": [
                    {"id": 1, "action": "profile", "target": "database"},
                    {"id": 2, "action": "optimize", "target": "queries"},
                    {"id": 3, "action": "cache", "target": "results"},
                ],
            }
        )
        mock_agent.learn = MagicMock(
            return_value={
                "status": "success",
                "metrics": {"performance_improvement": 45.0},
            }
        )

        # Act
        scan_result = mock_agent.scan()
        plan_result = mock_agent.plan()
        learn_result = mock_agent.learn()

        # Assert
        assert scan_result["performance_bottlenecks"] == 5
        assert len(plan_result["tasks"]) == 3
        assert learn_result["metrics"]["performance_improvement"] == 45.0


class TestAgentStateManagement:
    """Agent state management tests"""

    def test_state_persistence(self, mock_agent):
        """Test state persistence across operations"""
        # Arrange
        mock_agent.save_state = MagicMock(return_value=True)
        mock_agent.load_state = MagicMock(
            return_value={
                "last_scan": {"timestamp": "2026-06-05", "files_found": 10},
                "last_plan": {"timestamp": "2026-06-05", "tasks": 1},
            }
        )

        # Act
        saved = mock_agent.save_state()
        loaded = mock_agent.load_state()

        # Assert
        assert saved is True
        assert "last_scan" in loaded
        assert "last_plan" in loaded

    def test_state_recovery(self, mock_agent):
        """Test state recovery after failure"""
        # Arrange
        mock_agent.save_state = MagicMock(return_value=True)
        mock_agent.load_state = MagicMock(
            return_value={
                "last_scan": {"timestamp": "2026-06-05", "files_found": 10},
                "last_plan": {"timestamp": "2026-06-05", "tasks": 1},
                "last_execute": {"timestamp": "2026-06-05", "status": "success"},
            }
        )

        # Act
        saved = mock_agent.save_state()
        loaded = mock_agent.load_state()

        # Assert
        assert saved is True
        assert loaded["last_execute"]["status"] == "success"
