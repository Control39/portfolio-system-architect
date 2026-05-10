"""
Integration tests for CareerTracker

Тестирует реальную логику без моков (кроме внешних зависимостей).
Цель: повысить покрытие с 0% до 60%+ для tracker.py

Coverage targets:
- analyze_competencies()
- identify_skill_gap()
- generate_career_path()
- calculate_progress()
- save/load progress
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Импортируем реальный класс
from apps.it_compass.src.core.tracker import CareerTracker


class TestCareerTrackerIntegration:
    """Integration tests for CareerTracker real logic"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create tracker with temporary data directory"""
        data_dir = tmp_path / "markers"
        data_dir.mkdir()
        
        # Создаём тестовые маркеры
        (data_dir / "python_basics.md").write_text(
            "id: python_basics\n"
            "skill: Python\n"
            "level: junior\n"
            "priority: high\n"
            "description: Базовый синтаксис Python\n"
        )
        (data_dir / "docker_basics.md").write_text(
            "id: docker_basics\n"
            "skill: Docker\n"
            "level: junior\n"
            "priority: high\n"
            "description: Создание Dockerfile\n"
        )
        (data_dir / "k8s_advanced.md").write_text(
            "id: k8s_advanced\n"
            "skill: Kubernetes\n"
            "level: senior\n"
            "priority: medium\n"
            "description: Настройка кластера K8s\n"
        )
        
        tracker = CareerTracker(data_path=str(data_dir))
        return tracker

    def test_analyze_competencies_basic(self, tracker):
        """Базовый анализ компетенций"""
        result = tracker.analyze_competencies(
            current_skills=["Python", "Git"],
            target_level="junior"
        )
        
        assert result is not None
        assert "score" in result
        assert "gap_analysis" in result
        assert "recommendations" in result
        assert result["score"] >= 0
        assert result["score"] <= 100

    def test_identify_skill_gap(self, tracker):
        """Выявление пробелов в навыках"""
        gap = tracker.identify_skill_gap(
            current=["Python", "Docker"],
            target=["Python", "Docker", "Kubernetes", "AWS"]
        )
        
        assert gap is not None
        assert "missing_skills" in gap
        assert "ready_skills" in gap
        assert "Kubernetes" in gap["missing_skills"]
        assert "AWS" in gap["missing_skills"]
        assert "Python" in gap["ready_skills"]
        assert "Docker" in gap["ready_skills"]

    def test_generate_career_path(self, tracker):
        """Генерация карьерного пути"""
        path = tracker.generate_career_path(
            current_role="Junior Developer",
            target_role="Senior DevOps Engineer",
            timeline_months=24
        )
        
        assert path is not None
        assert "steps" in path
        assert "estimated_time" in path
        assert len(path["steps"]) > 0
        assert path["estimated_time"]["months"] <= 24

    def test_calculate_progress_with_completed(self, tracker):
        """Расчёт прогресса с выполненными маркерами"""
        # Помечаем некоторые маркеры как выполненные
        tracker.progress["completed_markers"] = ["python_basics"]
        
        progress = tracker.calculate_progress()
        
        assert progress is not None
        assert "total_markers" in progress
        assert "completed_markers" in progress
        assert "overall_percentage" in progress
        assert progress["completed_markers"] == 1
        assert progress["overall_percentage"] > 0

    def test_get_high_priority_markers(self, tracker):
        """Получение высокоприоритетных маркеров"""
        markers = tracker.get_high_priority_markers()
        
        assert markers is not None
        assert len(markers) > 0
        # python_basics и docker_basics имеют priority: high
        marker_ids = [m.id for m in markers]
        assert "python_basics" in marker_ids
        assert "docker_basics" in marker_ids

    def test_save_and_load_progress(self, tracker, tmp_path):
        """Сохранение и загрузка прогресса"""
        # Сохраняем прогресс
        tracker.progress["completed_markers"] = ["python_basics"]
        tracker.progress["last_updated"] = "2026-05-10"
        
        save_path = tmp_path / "progress.json"
        tracker.save_progress(str(save_path))
        
        # Проверяем, что файл создан
        assert save_path.exists()
        
        # Загружаем прогресс
        loaded_tracker = CareerTracker(data_path=str(tmp_path / "markers"))
        loaded_tracker.load_progress(str(save_path))
        
        assert loaded_tracker.progress["completed_markers"] == ["python_basics"]
        assert loaded_tracker.progress["last_updated"] == "2026-05-10"

    def test_analyze_competencies_with_empty_skills(self, tracker):
        """Анализ при пустом списке навыков"""
        result = tracker.analyze_competencies(
            current_skills=[],
            target_level="junior"
        )
        
        assert result is not None
        assert result["score"] == 0
        assert len(result["recommendations"]) > 0

    def test_identify_skill_gap_empty(self, tracker):
        """Выявление пробелов при полном совпадении"""
        gap = tracker.identify_skill_gap(
            current=["Python", "Docker"],
            target=["Python", "Docker"]
        )
        
        assert gap is not None
        assert len(gap["missing_skills"]) == 0
        assert len(gap["ready_skills"]) == 2

    def test_get_markers_by_level(self, tracker):
        """Получение маркеров по уровню"""
        junior_markers = tracker.get_markers_by_level("junior")
        senior_markers = tracker.get_markers_by_level("senior")
        
        assert len(junior_markers) == 2  # python_basics, docker_basics
        assert len(senior_markers) == 1  # k8s_advanced

    def test_mark_as_completed(self, tracker):
        """Отметка маркера как выполненного"""
        initial_count = len(tracker.progress["completed_markers"])
        
        tracker.mark_as_completed("python_basics")
        
        assert "python_basics" in tracker.progress["completed_markers"]
        assert len(tracker.progress["completed_markers"]) == initial_count + 1

    def test_get_skill_recommendations(self, tracker):
        """Получение рекомендаций по навыку"""
        recommendations = tracker.get_skill_recommendations("Python")
        
        assert recommendations is not None
        assert isinstance(recommendations, list)

    def test_calculate_progress_all_completed(self, tracker):
        """Прогресс при выполнении всех маркеров"""
        tracker.progress["completed_markers"] = [
            "python_basics",
            "docker_basics",
            "k8s_advanced"
        ]
        
        progress = tracker.calculate_progress()
        
        assert progress["overall_percentage"] == 100
        assert progress["completed_markers"] == 3

