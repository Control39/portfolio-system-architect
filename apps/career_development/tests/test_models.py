"""Tests for src/core/models.py"""

import sys
import unittest
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.career_development.src.core.models import CompetencyMarker, Skill, UserProfile  # noqa: E402


class TestModels(unittest.TestCase):
    """Тесты моделей данных"""

    def test_competency_marker_creation(self):
        """Тест создания CompetencyMarker"""
        marker = CompetencyMarker(
            id="test_001",
            title="Test Marker",
            status="pending",
            evidence_url="https://example.com",
        )
        self.assertEqual(marker.id, "test_001")
        self.assertEqual(marker.title, "Test Marker")
        self.assertEqual(marker.status, "pending")

    def test_skill_creation(self):
        """Тест создания Skill"""
        skill = Skill(name="Python", level=3, markers=[])
        self.assertEqual(skill.name, "Python")
        self.assertEqual(skill.level, 3)

    def test_user_profile_creation(self):
        """Тест создания UserProfile"""
        profile = UserProfile(
            username="TestUser",
            skills=[],
            goals=[],
            achievements=[],
        )
        self.assertEqual(profile.username, "TestUser")
        self.assertEqual(profile.skills, [])


if __name__ == "__main__":
    unittest.main()
