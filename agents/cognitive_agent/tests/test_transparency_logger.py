"""Тесты TransparencyLogger (src/transparency_logger.py)

Service Tier: UNIT
Purpose: Unit testing for TransparencyLogger class
"""

import json
import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.transparency_logger import TransparencyLogger


class TestTransparencyLoggerInitialization:
    """Тесты инициализации TransparencyLogger"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        logger = TransparencyLogger()

        assert logger.agent_id == "transparency-agent"
        assert logger._transparency_level == "full"
        assert len(logger._action_history) == 0
        assert Path(logger.log_file).parent.exists()

    def test_initialization_with_custom_agent_id(self):
        """Тест инициализации с кастомным agent_id"""
        logger = TransparencyLogger(agent_id="test-agent")

        assert logger.agent_id == "test-agent"

    def test_initialization_with_custom_log_file(self):
        """Тест инициализации с кастомным log_file"""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            log_file = f.name

        try:
            logger = TransparencyLogger(log_file=log_file)

            assert logger.log_file == log_file
            assert Path(log_file).exists()
        finally:
            Path(log_file).unlink(missing_ok=True)


class TestTransparencyLoggerSetTransparencyLevel:
    """Тесты метода set_transparency_level"""

    def test_set_transparency_level_full(self):
        """Тест установки уровня 'full'"""
        logger = TransparencyLogger()
        logger.set_transparency_level("full")

        assert logger._transparency_level == "full"

    def test_set_transparency_level_partial(self):
        """Тест установки уровня 'partial'"""
        logger = TransparencyLogger()
        logger.set_transparency_level("partial")

        assert logger._transparency_level == "partial"

    def test_set_transparency_level_minimal(self):
        """Тест установки уровня 'minimal'"""
        logger = TransparencyLogger()
        logger.set_transparency_level("minimal")

        assert logger._transparency_level == "minimal"

    def test_set_invalid_transparency_level_raises_error(self):
        """Тест, что установка невалидного уровня вызывает ошибку"""
        logger = TransparencyLogger()

        with pytest.raises(ValueError) as exc_info:
            logger.set_transparency_level("invalid")

        assert "Invalid transparency level" in str(exc_info.value)


class TestTransparencyLoggerLogAction:
    """Тесты метода log_action"""

    def test_log_action_with_full_data(self):
        """Тест log_action с полными данными"""
        logger = TransparencyLogger()

        action_data = {
            "planned": "Delete file config.yaml",
            "executed": "Delete file config.yaml",
            "status": "executed",
            "confidence": 0.95,
            "user_approval": True,
        }

        result = logger.log_action(action_data)

        assert result is True
        assert len(logger._action_history) == 1
        assert logger._action_history[0]["planned"] == action_data["planned"]
        assert logger._action_history[0]["executed"] == action_data["executed"]
        assert logger._action_history[0]["is_discrepancy"] is False

    def test_log_action_with_discrepancy(self):
        """Тест log_action с расхождением (обман)"""
        logger = TransparencyLogger()

        action_data = {
            "planned": "Delete file config.yaml",
            "executed": "Rename file config.yaml to config.yaml.bak",
            "status": "modified",
            "confidence": 0.8,
            "user_approval": False,
        }

        result = logger.log_action(action_data)

        assert result is True
        assert len(logger._action_history) == 1
        assert logger._action_history[0]["is_discrepancy"] is True

    def test_log_action_with_missing_fields(self):
        """Тест log_action с отсутствующими полями"""
        logger = TransparencyLogger()

        action_data = {
            "planned": "Delete file config.yaml",
            # Missing: executed, status
        }

        result = logger.log_action(action_data)

        assert result is False
        assert len(logger._action_history) == 0

    def test_log_action_without_optional_fields(self):
        """Тест log_action без опциональных полей"""
        logger = TransparencyLogger()

        action_data = {
            "planned": "Test action",
            "executed": "Test action",
            "status": "executed",
        }

        result = logger.log_action(action_data)

        assert result is True
        assert logger._action_history[0]["confidence"] == 1.0
        assert logger._action_history[0]["user_approval"] is False


class TestTransparencyLoggerGetStatus:
    """Тесты метода get_status"""

    def test_get_status_empty_history(self):
        """Тест get_status с пустой историей"""
        logger = TransparencyLogger()

        status = logger.get_status()

        assert status["total_actions"] == 0
        assert status["discrepancies"] == 0
        assert status["discrepancy_rate"] == 0.0
        assert status["history_preview"] == []

    def test_get_status_with_actions(self):
        """Тест get_status с действиями"""
        logger = TransparencyLogger()

        logger.log_action(
            {
                "planned": "Action 1",
                "executed": "Action 1",
                "status": "executed",
            }
        )
        logger.log_action(
            {
                "planned": "Action 2",
                "executed": "Modified Action 2",
                "status": "modified",
            }
        )

        status = logger.get_status()

        assert status["total_actions"] == 2
        assert status["discrepancies"] == 1
        assert status["discrepancy_rate"] == 0.5
        assert len(status["history_preview"]) <= 5


class TestTransparencyLoggerGetDiscrepancies:
    """Тесты метода get_discrepancies"""

    def test_get_discrepancies_empty(self):
        """Тест get_discrepancies с пустой историей"""
        logger = TransparencyLogger()

        discrepancies = logger.get_discrepancies()

        assert discrepancies == []

    def test_get_discrepancies_with_discrepancies(self):
        """Тест get_discrepancies с расхождениями"""
        logger = TransparencyLogger()

        logger.log_action(
            {
                "planned": "Action 1",
                "executed": "Action 1",
                "status": "executed",
            }
        )
        logger.log_action(
            {
                "planned": "Action 2",
                "executed": "Modified Action 2",
                "status": "modified",
            }
        )

        discrepancies = logger.get_discrepancies()

        assert len(discrepancies) == 1
        assert discrepancies[0]["planned"] == "Action 2"


class TestTransparencyLoggerClearHistory:
    """Тесты метода clear_history"""

    def test_clear_history(self):
        """Тест clear_history"""
        logger = TransparencyLogger()

        logger.log_action(
            {
                "planned": "Action 1",
                "executed": "Action 1",
                "status": "executed",
            }
        )
        logger.log_action(
            {
                "planned": "Action 2",
                "executed": "Action 2",
                "status": "executed",
            }
        )

        logger.clear_history()

        assert len(logger._action_history) == 0


class TestTransparencyLoggerFileOperations:
    """Тесты файловых операций"""

    def test_log_file_created(self):
        """Тест, что файл лога создается при инициализации"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = str(Path(tmpdir) / "transparency_test.jsonl")

            logger = TransparencyLogger(log_file=log_file)

            assert Path(log_file).exists()

    def test_log_action_writes_to_file(self):
        """Тест, что log_action пишет в файл"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = str(Path(tmpdir) / "transparency_test.jsonl")

            logger = TransparencyLogger(log_file=log_file)

            logger.log_action(
                {
                    "planned": "Test action",
                    "executed": "Test action",
                    "status": "executed",
                }
            )

            # Прочитать файл
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["planned"] == "Test action"
            assert data["executed"] == "Test action"
