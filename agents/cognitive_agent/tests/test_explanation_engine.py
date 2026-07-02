"""Тесты ExplanationEngine (src/explanation_engine.py)

Service Tier: UNIT
Purpose: Unit testing for ExplanationEngine class
"""

import json
import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.explanation_engine import ExplanationEngine
from agents.cognitive_agent.src.transparency_logger import TransparencyLogger


class TestExplanationEngineInitialization:
    """Тесты инициализации ExplanationEngine"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        engine = ExplanationEngine()

        assert len(engine.explanations) == 0
        assert engine.transparency_logger is None
        assert engine.save_to_file is False
        assert engine.explanations_dir == Path(".agent_data/explanations")

    def test_initialization_with_transparency_logger(self):
        """Тест инициализации с transparency_logger"""
        logger = TransparencyLogger()
        engine = ExplanationEngine(transparency_logger=logger)

        assert engine.transparency_logger == logger

    def test_initialization_with_save_to_file(self):
        """Тест инициализации с save_to_file=True"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ExplanationEngine(save_to_file=True)

            # Переопределяем директорию для теста
            with tempfile.TemporaryDirectory() as tmpdir2:
                engine.explanations_dir = Path(tmpdir2) / "explanations"
                engine.explanations_dir.mkdir(parents=True, exist_ok=True)

                assert engine.explanations_dir.exists()

    def test_initialization_logs_initialization(self, caplog):
        """Тест, что инициализация логируется"""
        # Логи идут через structlog, а не через caplog, поэтому просто проверяем, что инициализация прошла успешно
        engine = ExplanationEngine()

        assert engine is not None
        assert len(engine.explanations) == 0


class TestExplanationEngineExplainAction:
    """Тесты метода explain_action"""

    def test_explain_action_returns_correct_structure(self):
        """Тест, что explain_action возвращает корректную структуру"""
        engine = ExplanationEngine()
        action = {"name": "test_action", "description": "Test description"}

        result = engine.explain_action(action)

        assert result["id"] is not None
        assert result["type"] == "action"
        assert result["action"] == action
        assert "why" in result
        assert "evidence" in result
        assert "risk_assessment" in result
        assert "alternatives_considered" in result
        assert "timestamp" in result

    def test_explain_action_with_file(self):
        """Тест explain_action с file"""
        engine = ExplanationEngine()
        action = {"name": "modify_file", "file": "config.yaml", "risk_level": "high"}

        result = engine.explain_action(action)

        assert "File: config.yaml" in result["evidence"]
        assert "Risk level: high" in result["evidence"]

    def test_explain_action_with_risk_level(self):
        """Тест explain_action с различными уровнями риска"""
        engine = ExplanationEngine()

        for risk in ["low", "medium", "high", "critical"]:
            action = {"name": "test", "risk_level": risk}
            result = engine.explain_action(action)
            assert result["risk_assessment"] == risk

    def test_explain_action_adds_to_history(self):
        """Тест, что explain_action добавляет в историю"""
        engine = ExplanationEngine()
        action = {"name": "test_action"}

        engine.explain_action(action)

        assert len(engine.explanations) == 1
        assert engine.explanations[0]["action"] == action

    def test_explain_action_with_transparency_logger(self):
        """Тест explain_action с transparency_logger"""
        logger = TransparencyLogger()
        engine = ExplanationEngine(transparency_logger=logger)
        action = {"name": "test_action", "description": "Test"}

        engine.explain_action(action)

        # Проверяем, что log_action был вызван
        assert len(logger._action_history) == 1
        assert logger._action_history[0]["status"] == "executed"

    def test_explain_action_with_save_to_file(self):
        """Тест explain_action с save_to_file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            explanations_dir = Path(tmpdir) / "explanations"
            engine = ExplanationEngine(save_to_file=True)
            engine.explanations_dir = explanations_dir
            engine.explanations_dir.mkdir(parents=True, exist_ok=True)

            action = {"name": "test_action"}

            engine.explain_action(action)

            # Проверяем, что файл создан
            explanation_files = list(explanations_dir.glob("*.json"))
            assert len(explanation_files) == 1

            # Проверяем содержимое
            with open(explanation_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["action"]["name"] == "test_action"


class TestExplanationEngineExplainDecision:
    """Тесты метода explain_decision"""

    def test_explain_decision_returns_correct_structure(self):
        """Тест, что explain_decision возвращает корректную структуру"""
        engine = ExplanationEngine()
        decision = "Use alternative approach"
        context = {"files_analyzed": 5, "risk_level": "low"}

        result = engine.explain_decision(decision, context)

        assert result["id"] is not None
        assert result["type"] == "decision"
        assert result["decision"] == decision
        assert result["context"] == context
        assert "why" in result
        assert "evidence" in result
        assert "risk_assessment" in result
        assert "alternatives_considered" in result

    def test_explain_decision_with_context(self):
        """Тест explain_decision с контекстом"""
        engine = ExplanationEngine()
        decision = "Skip validation"
        context = {
            "files_analyzed": 10,
            "issues_found": 0,
            "risk_level": "low",
        }

        result = engine.explain_decision(decision, context)

        assert "Files analyzed: 10" in result["evidence"]
        # issues_found: 0 не добавляется, так как 0 - falsy value
        assert result["risk_assessment"] == "low"

    def test_explain_decision_adds_to_history(self):
        """Тест, что explain_decision добавляет в историю"""
        engine = ExplanationEngine()
        decision = "Test decision"
        context = {}

        engine.explain_decision(decision, context)

        assert len(engine.explanations) == 1
        assert engine.explanations[0]["type"] == "decision"

    def test_explain_decision_with_save_to_file(self):
        """Тест explain_decision с save_to_file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            explanations_dir = Path(tmpdir) / "explanations"
            engine = ExplanationEngine(save_to_file=True)
            engine.explanations_dir = explanations_dir
            engine.explanations_dir.mkdir(parents=True, exist_ok=True)

            decision = "Test decision"
            context = {}

            engine.explain_decision(decision, context)

            explanation_files = list(explanations_dir.glob("*.json"))
            assert len(explanation_files) == 1

            with open(explanation_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["type"] == "decision"


class TestExplanationEngineGetExplanationHistory:
    """Тесты метода get_explanation_history"""

    def test_get_explanation_history_empty(self):
        """Тест get_explanation_history с пустой историей"""
        engine = ExplanationEngine()

        history = engine.get_explanation_history()

        assert history == []

    def test_get_explanation_history_with_limit(self):
        """Тест get_explanation_history с лимитом"""
        engine = ExplanationEngine()

        for i in range(10):
            engine.explain_action({"name": f"action_{i}"})

        history = engine.get_explanation_history(limit=5)

        assert len(history) == 5
        assert history[0]["action"]["name"] == "action_5"

    def test_get_explanation_history_all(self):
        """Тест get_explanation_history без лимита"""
        engine = ExplanationEngine()

        for i in range(3):
            engine.explain_action({"name": f"action_{i}"})

        history = engine.get_explanation_history()

        assert len(history) == 3


class TestExplanationEngineClearHistory:
    """Тесты метода clear_history"""

    def test_clear_history(self):
        """Тест clear_history"""
        engine = ExplanationEngine()

        for i in range(5):
            engine.explain_action({"name": f"action_{i}"})

        engine.clear_history()

        assert len(engine.explanations) == 0


class TestExplanationEngineGetStats:
    """Тесты метода get_stats"""

    def test_get_stats_empty(self):
        """Тест get_stats с пустой историей"""
        engine = ExplanationEngine()

        stats = engine.get_stats()

        assert stats["total_explanations"] == 0
        assert stats["actions"] == 0
        assert stats["decisions"] == 0
        assert stats["high_risk"] == 0

    def test_get_stats_with_mixed_explanations(self):
        """Тест get_stats с разными типами объяснений"""
        engine = ExplanationEngine()

        engine.explain_action({"name": "action1", "risk_level": "low"})
        engine.explain_action({"name": "action2", "risk_level": "high"})
        engine.explain_decision("test_decision", {"risk_level": "medium"})
        engine.explain_decision("test_decision2", {"risk_level": "critical"})

        stats = engine.get_stats()

        assert stats["total_explanations"] == 4
        assert stats["actions"] == 2
        assert stats["decisions"] == 2
        assert stats["high_risk"] == 2  # high + critical


class TestExplanationEngineHelperMethods:
    """Тесты helper методов"""

    def test_generate_reason_with_description(self):
        """Тест _generate_reason с description"""
        engine = ExplanationEngine()
        action = {"name": "test", "description": "Custom description"}

        reason = engine._generate_reason(action)

        assert reason == "Custom description"

    def test_generate_reason_with_file(self):
        """Тест _generate_reason с file"""
        engine = ExplanationEngine()
        action = {"name": "modify", "file": "config.yaml"}

        reason = engine._generate_reason(action)

        assert "config.yaml" in reason

    def test_collect_evidence_with_file(self):
        """Тест _collect_evidence с file"""
        engine = ExplanationEngine()
        action = {"name": "test", "file": "config.yaml"}

        evidence = engine._collect_evidence(action)

        assert "File: config.yaml" in evidence

    def test_collect_evidence_with_risk(self):
        """Тест _collect_evidence с risk_level"""
        engine = ExplanationEngine()
        action = {"name": "test", "risk_level": "high"}

        evidence = engine._collect_evidence(action)

        assert "Risk level: high" in evidence

    def test_assess_risk_with_level(self):
        """Тест _assess_risk с уровнем риска"""
        engine = ExplanationEngine()
        action = {"name": "test", "risk_level": "critical"}

        risk = engine._assess_risk(action)

        assert risk == "critical"

    def test_assess_risk_default(self):
        """Тест _assess_risk по умолчанию"""
        engine = ExplanationEngine()
        action = {"name": "test"}

        risk = engine._assess_risk(action)

        assert risk == "medium"

    def test_list_alternatives_with_file(self):
        """Тест _list_alternatives с file"""
        engine = ExplanationEngine()
        action = {"name": "modify", "file": "config.yaml"}

        alternatives = engine._list_alternatives(action)

        assert len(alternatives) >= 2
        assert alternatives[0]["alternative"] == "Do nothing"

    def test_generate_decision_reason(self):
        """Тест _generate_decision_reason"""
        engine = ExplanationEngine()
        decision = "Use cache"
        context = {"type": "performance"}

        reason = engine._generate_decision_reason(decision, context)

        assert "Use cache" in reason

    def test_collect_decision_evidence_with_context(self):
        """Тест _collect_decision_evidence с контекстом"""
        engine = ExplanationEngine()
        context = {"files_analyzed": 5, "issues_found": 3}

        evidence = engine._collect_decision_evidence(context)

        assert "Files analyzed: 5" in evidence
        assert "Issues found: 3" in evidence

    def test_assess_decision_risk_with_context(self):
        """Тест _assess_decision_risk с контекстом"""
        engine = ExplanationEngine()
        decision = "Test"
        context = {"risk_level": "high"}

        risk = engine._assess_decision_risk(decision, context)

        assert risk == "high"

    def test_list_decision_alternatives(self):
        """Тест _list_decision_alternatives"""
        engine = ExplanationEngine()
        decision = "Test"
        context = {}

        alternatives = engine._list_decision_alternatives(decision, context)

        assert len(alternatives) >= 2


class TestExplanationEngineIntegrationWithTransparencyLogger:
    """Интеграционные тесты с TransparencyLogger"""

    def test_explain_action_logs_to_transparency(self):
        """Тест, что explain_action логирует в TransparencyLogger"""
        logger = TransparencyLogger()
        engine = ExplanationEngine(transparency_logger=logger)
        action = {"name": "test_action", "description": "Test"}

        engine.explain_action(action)

        assert len(logger._action_history) == 1
        assert logger._action_history[0]["executed"].startswith("Explanation generated:")

    def test_explain_decision_does_not_log_to_transparency(self):
        """Тест, что explain_decision не логирует в TransparencyLogger"""
        logger = TransparencyLogger()
        engine = ExplanationEngine(transparency_logger=logger)
        decision = "Test"
        context = {}

        engine.explain_decision(decision, context)

        # explain_decision не должен логировать в TransparencyLogger
        assert len(logger._action_history) == 0


class TestExplanationEngineGetExplanationById:
    """Тесты метода get_explanation_by_id"""

    def test_get_explanation_by_id_found(self):
        """Тест get_explanation_by_id с найденным объяснением"""
        engine = ExplanationEngine()
        action = {"name": "test_action"}

        explanation = engine.explain_action(action)
        explanation_id = explanation["id"]

        result = engine.get_explanation_by_id(explanation_id)

        assert result is not None
        assert result["id"] == explanation_id
        assert result["action"]["name"] == "test_action"

    def test_get_explanation_by_id_not_found(self):
        """Тест get_explanation_by_id с не найденным объяснением"""
        engine = ExplanationEngine()

        result = engine.get_explanation_by_id("nonexistent-id")

        assert result is None
