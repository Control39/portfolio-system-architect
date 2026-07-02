#!/usr/bin/env python3
"""Критериальный тест ExplanationEngine

Критерии:
1. Создание engine
2. explain_action возвращает структуру с why, evidence, risk_assessment, alternatives_considered
3. explain_decision возвращает структуру с why, evidence, risk_assessment, alternatives_considered
4. get_explanation_history возвращает список
5. clear_history очищает историю
6. get_stats возвращает статистику
7. Интеграция с TransparencyLogger
8. save_to_file сохраняет объяснения в файлы
9. get_explanation_by_id возвращает объяснение по ID
"""

import json
import tempfile
from pathlib import Path

from agents.cognitive_agent.src.explanation_engine import ExplanationEngine
from agents.cognitive_agent.src.transparency_logger import TransparencyLogger


def test_explanation_engine_criteria():
    """Критериальный тест ExplanationEngine"""
    print("=" * 80)
    print("КРИТЕРИАЛЬНЫЙ ТЕСТ: ExplanationEngine")
    print("=" * 80)

    # Критерий 1: Создание engine
    print("\n[1/9] Создание ExplanationEngine...")
    engine = ExplanationEngine()
    assert engine is not None
    assert len(engine.explanations) == 0
    print("✓ ExplanationEngine создан")

    # Критерий 2: explain_action возвращает правильную структуру
    print("\n[2/9] explain_action с правильной структурой...")
    action = {
        "name": "modify_config",
        "file": "config.yaml",
        "description": "Modify configuration file",
        "risk_level": "high",
    }
    explanation = engine.explain_action(action)

    assert "id" in explanation
    assert "type" in explanation
    assert explanation["type"] == "action"
    assert "why" in explanation
    assert "evidence" in explanation
    assert "risk_assessment" in explanation
    assert "alternatives_considered" in explanation
    assert "timestamp" in explanation

    assert explanation["action"] == action
    assert explanation["risk_assessment"] == "high"
    assert "File: config.yaml" in explanation["evidence"]
    print("✓ explain_action возвращает правильную структуру")

    # Критерий 3: explain_decision возвращает правильную структуру
    print("\n[3/9] explain_decision с правильной структурой...")
    decision = "Use alternative approach"
    context = {"files_analyzed": 5, "risk_level": "low"}
    explanation = engine.explain_decision(decision, context)

    assert "id" in explanation
    assert "type" in explanation
    assert explanation["type"] == "decision"
    assert "why" in explanation
    assert "evidence" in explanation
    assert "risk_assessment" in explanation
    assert "alternatives_considered" in explanation

    assert explanation["decision"] == decision
    assert explanation["context"] == context
    assert "Files analyzed: 5" in explanation["evidence"]
    print("✓ explain_decision возвращает правильную структуру")

    # Критерий 4: get_explanation_history возвращает список
    print("\n[4/9] get_explanation_history...")
    history = engine.get_explanation_history()

    assert isinstance(history, list)
    assert len(history) == 2  # 1 action + 1 decision
    print("✓ get_explanation_history возвращает список")

    # Критерий 5: clear_history очищает историю
    print("\n[5/9] clear_history...")
    engine.clear_history()
    history = engine.get_explanation_history()

    assert len(history) == 0
    print("✓ clear_history очищает историю")

    # Критерий 6: get_stats возвращает статистику
    print("\n[6/9] get_stats...")
    engine.explain_action({"name": "action1", "risk_level": "low"})
    engine.explain_action({"name": "action2", "risk_level": "high"})
    engine.explain_decision("test", {"risk_level": "medium"})

    stats = engine.get_stats()

    assert stats["total_explanations"] == 3
    assert stats["actions"] == 2
    assert stats["decisions"] == 1
    assert stats["high_risk"] == 1  # only "high", not "medium"
    print("✓ get_stats возвращает корректную статистику")

    # Критерий 7: Интеграция с TransparencyLogger
    print("\n[7/9] Интеграция с TransparencyLogger...")
    logger = TransparencyLogger()
    engine_with_logger = ExplanationEngine(transparency_logger=logger)
    action = {"name": "test", "description": "Test action"}

    engine_with_logger.explain_action(action)

    assert len(logger._action_history) == 1
    assert logger._action_history[0]["status"] == "executed"
    print("✓ Интеграция с TransparencyLogger работает")

    # Критерий 8: save_to_file сохраняет объяснения в файлы
    print("\n[8/9] save_to_file...")
    with tempfile.TemporaryDirectory() as tmpdir:
        explanations_dir = Path(tmpdir) / "explanations"
        engine_with_file = ExplanationEngine(save_to_file=True)
        engine_with_file.explanations_dir = explanations_dir
        engine_with_file.explanations_dir.mkdir(parents=True, exist_ok=True)

        action = {"name": "test_action"}
        engine_with_file.explain_action(action)

        explanation_files = list(explanations_dir.glob("*.json"))
        assert len(explanation_files) == 1

        with open(explanation_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["action"]["name"] == "test_action"
    print("✓ save_to_file сохраняет объяснения в файлы")

    # Критерий 9: get_explanation_by_id возвращает объяснение по ID
    print("\n[9/9] get_explanation_by_id...")
    engine_for_id = ExplanationEngine()
    action = {"name": "test_action"}
    explanation = engine_for_id.explain_action(action)
    explanation_id = explanation["id"]

    result = engine_for_id.get_explanation_by_id(explanation_id)

    assert result is not None
    assert result["id"] == explanation_id
    assert result["action"]["name"] == "test_action"

    # Тест с несуществующим ID
    result = engine_for_id.get_explanation_by_id("nonexistent-id")
    assert result is None
    print("✓ get_explanation_by_id возвращает объяснение по ID")

    # Итог
    print("\n" + "=" * 80)
    print("ВСЕ КРИТЕРИИ ПРОЙДЕНЫ!")
    print("=" * 80)
    print("\nSummary:")
    print("- ExplanationEngine корректно инициализируется")
    print("- explain_action и explain_decision возвращают структурированные объяснения")
    print("- История объяснений управляется корректно")
    print("- Статистика подсчитывается правильно")
    print("- Интеграция с TransparencyLogger работает")
    print("- save_to_file сохраняет объяснения")
    print("- get_explanation_by_id находит объяснения по ID")
    print("=" * 80)


if __name__ == "__main__":
    test_explanation_engine_criteria()
