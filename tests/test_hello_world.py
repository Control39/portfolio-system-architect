"""
Тесты для hello_world.py
"""

import unittest
from hello_world import greet

class TestGreet(unittest.TestCase):
    """Тесты для функции greet."""
    
    def test_greet_default(self) -> None:
        """Проверка приветствия по умолчанию."""
        self.assertEqual(greet(), "Hello, World!")
    
    def test_greet_custom_name(self) -> None:
        """Проверка приветствия с именем."""
        self.assertEqual(greet("Alice"), "Hello, Alice!")
    
    def test_greet_empty_name(self) -> None:
        """Проверка приветствия с пустым именем."""
        self.assertEqual(greet("").strip(), "Hello,!")


def suite() -> unittest.TestSuite:
    """Создает набор тестов."""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGreet))
    return test_suite


def run_tests() -> None:
    """Запускает тесты."""
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    runner.run(test_suite)


if __name__ == "__main__":
    run_tests()