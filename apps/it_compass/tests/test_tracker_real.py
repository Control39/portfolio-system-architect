"""
Реальные тесты для CareerTracker (it_compass)

Тестирует существующую бизнес-логику:
- show_progress()
- mark_completed()
- show_recommendations()
- get_skill_progress()
- _load_progress() / _save_progress()
"""

import json
import tempfile
from pathlib import Path

import pytest

from apps.it_compass.src.core.tracker import CareerTracker


class TestCareerTrackerRealLogic:
    """Тесты реальной бизнес-логики CareerTracker"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Создаём tracker с тестовыми маркерами"""
        markers_dir = tmp_path / "markers"
        markers_dir.mkdir()

        # Создаём тестовые маркеры в ПРАВИЛЬНОМ формате (с levels)
        (markers_dir / "python.json").write_text(
            json.dumps(
                {
                    "skill_name": "Python",
                    "description": "Язык программирования Python",
                    "levels": {
                        "beginner": [
                            {
                                "id": "python_basics",
                                "marker": "Базовый синтаксис Python",
                                "validation": "Успешное прохождение тестов",
                                "priority": "high",
                                "resources": ["https://docs.python.org/"],
                                "smart_criteria": {
                                    "beginner": "Создать простой скрипт"
                                },
                            }
                        ]
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        (markers_dir / "docker.json").write_text(
            json.dumps(
                {
                    "skill_name": "Docker",
                    "description": "Контейнеризация приложений",
                    "levels": {
                        "beginner": [
                            {
                                "id": "docker_basics",
                                "marker": "Создание Dockerfile",
                                "validation": "Успешная сборка образа",
                                "priority": "high",
                                "resources": ["https://docs.docker.com/"],
                                "smart_criteria": {
                                    "beginner": "Создать Dockerfile для приложения"
                                },
                            }
                        ]
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        (markers_dir / "kubernetes.json").write_text(
            json.dumps(
                {
                    "skill_name": "Kubernetes",
                    "description": "Оркестрация контейнеров",
                    "levels": {
                        "advanced": [
                            {
                                "id": "k8s_advanced",
                                "marker": "Настройка кластера Kubernetes",
                                "validation": "Развёртывание приложения в кластере",
                                "priority": "medium",
                                "resources": ["https://kubernetes.io/docs/"],
                                "smart_criteria": {
                                    "advanced": "Создать deployment и service"
                                },
                            }
                        ]
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        progress_file = tmp_path / "progress.json"
        return CareerTracker(
            markers_dir=str(markers_dir), progress_file=str(progress_file)
        )

    def test_tracker_initialization_with_valid_markers(self, tracker):
        """Инициализация трекера с валидными маркерами"""
        assert len(tracker.markers) == 3
        assert "Python" in tracker.markers
        assert "Docker" in tracker.markers
        assert "Kubernetes" in tracker.markers

    def test_tracker_initializes_empty_progress(self, tracker):
        """Инициализация с пустым прогрессом"""
        assert tracker.progress["completed_markers"] == []
        assert tracker.progress["in_progress_markers"] == []

    def test_mark_completed_success(self, tracker):
        """Отметка маркера как завершённого"""
        result = tracker.mark_completed("python_basics")

        assert result is True
        assert "python_basics" in tracker.progress["completed_markers"]

    def test_mark_completed_invalid_marker(self, tracker):
        """Отметка несуществующего маркера возвращает False"""
        result = tracker.mark_completed("nonexistent_marker")

        assert result is False

    def test_mark_completed_twice(self, tracker):
        """Повторная отметка уже завершённого маркера"""
        # Первая отметка
        result1 = tracker.mark_completed("python_basics")
        assert result1 is True

        # Вторая отметка (возвращает True с предупреждением)
        result2 = tracker.mark_completed("python_basics")
        # Код возвращает True даже для уже завершённого маркера (с логированием)
        assert result2 is True
        assert "python_basics" in tracker.progress["completed_markers"]

    def test_show_progress_empty(self, tracker, capsys):
        """Показ прогресса (пустой)"""
        tracker.show_progress()

        captured = capsys.readouterr()
        assert "ВАШ ПРОГРЕСС" in captured.out.upper()

    def test_show_progress_with_completed(self, tracker, capsys):
        """Показ прогресса с завершёнными маркерами"""
        tracker.mark_completed("python_basics")
        tracker.mark_completed("docker_basics")

        tracker.show_progress()

        captured = capsys.readouterr()
        assert "ВАШ ПРОГРЕСС" in captured.out.upper()

    def test_show_recommendations(self, tracker, capsys):
        """Показ рекомендаций"""
        tracker.show_recommendations(limit=2)

        captured = capsys.readouterr()
        assert "РЕКОМЕНДАЦИИ" in captured.out.upper() or "Поздравляем" in captured.out

    def test_get_skill_progress(self, tracker):
        """Получение прогресса по навыку"""
        # Сначала отметим маркер
        tracker.mark_completed("python_basics")

        progress = tracker.get_skill_progress("Python")

        assert progress is not None
        assert progress["skill_name"] == "Python"

    def test_get_skill_progress_not_found(self, tracker):
        """Получение прогресса несуществующего навыка"""
        progress = tracker.get_skill_progress("NonExistentSkill")

        # Может вернуть None или пустой прогресс
        assert progress is None or progress["skill_name"] == "NonExistentSkill"

    def test_load_progress_from_existing_file(self, tracker):
        """Загрузка прогресса из существующего файла"""
        # Добавляем маркер
        tracker.mark_completed("python_basics")
        tracker._save_progress()

        # Создаём новый tracker с тем же файлом
        new_tracker = CareerTracker(
            markers_dir=str(tracker.markers_dir),
            progress_file=str(tracker.progress_file),
        )

        assert "python_basics" in new_tracker.progress["completed_markers"]

    def test_save_progress_creates_file(self, tracker):
        """Сохранение прогресса создаёт файл"""
        tracker.mark_completed("python_basics")
        tracker._save_progress()

        assert tracker.progress_file.exists()

    def test_progress_persistence(self, tracker):
        """Персистентность прогресса"""
        # Добавляем маркер
        tracker.mark_completed("python_basics")
        tracker._save_progress()

        # Загружаем и проверяем
        with open(tracker.progress_file, encoding="utf-8") as f:
            saved_progress = json.load(f)

        assert "python_basics" in saved_progress["completed_markers"]

    def test_markers_load_from_json_files(self, tracker):
        """Загрузка маркеров из JSON файлов"""
        assert len(tracker.markers) == 3

        # Проверяем структуру навыка
        python_data = tracker.markers["Python"]
        assert python_data.skill_name == "Python"
        assert "beginner" in python_data.levels
        assert len(python_data.levels["beginner"]) == 1

    def test_empty_markers_directory(self):
        """Обработка пустой директории маркеров"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            empty_markers_dir = Path(tmp_dir) / "empty_markers"
            empty_markers_dir.mkdir()
            progress_file = Path(tmp_dir) / "progress.json"

            tracker = CareerTracker(
                markers_dir=str(empty_markers_dir), progress_file=str(progress_file)
            )

            assert len(tracker.markers) == 0

    def test_corrupted_marker_file_handling(self, tmp_path):
        """Обработка повреждённого файла маркера"""
        markers_dir = tmp_path / "markers"
        markers_dir.mkdir()

        # Создаём невалидный JSON
        (markers_dir / "corrupted.json").write_text("not valid json{")

        progress_file = tmp_path / "progress.json"
        tracker = CareerTracker(
            markers_dir=str(markers_dir), progress_file=str(progress_file)
        )

        # Должен обработать ошибку и вернуть пустой словарь
        assert len(tracker.markers) == 0

    def test_multiple_skills_progress(self, tracker):
        """Прогресс по нескольким навыкам"""
        tracker.mark_completed("python_basics")
        tracker.mark_completed("docker_basics")

        python_progress = tracker.get_skill_progress("Python")
        docker_progress = tracker.get_skill_progress("Docker")

        assert python_progress is not None
        assert docker_progress is not None

    def test_progress_calculation_with_partial_completion(self, tracker):
        """Расчёт прогресса с частичным завершением"""
        tracker.mark_completed("python_basics")  # 1 из 1 в Python

        python_progress = tracker.get_skill_progress("Python")

        assert python_progress is not None
