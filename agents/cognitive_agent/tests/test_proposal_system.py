"""Тесты ProposalSystem (src/proposal_system.py)

Service Tier: UNIT
Purpose: Unit testing for ProposalSystem class
"""

import json
from pathlib import Path

import pytest

from agents.cognitive_agent.src.proposal_system import ProposalSystem


class TestProposalSystemInitialization:
    """Тесты инициализации ProposalSystem"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        system = ProposalSystem()

        assert len(system.proposals) == 0
        assert system.proposals_dir.exists()
        assert system.proposals_dir == Path(".agent_data/proposals")

    def test_initialization_with_transparency_logger(self):
        """Тест инициализации с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        system = ProposalSystem(transparency_logger=logger)

        assert system.transparency_logger == logger


class TestProposalSystemCreateProposal:
    """Тесты метода create_proposal"""

    def test_create_proposal_returns_id(self):
        """Тест, что create_proposal возвращает ID"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test Proposal",
            description="Test description",
            changes={"file": "test.py", "action": "create"},
        )

        assert proposal_id is not None
        assert isinstance(proposal_id, str)
        assert len(proposal_id) > 0  # UUID формат

    def test_create_proposal_saves_file(self):
        """Тест, что create_proposal сохраняет файл"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Config Update",
            description="Change timeout",
            changes={"file": "config.yaml", "timeout": 60},
        )

        proposal_file = system.proposals_dir / f"proposal_{proposal_id}.json"
        assert proposal_file.exists()

    def test_create_proposal_file_content(self):
        """Тест содержимого файла предложения"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Description",
            changes={"a": 1},
        )

        proposal_file = system.proposals_dir / f"proposal_{proposal_id}.json"

        with open(proposal_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == proposal_id
        assert data["title"] == "Test"
        assert data["description"] == "Description"
        assert data["changes"] == {"a": 1}
        assert data["status"] == "pending"
        assert data["risk_level"] == "medium"  # default

    def test_create_proposal_with_risk_level(self):
        """Тест создания с кастомным риском"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Critical Change",
            description="Main code change",
            changes={"file": "main.py", "action": "modify"},
            risk_level="critical",
        )

        proposal = system.get_proposal(proposal_id)
        assert proposal["risk_level"] == "critical"


class TestProposalSystemGetProposal:
    """Тесты метода get_proposal"""

    def test_get_proposal_exists(self):
        """Тест get_proposal с существующим ID"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        proposal = system.get_proposal(proposal_id)

        assert proposal is not None
        assert proposal["id"] == proposal_id

    def test_get_proposal_not_found(self):
        """Тест get_proposal с несуществующим ID"""
        system = ProposalSystem()

        proposal = system.get_proposal("non-existent-id")

        assert proposal is None


class TestProposalSystemListProposals:
    """Тесты метода list_proposals"""

    def test_list_proposals_empty(self):
        """Тест list_proposals с пустыми предложениями"""
        system = ProposalSystem()

        proposals = system.list_proposals(status="pending")

        assert proposals == []

    def test_list_proposals_filter_by_status(self):
        """Тест list_proposals с фильтрацией"""
        system = ProposalSystem()

        pid1 = system.create_proposal("Test1", "Desc1", {"a": 1})
        system.update_proposal_status(pid1, "rejected")

        pid2 = system.create_proposal("Test2", "Desc2", {"b": 2})

        pending = system.list_proposals(status="pending")
        rejected = system.list_proposals(status="rejected")

        assert len(pending) == 1
        assert pending[0]["id"] == pid2
        assert len(rejected) == 1
        assert rejected[0]["id"] == pid1

    def test_list_proposals_all(self):
        """Тест list_proposals с all"""
        system = ProposalSystem()

        system.create_proposal("Test1", "Desc1", {"a": 1})
        system.create_proposal("Test2", "Desc2", {"b": 2})

        all_proposals = system.list_proposals(status="all")

        assert len(all_proposals) == 2


class TestProposalSystemApplyProposal:
    """Тесты метода apply_proposal"""

    def test_apply_proposal_valid(self):
        """Тест apply_proposal с валидным ID"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        applied = system.apply_proposal(proposal_id)

        assert applied is True
        proposal = system.get_proposal(proposal_id)
        assert proposal["status"] == "applied"
        assert proposal["applied_at"] is not None
        assert proposal["applied_by"] == "human"

    def test_apply_proposal_invalid(self):
        """Тест apply_proposal с невалидным ID"""
        system = ProposalSystem()

        applied = system.apply_proposal("non-existent-id")

        assert applied is False


class TestProposalSystemRejectProposal:
    """Тесты метода reject_proposal"""

    def test_reject_proposal_valid(self):
        """Тест reject_proposal с валидным ID"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        rejected = system.reject_proposal(proposal_id)

        assert rejected is True
        proposal = system.get_proposal(proposal_id)
        assert proposal["status"] == "rejected"
        assert proposal["rejected_at"] is not None
        assert proposal["rejected_by"] == "human"

    def test_reject_proposal_invalid(self):
        """Тест reject_proposal с невалидным ID"""
        system = ProposalSystem()

        rejected = system.reject_proposal("non-existent-id")

        assert rejected is False


class TestProposalSystemUpdateStatus:
    """Тесты метода update_proposal_status"""

    def test_update_status_valid(self):
        """Тест update_proposal_status с валидным ID"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        updated = system.update_proposal_status(proposal_id, "approved")

        assert updated is True
        proposal = system.get_proposal(proposal_id)
        assert proposal["status"] == "approved"

    def test_update_status_invalid_status(self):
        """Тест update_proposal_status с невалидным статусом"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        updated = system.update_proposal_status(proposal_id, "invalid_status")

        assert updated is False


class TestProposalSystemGetters:
    """Тесты методов получения"""

    def test_get_proposal_file(self):
        """Тест get_proposal_file"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        file_path = system.get_proposal_file(proposal_id)

        assert file_path is not None
        assert file_path.exists()

    def test_get_pending_count(self):
        """Тест get_pending_count"""
        system = ProposalSystem()

        system.create_proposal("Test1", "Desc1", {"a": 1})
        system.create_proposal("Test2", "Desc2", {"b": 2})

        assert system.get_pending_count() == 2

    def test_get_stats(self):
        """Тест get_stats"""
        system = ProposalSystem()

        pid1 = system.create_proposal("Test1", "Desc1", {"a": 1})
        system.update_proposal_status(pid1, "rejected")

        stats = system.get_stats()

        assert stats["total"] == 1
        assert stats["pending"] == 0
        assert stats["rejected"] == 1


class TestProposalSystemIntegration:
    """Тесты интеграции с TransparencyLogger"""

    def test_transparency_logger_integration(self):
        """Тест интеграции с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        system = ProposalSystem(transparency_logger=logger)

        proposal_id = system.create_proposal(
            title="Test Proposal",
            description="Test description",
            changes={"a": 1},
        )

        # Проверить статус прозрачности
        status = logger.get_status()
        assert status["total_actions"] > 0
        assert status["discrepancies"] == 1  # planned != executed


class TestProposalSystemFilePaths:
    """Тесты работы с путями"""

    def test_proposals_dir_path(self):
        """Тест proposals_dir"""
        system = ProposalSystem()

        assert system.proposals_dir == Path(".agent_data/proposals")
        assert system.proposals_dir.exists()

    def test_proposal_file_absolute_path(self):
        """Тест абсолютного пути к файлу"""
        system = ProposalSystem()

        proposal_id = system.create_proposal(
            title="Test",
            description="Desc",
            changes={"a": 1},
        )

        proposal_file = system.proposals_dir / f"proposal_{proposal_id}.json"

        # Проверить, что путь абсолютный
        assert proposal_file.is_absolute() or str(proposal_file).startswith(".")
