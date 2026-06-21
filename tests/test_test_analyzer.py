"""
Тесты для модуля анализа тестов
"""

import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.test_analyzer import TestAnalyzer, TestFramework


def test_test_analyzer_initialization():
    """Тест инициализации анализатора тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = TestAnalyzer(temp_dir)

        # Проверяем, что анализатор инициализировался
        assert analyzer is not None
        assert hasattr(analyzer, "project_path")
        assert hasattr(analyzer, "test_files")
        assert hasattr(analyzer, "framework")

        # Проверяем, что test_files - это список
        assert isinstance(analyzer.test_files, list)

        # Проверяем, что framework - это enum TestFramework
        assert isinstance(analyzer.framework, TestFramework)


def test_find_test_files():
    """Тест поиска файлов тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем несколько файлов тестов
        Path(temp_dir, "test_module.py").write_text("def test_func(): pass")
        Path(temp_dir, "example_test.py").write_text("def test_example(): pass")

        # Создаем директорию tests
        tests_dir = Path(temp_dir, "tests")
        tests_dir.mkdir()
        Path(tests_dir, "test_sample.py").write_text("def test_sample(): pass")

        analyzer = TestAnalyzer(temp_dir)
        test_files = analyzer.test_files

        # Проверяем, что найдены все файлы тестов
        file_names = [f.name for f in test_files]
        assert "test_module.py" in file_names
        assert "example_test.py" in file_names
        assert "test_sample.py" in file_names


def test_detect_test_framework():
    """Тест определения фреймворка тестирования"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файл с pytest
        pytest_file = Path(temp_dir, "test_with_pytest.py")
        pytest_file.write_text("""
import pytest

def test_with_pytest():
    assert True
""")

        analyzer = TestAnalyzer(temp_dir)

        # Проверяем, что определен pytest
        assert analyzer.framework == TestFramework.PYTEST


def test_analyze_test_structure():
    """Тест анализа структуры тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файл с тестами
        test_file = Path(temp_dir, "test_sample.py")
        test_file.write_text("""
def test_simple_function():
    assert True

def test_with_multiple_asserts():
    assert 1 == 1
    assert "hello" == "hello"

class TestClass:
    def test_method(self):
        assert True
""")

        analyzer = TestAnalyzer(temp_dir)
        structure_analysis = analyzer.analyze_test_structure()

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(structure_analysis, dict)
        assert "total_test_files" in structure_analysis
        assert "framework_detected" in structure_analysis
        assert "test_file_organization" in structure_analysis
        assert isinstance(structure_analysis["test_file_organization"], dict)


def test_analyze_test_quality():
    """Тест анализа качества тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файл с разными типами тестов
        test_file = Path(temp_dir, "test_quality.py")
        test_file.write_text("""
def test_with_assert():
    assert True

def test_without_assert():
    x = 1 + 1
    # Этот тест не содержит assert

def test_long_but_valid():
    # Длинный тест, но с assert
    for i in range(10):
        assert i >= 0
""")

        analyzer = TestAnalyzer(temp_dir)
        quality_issues = analyzer.analyze_test_quality()

        # Проверяем, что результат содержит список проблем
        assert isinstance(quality_issues, list)

        # Проверяем, что обнаружена проблема с отсутствием assert в одном из тестов
        no_assert_issues = [issue for issue in quality_issues if issue.issue_type == "no_assertions"]
        assert len(no_assert_issues) >= 1


def test_run_test_analysis():
    """Тест полного анализа тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файлы для анализа
        test_file = Path(temp_dir, "test_sample.py")
        test_file.write_text("""
def test_simple():
    assert True
""")

        analyzer = TestAnalyzer(temp_dir)
        full_analysis = analyzer.run_test_analysis()

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(full_analysis, dict)
        assert "project_path" in full_analysis
        assert "framework_detected" in full_analysis
        assert "total_test_files" in full_analysis
        assert "structure_analysis" in full_analysis
        assert "coverage_analysis" in full_analysis
        assert "quality_issues" in full_analysis
        assert "summary" in full_analysis


def test_generate_test_improvement_plan():
    """Тест генерации плана улучшения тестов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файлы для анализа
        test_file = Path(temp_dir, "test_sample.py")
        test_file.write_text("""
def test_simple():
    assert True
""")

        analyzer = TestAnalyzer(temp_dir)
        analysis_results = analyzer.run_test_analysis()
        improvements = analyzer.generate_test_improvement_plan(analysis_results)

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(improvements, dict)
        assert "timestamp" in improvements
        assert "project_path" in improvements
        assert "framework_detected" in improvements
        assert "recommendations" in improvements
        assert "priority_actions" in improvements
        assert "implementation_guide" in improvements


def test_analyze_test_coverage():
    """Тест анализа покрытия тестами"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем простой тестовый файл
        test_file = Path(temp_dir, "test_sample.py")
        test_file.write_text("""
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
""")

        analyzer = TestAnalyzer(temp_dir)
        coverage_analysis = analyzer.analyze_test_coverage()

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(coverage_analysis, dict)
        assert "framework" in coverage_analysis
        assert "coverage_available" in coverage_analysis
        assert "total_coverage" in coverage_analysis


if __name__ == "__main__":
    pytest.main([__file__])
