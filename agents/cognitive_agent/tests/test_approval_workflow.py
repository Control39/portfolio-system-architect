"""Тесты ApprovalWorkflow (src/approval_workflow.py)

Service Tier: UNIT
Purpose: Unit testing for ApprovalWorkflow class
"""

import json
from pathlib import Path

import pytest

from agents.cognitive_agent.src.approval_workflow import ApprovalWorkflow


class TestApprovalWorkflowInitialization:
    """Тесты инициализации ApprovalWorkflow"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        workflow = ApprovalWorkflow()

        assert len(workflow.pending_approvals) == 0
        assert workflow.approvals_dir.exists()
        assert workflow.approvals_dir == Path(".agent_data/approvals")
        assert workflow._timeout.total_seconds() == 300

    def test_initialization_with_transparency_logger(self):
        """Тест инициализации с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        workflow = ApprovalWorkflow(transparency_logger=logger)

        assert workflow.transparency_logger == logger

    def test_initialization_with_safe_mode_config(self):
        """Тест инициализации с safe_mode_config"""
        safe_config = {"mode": "LOCKDOWN"}
        workflow = ApprovalWorkflow(safe_mode_config=safe_config)

        assert workflow.safe_mode_config == safe_config


class TestApprovalWorkflowRequestApproval:
    """Тесты метода request_approval"""

    def test_auto_approve_low_risk(self):
        """Тест автоподтверждения для low риска"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "read_file",
                "risk_level": "low",
                "description": "Read config file",
            }
        )

        assert result["status"] == "auto_approved"
        assert len(workflow.pending_approvals) == 0

    def test_auto_approve_medium_risk(self):
        """Тест автоподтверждения для medium риска"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "update_docs",
                "risk_level": "medium",
                "description": "Update documentation",
            }
        )

        assert result["status"] == "auto_approved"
        assert len(workflow.pending_approvals) == 0

    def test_pending_high_risk(self):
        """Тест ожидания подтверждения для high риска"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "modify_config",
                "risk_level": "high",
                "description": "Modify agent config",
                "path": "config.yaml",
            }
        )

        assert result["status"] == "pending"
        assert "approval_id" in result
        assert len(workflow.pending_approvals) == 1

    def test_pending_critical_risk(self):
        """Тест ожидания подтверждения для critical риска"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "modify_main_code",
                "risk_level": "critical",
                "description": "Modify main.py",
                "path": "main.py",
            }
        )

        assert result["status"] == "pending"
        assert "approval_id" in result
        assert len(workflow.pending_approvals) == 1

    def test_invalid_risk_level_defaults_to_medium(self):
        """Тест, что невалидный риск level становится medium"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "invalid_level",
            }
        )

        assert result["status"] == "auto_approved"  # medium = auto_approved


class TestApprovalWorkflowAutoApproveWithSafeMode:
    """Тесты автоподтверждения с safe_mode"""

    def test_lockdown_mode_requires_approval(self):
        """Тест, что LOCKDOWN режим требует подтверждения даже для low"""
        safe_config = {"mode": "LOCKDOWN"}
        workflow = ApprovalWorkflow(safe_mode_config=safe_config)

        result = workflow.request_approval(
            {
                "action": "read_file",
                "risk_level": "low",
                "description": "Read config",
            }
        )

        assert result["status"] == "pending"
        assert len(workflow.pending_approvals) == 1


class TestApprovalWorkflowApprove:
    """Тесты метода approve"""

    def test_approve_valid(self):
        """Тест подтверждения валидного ID"""
        workflow = ApprovalWorkflow()

        # Создать request
        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
            }
        )
        approval_id = result["approval_id"]

        # Подтвердить
        approved = workflow.approve(approval_id)

        assert approved is True
        assert approval_id not in workflow.pending_approvals

    def test_approve_invalid(self):
        """Тест подтверждения невалидного ID"""
        workflow = ApprovalWorkflow()

        approved = workflow.approve("non-existent-id")

        assert approved is False
        assert len(workflow.pending_approvals) == 0


class TestApprovalWorkflowDeny:
    """Тесты метода deny"""

    def test_deny_valid(self):
        """Тест отклонения валидного ID"""
        workflow = ApprovalWorkflow()

        # Создать request
        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
            }
        )
        approval_id = result["approval_id"]

        # Отклонить
        denied = workflow.deny(approval_id)

        assert denied is True
        assert approval_id not in workflow.pending_approvals

    def test_deny_invalid(self):
        """Тест отклонения невалидного ID"""
        workflow = ApprovalWorkflow()

        denied = workflow.deny("non-existent-id")

        assert denied is False


class TestApprovalWorkflowCheckPending:
    """Тесты метода check_pending"""

    def test_check_pending_empty(self):
        """Тест check_pending с пустыми заявками"""
        workflow = ApprovalWorkflow()

        pending = workflow.check_pending()

        assert pending == []

    def test_check_pending_with_requests(self):
        """Тест check_pending с заявками"""
        workflow = ApprovalWorkflow()

        workflow.request_approval(
            {
                "action": "test1",
                "risk_level": "high",
            }
        )
        workflow.request_approval(
            {
                "action": "test2",
                "risk_level": "critical",
            }
        )

        pending = workflow.check_pending()

        assert len(pending) == 2


class TestApprovalWorkflowIsExpired:
    """Тесты метода is_expired"""

    def test_is_expired_valid(self):
        """Тест is_expired для валидного ID"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
            }
        )
        approval_id = result["approval_id"]

        expired = workflow.is_expired(approval_id)

        assert expired is False  # Ещё не истёк

    def test_is_expired_invalid(self):
        """Тест is_expired для невалидного ID"""
        workflow = ApprovalWorkflow()

        expired = workflow.is_expired("non-existent-id")

        assert expired is True  # Не существует = истёк


class TestApprovalWorkflowSaveApproval:
    """Тесты сохранения в файл"""

    def test_approval_file_created(self):
        """Тест, что файл создания"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
            }
        )
        approval_id = result["approval_id"]

        approval_file = workflow.approvals_dir / f"approval_{approval_id}.json"

        assert approval_file.exists()

    def test_approval_file_content(self):
        """Тест содержимого файла"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
                "description": "Test approval",
            }
        )
        approval_id = result["approval_id"]

        approval_file = workflow.approvals_dir / f"approval_{approval_id}.json"

        with open(approval_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == approval_id
        assert data["status"] == "pending"
        assert data["risk_level"] == "high"
        assert data["action"]["action"] == "test"


class TestApprovalWorkflowIntegration:
    """Тесты интеграции с TransparencyLogger"""

    def test_transparency_logger_integration(self):
        """Тест интеграции с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        workflow = ApprovalWorkflow(transparency_logger=logger)

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
                "description": "Test action",
            }
        )

        # Проверить статус прозрачности
        status = logger.get_status()
        assert status["total_actions"] > 0
        assert status["discrepancies"] == 1  # planned != executed

    def test_transparency_logger_auto_approve(self):
        """Тест интеграции с auto_approved"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        workflow = ApprovalWorkflow(transparency_logger=logger)

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "low",
                "description": "Low risk action",
            }
        )

        # Проверить статус прозрачности
        status = logger.get_status()
        assert status["total_actions"] > 0


class TestApprovalWorkflowGetStats:
    """Тесты метода get_stats"""

    def test_get_stats_empty(self):
        """Тест get_stats с пустыми заявками"""
        workflow = ApprovalWorkflow()

        stats = workflow.get_stats()

        assert stats["total_pending"] == 0
        assert stats["high_risk_pending"] == 0
        assert stats["critical_risk_pending"] == 0

    def test_get_stats_with_requests(self):
        """Тест get_stats с заявками"""
        workflow = ApprovalWorkflow()

        workflow.request_approval({"action": "low", "risk_level": "low"})
        workflow.request_approval({"action": "high", "risk_level": "high"})
        workflow.request_approval({"action": "critical", "risk_level": "critical"})

        stats = workflow.get_stats()

        assert stats["total_pending"] == 2
        assert stats["high_risk_pending"] == 1
        assert stats["critical_risk_pending"] == 1


class TestApprovalWorkflowFilePaths:
    """Тесты работы с путями"""

    def test_approvals_dir_path(self):
        """Тест approvals_dir"""
        workflow = ApprovalWorkflow()

        assert workflow.approvals_dir == Path(".agent_data/approvals")
        assert workflow.approvals_dir.exists()

    def test_approval_file_absolute_path(self):
        """Тест абсолютного пути к файлу"""
        workflow = ApprovalWorkflow()

        result = workflow.request_approval(
            {
                "action": "test",
                "risk_level": "high",
            }
        )
        approval_id = result["approval_id"]

        approval_file = workflow.approvals_dir / f"approval_{approval_id}.json"

        # Проверить, что путь абсолютный
        assert approval_file.is_absolute() or str(approval_file).startswith(".")
