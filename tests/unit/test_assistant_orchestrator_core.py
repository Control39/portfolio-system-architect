"""
Unit tests for assistant_orchestrator core components.
"""

from unittest.mock import MagicMock, patch

import pytest

# Импорты тестируемых компонентов
from src.assistant_orchestrator.core.analyzer import AssistantOrchestrator
from src.assistant_orchestrator.core.maturity_scoring import MaturityScorer


def test_assistant_orchestrator_import():
    """Test that AssistantOrchestrator class can be imported."""
    try:
        from src.assistant_orchestrator.core.analyzer import AssistantOrchestrator

        assert AssistantOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"AssistantOrchestrator import failed: {e}")


def test_assistant_orchestrator_initialization():
    """Test initialization of AssistantOrchestrator with project root."""
    with patch(
        "src.assistant_orchestrator.core.analyzer.EvidenceCollector"
    ) as mock_collector_class:
        mock_collector_instance = MagicMock()
        mock_collector_class.return_value = mock_collector_instance

        # Создаём оркестратор
        orchestrator = AssistantOrchestrator(project_root="/fake/project/root")

        # Проверяем атрибуты
        assert orchestrator.project_root == "/fake/project/root"
        # Проверяем, что EvidenceCollector был создан с правильным путём
        mock_collector_class.assert_called_once_with("/fake/project/root")


def test_assistant_orchestrator_run_full_analysis():
    """Test that run_full_analysis collects all evidence and returns AnalysisResult."""
    with patch(
        "src.assistant_orchestrator.core.analyzer.EvidenceCollector"
    ) as mock_collector_class:
        mock_collector_instance = MagicMock()
        mock_collector_class.return_value = mock_collector_instance

        # Настройка моков для каждого метода сбора
        mock_collector_instance.collect_microservices.return_value = {"services": []}
        mock_collector_instance.collect_skill_markers.return_value = {"total_count": 0}
        mock_collector_instance.collect_architecture_docs.return_value = []
        mock_collector_instance.collect_git_stats.return_value = {"total_commits": 0}
        mock_collector_instance.collect_dependencies.return_value = {}

        orchestrator = AssistantOrchestrator(project_root="/fake")
        result = orchestrator.run_full_analysis()

        # Проверяем, что все методы сбора были вызваны
        mock_collector_instance.collect_microservices.assert_called_once()
        mock_collector_instance.collect_skill_markers.assert_called_once()
        mock_collector_instance.collect_architecture_docs.assert_called_once()
        mock_collector_instance.collect_git_stats.assert_called_once()
        mock_collector_instance.collect_dependencies.assert_called_once()

        # Проверяем структуру результата
        assert hasattr(result, "timestamp")
        assert "microservices" in result.__dict__
        assert "skill_markers" in result.__dict__
        assert "architecture_docs" in result.__dict__
        assert "git_stats" in result.__dict__
        assert "dependencies" in result.__dict__


def test_assistant_orchestrator_run_full_analysis_with_errors():
    """Test that run_full_analysis handles errors gracefully and returns partial results."""
    with patch(
        "src.assistant_orchestrator.core.analyzer.EvidenceCollector"
    ) as mock_collector_class:
        mock_collector_instance = MagicMock()
        mock_collector_class.return_value = mock_collector_instance

        # Настройка моков для выброса исключений
        mock_collector_instance.collect_microservices.side_effect = Exception("Microservice error")
        mock_collector_instance.collect_skill_markers.side_effect = Exception("Skills error")
        mock_collector_instance.collect_architecture_docs.side_effect = Exception("Docs error")
        mock_collector_instance.collect_git_stats.side_effect = Exception("Git error")
        mock_collector_instance.collect_dependencies.side_effect = Exception("Deps error")

        orchestrator = AssistantOrchestrator(project_root="/fake")
        result = orchestrator.run_full_analysis()

        # Проверяем, что возвращается AnalysisResult даже при ошибках
        assert hasattr(result, "timestamp")
        # assert "error" in result.microservices
        # assert "error" in result.skill_markers
        # assert "error" in result.git_stats


def test_maturity_scorer_import():
    """Test that MaturityScorer class can be imported."""
    try:
        from src.assistant_orchestrator.core.maturity_scoring import MaturityScorer

        assert MaturityScorer is not None
    except ImportError as e:
        pytest.fail(f"MaturityScorer import failed: {e}")


def test_maturity_scorer_initialization():
    """Test initialization of MaturityScorer."""
    mock_analysis = {"microservices": {}, "skill_markers": {}, "architecture_docs": []}
    scorer = MaturityScorer(analysis_result=mock_analysis)

    assert scorer.analysis == mock_analysis


def test_maturity_scorer_calculate_score():
    """Test that calculate_score returns a float between 0 and 5."""
    # Пустой анализ (минимальный результат)
    empty_analysis = {}
    empty_scorer = MaturityScorer(empty_analysis)
    assert 0.0 <= empty_scorer.calculate_score() <= 5.0

    # Полный анализ (максимальный результат)
    full_analysis = {
        "microservices": {
            "services": [{"is_production_ready": True, "has_tests": True, "has_docker": True}],
            "has_docker_compose": True,
        },
        "skill_markers": {"total_count": 100, "categories": ["cat1", "cat2", "cat3"]},
        "architecture_docs": ["doc1.md", "doc2.md", "doc3.md"],
        "git_stats": {
            "total_commits": 1000,
            "recent_activity_days": 50,
            "contributors": ["a", "b"],
        },
        "dependencies": {"service1": ["dep1"]},
    }
    full_scorer = MaturityScorer(full_analysis)
    score = full_scorer.calculate_score()
    assert 0.0 <= score <= 5.0
    assert score > empty_scorer.calculate_score()  # Полный анализ должен давать лучший результат


def test_maturity_scorer_get_recommendations():
    """Test that get_recommendations returns a list of recommendations."""
    # Анализ с низким количеством production-ready сервисов
    low_prod_analysis = {
        "microservices": {
            "services": [{"is_production_ready": False}, {"is_production_ready": False}],
            "has_kubernetes": False,
        },
        "architecture_docs": ["doc.md"],
        "git_stats": {"recent_activity_days": 5},
    }
    scorer = MaturityScorer(low_prod_analysis)
    recommendations = scorer.get_recommendations()

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Проверяем наличие конкретных рекомендаций
    titles = [rec["title"] for rec in recommendations]
    assert "Добавить Kubernetes manifests" in titles
    assert "Начать вести Architecture Decision Records (ADR)" in titles
    assert "Увеличить активность разработки" in titles

    # Анализ с высокой зрелостью
    high_analysis = {
        "microservices": {
            "services": [{"is_production_ready": True}, {"is_production_ready": True}],
            "has_kubernetes": True,
        },
        "architecture_docs": ["doc.md", "adr/intro.md"],
        "git_stats": {"recent_activity_days": 30},
    }
    high_scorer = MaturityScorer(high_analysis)
    high_recommendations = high_scorer.get_recommendations()

    # Проверяем, что нет рекомендаций по основным пунктам
    high_titles = [rec["title"] for rec in high_recommendations]
    assert "Увеличить количество production-ready сервисов" not in high_titles
    assert "Добавить Kubernetes manifests" not in high_titles
