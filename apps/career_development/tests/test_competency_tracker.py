import sys
import unittest
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.career_development.src.core.competency_tracker import CompetencyTracker  # noqa: E402
from apps.career_development.src.core.models import UserProfile  # noqa: E402


class TestCompetencyTracker(unittest.TestCase):
    def setUp(self):
        """Настройка тестового окружения"""
        # Создаем профиль пользователя для теста
        self.profile = UserProfile(
            id="user_001",
            username="Тестовый Пользователь",
            email="test@example.com",
            skills=[],
            level=1,
            completed_markers=[],
        )
        self.tracker = CompetencyTracker(profile=self.profile)
        self.user_id = "user_001"

        # Добавляем тестового пользователя
        self.tracker.add_user(self.user_id, "Тестовый Пользователь", "test@example.com")

        # Добавляем тестовые маркеры компетенций
        self.tracker.add_competency_marker(
            "marker_001",
            "Основы программирования",
            "Понимание базовых концепций программирования",
            2,
        )
        self.tracker.add_competency_marker(
            "marker_002",
            "Продвинутые алгоритмы",
            "Знание сложных алгоритмов и структур данных",
            4,
        )

    def test_add_user(self):
        """Тест добавления пользователя"""
        self.assertIn(self.user_id, self.tracker.users)
        self.assertEqual(self.tracker.users[self.user_id]["username"], "Тестовый Пользователь")
        self.assertEqual(self.tracker.users[self.user_id]["email"], "test@example.com")

    def test_add_skill(self):
        """Тест добавления навыка"""
        self.tracker.add_skill(self.user_id, "Python", 3)
        self.assertIn("Python", self.tracker.users[self.user_id]["skills"])
        self.assertEqual(self.tracker.users[self.user_id]["skills"]["Python"], 3)

    def test_add_skill_nonexistent_user(self):
        """Тест добавления навыка несуществующему пользователю"""
        with self.assertRaises(ValueError):
            self.tracker.add_skill("nonexistent_user", "Python", 3)

    def test_add_competency_marker(self):
        """Тест добавления маркера компетенции"""
        self.assertIn("marker_001", self.tracker.competency_markers)
        self.assertEqual(
            self.tracker.competency_markers["marker_001"]["title"],
            "Основы программирования",
        )
        self.assertEqual(self.tracker.competency_markers["marker_001"]["required_level"], 2)

    def test_update_skill_level(self):
        """Тест обновления уровня навыка"""
        self.tracker.add_skill(self.user_id, "Python", 2)
        self.tracker.update_skill_level(self.user_id, "Python", 4)

        self.assertEqual(self.tracker.users[self.user_id]["skills"]["Python"], 4)
        # Проверяем, что записи о прогрессе добавлены (2 записи: add + update)
        self.assertEqual(len(self.tracker.users[self.user_id]["progress_history"]), 2)

    def test_update_skill_level_nonexistent_user(self):
        """Тест обновления уровня навыка несуществующего пользователя"""
        with self.assertRaises(ValueError):
            self.tracker.update_skill_level("nonexistent_user", "Python", 3)

    def test_update_skill_level_nonexistent_skill(self):
        """Тест обновления уровня несуществующего навыка"""
        with self.assertRaises(ValueError):
            self.tracker.update_skill_level(self.user_id, "NonexistentSkill", 3)

    def test_get_user_skills(self):
        """Тест получения навыков пользователя"""
        self.tracker.add_skill(self.user_id, "Python", 3)
        self.tracker.add_skill(self.user_id, "JavaScript", 2)

        skills = self.tracker.get_user_skills(self.user_id)
        self.assertEqual(len(skills), 2)
        self.assertIn("Python", skills)
        self.assertIn("JavaScript", skills)

    def test_get_user_progress(self):
        """Тест получения истории прогресса пользователя"""
        self.tracker.add_skill(self.user_id, "Python", 2)
        self.tracker.update_skill_level(self.user_id, "Python", 3)

        progress = self.tracker.get_user_progress(self.user_id)
        self.assertEqual(progress["total_skills"], 1)
        self.assertIn("skills", progress)
        self.assertIn("history", progress)
        self.assertEqual(len(progress["history"]), 2)  # add + update

    def test_check_competency_achievement(self):
        """Тест проверки достижения маркеров компетенций"""
        self.tracker.add_skill(self.user_id, "Программирование", 3)

        achieved_markers = self.tracker.check_competency_achievement(self.user_id)
        # Проверяем, что достигнут хотя бы один маркер (требует уровень 2)
        self.assertGreater(len(achieved_markers), 0)

    def test_generate_progress_report(self):
        """Тест генерации отчета о прогрессе"""
        self.tracker.add_skill(self.user_id, "Python", 3)
        self.tracker.update_skill_level(self.user_id, "Python", 4)

        report = self.tracker.generate_progress_report(self.user_id)

        self.assertIsInstance(report, str)
        self.assertIn(self.user_id, report)
        self.assertIn("Progress", report)
        self.assertIn("Skills", report)
        self.assertIn("Competencies", report)

    def test_update_marker_found(self):
        """Тест обновления маркера (найден)"""
        # Добавляем маркер в профиль
        from apps.career_development.src.core.models import CompetencyMarker, Skill

        marker = CompetencyMarker(
            id="marker_003",
            title="Test",
            validation="test",
            priority="high",
            skill_name="Python",
            status="pending",
        )
        skill = Skill(name="Python", markers=[marker], progress=0, status="in_progress")
        self.profile.skills.append(skill)

        result = self.tracker.update_marker("marker_003", "completed")
        self.assertTrue(result)
        self.assertEqual(marker.status, "completed")

    def test_update_marker_not_found(self):
        """Тест обновления маркера (не найден)"""
        result = self.tracker.update_marker("nonexistent_marker", "completed")
        self.assertFalse(result)

    def test_calculate_progress_no_markers(self):
        """Тест расчёта прогресса без маркеров"""
        progress = self.tracker.calculate_progress()
        self.assertEqual(progress, 0.0)

    def test_calculate_progress_with_markers(self):
        """Тест расчёта прогресса с маркерами"""
        from apps.career_development.src.core.models import CompetencyMarker, Skill

        # Создаём маркеры
        marker1 = CompetencyMarker(
            id="m1",
            title="Test1",
            validation="test",
            priority="high",
            skill_name="Python",
            status="completed",
        )
        marker2 = CompetencyMarker(
            id="m2",
            title="Test2",
            validation="test",
            priority="high",
            skill_name="Python",
            status="pending",
        )
        skill = Skill(name="Python", markers=[marker1, marker2], progress=0, status="in_progress")
        self.profile.skills.append(skill)

        progress = self.tracker.calculate_progress()
        self.assertEqual(progress, 50.0)  # 1 из 2 завершено

    def test_list_pending_markers_empty(self):
        """Тест списка pending маркеров (пусто)"""
        pending = self.tracker.list_pending_markers()
        self.assertEqual(len(pending), 0)

    def test_list_pending_markers_with_pending(self):
        """Тест списка pending маркеров (с pending)"""
        from apps.career_development.src.core.models import CompetencyMarker, Skill

        marker1 = CompetencyMarker(
            id="m1",
            title="Test1",
            validation="test",
            priority="high",
            skill_name="Python",
            status="completed",
        )
        marker2 = CompetencyMarker(
            id="m2",
            title="Test2",
            validation="test",
            priority="high",
            skill_name="Python",
            status="pending",
        )
        skill = Skill(name="Python", markers=[marker1, marker2], progress=0, status="in_progress")
        self.profile.skills.append(skill)

        pending = self.tracker.list_pending_markers()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, "m2")

    def test_get_user_progress_nonexistent_user(self):
        """Тест получения прогресса несуществующего пользователя"""
        with self.assertRaises(ValueError):
            self.tracker.get_user_progress("nonexistent_user")

    def test_check_competency_achievement_nonexistent_user(self):
        """Тест проверки достижения несуществующего пользователя"""
        with self.assertRaises(ValueError):
            self.tracker.check_competency_achievement("nonexistent_user")

    def test_get_user_skills_nonexistent_user(self):
        """Тест получения навыков несуществующего пользователя"""
        with self.assertRaises(ValueError):
            self.tracker.get_user_skills("nonexistent_user")


if __name__ == "__main__":
    unittest.main()
