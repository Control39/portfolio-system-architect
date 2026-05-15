"""Tests for src/utils/helpers.py"""

import sys
import unittest
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.career_development.src.utils.helpers import generate_id, validate_evidence_link  # noqa: E402


class TestHelpers(unittest.TestCase):
    """Тесты вспомогательных функций"""

    def test_generate_id_returns_string(self):
        """Тест генерации ID возвращает строку"""
        result = generate_id()
        self.assertIsInstance(result, str)

    def test_generate_id_is_uuid_format(self):
        """Тест формата UUID"""
        result = generate_id()
        # UUID v4 имеет формат 8-4-4-4-12
        parts = result.split("-")
        self.assertEqual(len(parts), 5)
        self.assertEqual(len(parts[0]), 8)
        self.assertEqual(len(parts[1]), 4)
        self.assertEqual(len(parts[2]), 4)
        self.assertEqual(len(parts[3]), 4)
        self.assertEqual(len(parts[4]), 12)

    def test_generate_id_is_unique(self):
        """Тест уникальности ID"""
        id1 = generate_id()
        id2 = generate_id()
        self.assertNotEqual(id1, id2)

    def test_validate_evidence_link_http(self):
        """Тест валидации HTTP ссылки"""
        self.assertTrue(validate_evidence_link("http://example.com"))

    def test_validate_evidence_link_https(self):
        """Тест валидации HTTPS ссылки"""
        self.assertTrue(validate_evidence_link("https://example.com"))

    def test_validate_evidence_link_with_path(self):
        """Тест валидации ссылки с путём"""
        self.assertTrue(validate_evidence_link("https://example.com/path/to/resource"))

    def test_validate_evidence_link_invalid_no_protocol(self):
        """Тест невалидной ссылки без протокола"""
        self.assertFalse(validate_evidence_link("example.com"))

    def test_validate_evidence_link_invalid_empty(self):
        """Тест невалидной пустой ссылки"""
        self.assertFalse(validate_evidence_link(""))

    def test_validate_evidence_link_invalid_ftp(self):
        """Тест невалидной FTP ссылки"""
        self.assertFalse(validate_evidence_link("ftp://example.com"))


if __name__ == "__main__":
    unittest.main()
