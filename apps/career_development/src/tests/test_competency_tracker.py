import unittest

from src.core.competency_tracker import CompetencyTracker
from src.core.models import UserProfile


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
        self.assertEqual(
            self.tracker.users[self.user_id]["username"], "Тестовый Пользователь"
        )
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
        self.assertEqual(
            self.tracker.competency_markers["marker_001"]["required_level"], 2
        )

    def test_update_skill_level(self):
        """Тест обновления уровня навыка"""
        self.tracker.add_skill(self.user_id, "Python", 2)
        self.tracker.update_skill_level(self.user_id, "Python", 4)

        self.assertEqual(self.tracker.users[self.user_id]["skills"]["Python"], 4)
        # Проверяем, что запись о прогрессе добавлена
        self.assertEqual(len(self.tracker.users[self.user_id]["progress_history"]), 1)

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
        self.assertEqual(len(progress), 1)
        self.assertEqual(progress[0]["skill"], "Python")
        self.assertEqual(progress[0]["from_level"], 2)
        self.assertEqual(progress[0]["to_level"], 3)

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

        self.assertEqual(report["user"]["id"], self.user_id)
        self.assertEqual(report["user"]["username"], "Тестовый Пользователь")
        self.assertGreaterEqual(report["total_skills"], 1)
        self.assertIsNotNone(report["next_milestones"])


if __name__ == "__main__":
    unittest.main()
