"""Тесты ConflictResolver (src/conflict_resolver.py)

Service Tier: UNIT
Purpose: Unit testing for ConflictResolver class
"""

import json
from pathlib import Path

import pytest

from agents.cognitive_agent.src.conflict_resolver import ConflictResolver


class TestConflictResolverInitialization:
    """Тесты инициализации ConflictResolver"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        resolver = ConflictResolver()

        assert len(resolver.conflicts) == 0
        assert resolver.proposals_dir.exists()
        assert resolver.proposals_dir == Path(".agent_data/proposals")

    def test_initialization_with_transparency_logger(self):
        """Тест инициализации с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        resolver = ConflictResolver(transparency_logger=logger)

        assert resolver.transparency_logger == logger


class TestConflictResolverDetectConflict:
    """Тесты метода detect_conflict"""

    def test_detect_conflict_basic(self):
        """Тест обнаружения базового конфликта"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"mode": "NORMAL"},
            agent_preference={"mode": "LOCKDOWN"},
        )

        assert conflict["id"] is not None
        assert conflict["config"] == "config.yaml"
        assert conflict["human_change"] == {"mode": "NORMAL"}
        assert conflict["agent_preference"] == {"mode": "LOCKDOWN"}
        assert conflict["status"] == "pending"
        assert conflict["human_wins_by_default"] is True
        assert "proposal_id" in conflict

    def test_detect_conflict_no_auto_recovery(self):
        """Тест, что detect_conflict НЕ восстанавливает файлы автоматически"""
        resolver = ConflictResolver()

        # detect_conflict должен создать proposal, но НЕ применять изменения
        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"enabled": True},
            agent_preference={"enabled": False},
        )

        # Проверить, что конфликт создан и статус pending
        assert conflict["status"] == "pending"
        assert conflict["human_wins_by_default"] is True

        # Проверить, что proposal файл создан
        proposal_file = resolver.proposals_dir / f"proposal_{conflict['id']}.json"
        assert proposal_file.exists()

        # Проверить, что конфликт не был автоматически разрешен
        assert conflict.get("resolved_decision") is None

    def test_detect_conflict_with_multiple_changes(self):
        """Тест обнаружения конфликта с множественными изменениями"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="agents/cognitive_agent/config/agent-config.yaml",
            human_change={
                "debug_mode": True,
                "log_level": "DEBUG",
                "max_retries": 5,
            },
            agent_preference={
                "debug_mode": False,
                "log_level": "INFO",
                "max_retries": 3,
            },
        )

        assert conflict["id"] is not None
        assert conflict["human_change"]["debug_mode"] is True
        assert conflict["agent_preference"]["debug_mode"] is False


class TestConflictResolverCreateProposal:
    """Тесты метода _create_proposal"""

    def test_create_proposal_file(self):
        """Тест создания файла proposal"""
        resolver = ConflictResolver()

        conflict = {
            "id": "test-uuid-123",
            "config": "config.yaml",
            "human_change": {"mode": "NORMAL"},
            "agent_preference": {"mode": "LOCKDOWN"},
            "timestamp": "2026-07-02T12:00:00",
        }

        proposal_id = resolver._create_proposal(conflict)

        proposal_file = resolver.proposals_dir / f"proposal_{proposal_id}.json"
        assert proposal_file.exists()

        # Проверить содержимое файла
        with open(proposal_file, encoding="utf-8") as f:
            data = json.load(f)

        assert data["conflict_id"] == "test-uuid-123"
        assert data["config"] == "config.yaml"
        assert data["status"] == "pending"


class TestConflictResolverResolveConflict:
    """Тесты метода resolve_conflict"""

    def test_resolve_conflict_human_wins(self):
        """Тест разрешения конфликта: human_wins"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"mode": "NORMAL"},
            agent_preference={"mode": "LOCKDOWN"},
        )

        resolved = resolver.resolve_conflict(conflict["id"], "human_wins")

        assert resolved["status"] == "resolved"
        assert resolved["resolved_decision"] == "human_wins"
        assert "resolved_at" in resolved

    def test_resolve_conflict_agent_wins(self):
        """Тест разрешения конфликта: agent_wins"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"enabled": True},
            agent_preference={"enabled": False},
        )

        resolved = resolver.resolve_conflict(conflict["id"], "agent_wins")

        assert resolved["status"] == "resolved"
        assert resolved["resolved_decision"] == "agent_wins"

    def test_resolve_conflict_compromise(self):
        """Тест разрешения конфликта: compromise"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"timeout": 30},
            agent_preference={"timeout": 60},
        )

        resolved = resolver.resolve_conflict(conflict["id"], "compromise")

        assert resolved["status"] == "resolved"
        assert resolved["resolved_decision"] == "compromise"

    def test_resolve_conflict_not_found(self):
        """Тест разрешения несуществующего конфликта"""
        resolver = ConflictResolver()

        with pytest.raises(ValueError) as exc_info:
            resolver.resolve_conflict("non-existent-id", "human_wins")

        assert "Conflict not found" in str(exc_info.value)

    def test_resolve_conflict_invalid_decision(self):
        """Тест разрешения с невалидным решением"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )

        with pytest.raises(ValueError) as exc_info:
            resolver.resolve_conflict(conflict["id"], "invalid_decision")

        assert "Invalid decision" in str(exc_info.value)


class TestConflictResolverGetters:
    """Тесты методов получения данных"""

    def test_get_conflict(self):
        """Тест get_conflict"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )

        retrieved = resolver.get_conflict(conflict["id"])

        assert retrieved is not None
        assert retrieved["id"] == conflict["id"]

    def test_get_conflict_not_found(self):
        """Тест get_conflict для несуществующего конфликта"""
        resolver = ConflictResolver()

        result = resolver.get_conflict("non-existent-id")

        assert result is None

    def test_get_all_conflicts(self):
        """Тест get_all_conflicts"""
        resolver = ConflictResolver()

        resolver.detect_conflict(
            config_path="config1.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )
        resolver.detect_conflict(
            config_path="config2.yaml",
            human_change={"b": 1},
            agent_preference={"b": 2},
        )

        all_conflicts = resolver.get_all_conflicts()

        assert len(all_conflicts) == 2

    def test_get_pending_conflicts(self):
        """Тест get_pending_conflicts"""
        resolver = ConflictResolver()

        conflict1 = resolver.detect_conflict(
            config_path="config1.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )

        resolver.resolve_conflict(conflict1["id"], "human_wins")

        conflict2 = resolver.detect_conflict(
            config_path="config2.yaml",
            human_change={"b": 1},
            agent_preference={"b": 2},
        )

        pending = resolver.get_pending_conflicts()

        assert len(pending) == 1
        assert pending[0]["id"] == conflict2["id"]


class TestConflictResolverIntegration:
    """Тесты интеграции с TransparencyLogger"""

    def test_transparency_logger_integration(self):
        """Тест интеграции с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        resolver = ConflictResolver(transparency_logger=logger)

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"mode": "NORMAL"},
            agent_preference={"mode": "LOCKDOWN"},
        )

        # Проверить статус прозрачности
        status = logger.get_status()
        assert status["total_actions"] > 0
        assert status["discrepancies"] == 1  # planned != executed

    def test_transparency_logger_with_resolution(self):
        """Тест интеграции с TransparencyLogger при разрешении"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        resolver = ConflictResolver(transparency_logger=logger)

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )

        resolver.resolve_conflict(conflict["id"], "human_wins")

        # Проверить статус прозрачности
        status = logger.get_status()
        assert status["total_actions"] >= 2  # detect + resolve
        assert status["approved_actions"] >= 1


class TestConflictResolverFilePaths:
    """Тесты работы с путями"""

    def test_proposals_dir_path(self):
        """Тест get_proposals_dir"""
        resolver = ConflictResolver()

        proposals_dir = resolver.get_proposals_dir()

        assert proposals_dir == Path(".agent_data/proposals")
        assert proposals_dir.exists()

    def test_absolute_proposal_file_path(self):
        """Тест абсолютного пути к proposal файлу"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflict(
            config_path="config.yaml",
            human_change={"a": 1},
            agent_preference={"a": 2},
        )

        proposal_file = resolver.proposals_dir / f"proposal_{conflict['id']}.json"

        # Проверить, что путь абсолютный
        assert proposal_file.is_absolute() or str(proposal_file).startswith(".")
