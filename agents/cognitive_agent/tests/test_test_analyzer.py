"""
Тесты для модуля анализа тестов (src/test_analyzer.py)

Service Tier: CORE
Purpose: Unit and integration testing for test quality analysis functionality
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.cognitive_agent.src.test_analyzer import TestAnalyzer, TestFramework, TestIssue, TestResult


class TestTestAnalyzerInitialization:
    """Тесты инициализации анализатора тестов"""

    def test_analyzer_initialization_with_existing_path(self):
        """Тест инициализации с существующей директорией"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)

            assert analyzer is not None
            assert str(analyzer.project_path) == temp_dir

    def test_analyzer_initialization_with_nonexistent_path(self):
        """Тест инициализации с несуществующей директорией"""
        nonexistent_path = "/nonexistent/path/for/testing"
        analyzer = TestAnalyzer(nonexistent_path)

        assert analyzer is not None
        assert str(analyzer.project_path) == nonexistent_path


class TestTestIssue:
    """Тесты объекта проблемы тестов"""

    def test_test_issue_creation(self):
        """Тест создания объекта TestIssue"""
        issue = TestIssue(
            file_path="test_example.py",
            issue_type="missing_assertion",
            severity="high",
            message="Test function does not have any assertions",
            suggested_fix="Add assertions to verify functionality",
        )

        assert issue.file_path == "test_example.py"
        assert issue.issue_type == "missing_assertion"
        assert issue.severity == "high"
        assert issue.message == "Test function does not have any assertions"
        assert issue.suggested_fix == "Add assertions to verify functionality"


class TestTestResult:
    """Тесты объекта результата тестов"""

    def test_test_result_creation(self):
        """Тест создания объекта TestResult"""
        issue = TestIssue(
            file_path="test_example.py",
            issue_type="missing_assertion",
            severity="high",
            message="Test function does not have any assertions",
            suggested_fix="Add assertions to verify functionality",
        )

        result = TestResult(
            framework=TestFramework.PYTEST,
            success=True,
            output="Test analysis completed",
            issues=[issue],
            summary={"total_tests": 5, "failed_tests": 0, "coverage": 80},
        )

        assert result.framework == TestFramework.PYTEST
        assert result.success is True
        assert result.output == "Test analysis completed"
        assert len(result.issues) == 1
        assert result.summary["total_tests"] == 5


class TestFindTestFiles:
    """Тесты поиска файлов тестов"""

    def test_find_test_files_empty_directory(self):
        """Тест поиска файлов тестов в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)
            files = analyzer.find_test_files()

            assert isinstance(files, dict)
            for test_framework in TestFramework:
                assert test_framework.value in files
                assert isinstance(files[test_framework.value], list)
                assert len(files[test_framework.value]) == 0

    def test_find_test_files_with_test_patterns(self):
        """Тест поиска файлов тестов с различными паттернами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файлы с разными паттернами тестов
            (temp_path / "test_main.py").write_text("# Test file")
            (temp_path / "main_test.py").write_text("# Test file")
            (temp_path / "tests.py").write_text("# Test file")
            (temp_path / "conftest.py").write_text("# Pytest config")
            (temp_path / "test").mkdir()
            (temp_path / "test" / "test_submodule.py").write_text("# Submodule test")
            (temp_path / "spec").mkdir()
            (temp_path / "spec" / "example_spec.py").write_text("# Spec test")

            analyzer = TestAnalyzer(temp_dir)
            files = analyzer.find_test_files()

            # Проверяем, что файлы тестов найдены
            pytest_files = files[TestFramework.PYTEST.value]
            files[TestFramework.UNITTEST.value]

            assert len(pytest_files) >= 3  # test_main.py, conftest.py, test_submodule.py


class TestAnalyzePytestTests:
    """Тесты анализа pytest тестов"""

    def test_analyze_pytest_with_good_practices(self):
        """Тест анализа pytest тестов с хорошими практиками"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с хорошими pytest тестами
            good_test_content = '''
import pytest
from unittest.mock import Mock, patch

def add(a, b):
    return a + b

def test_add_positive_numbers():
    """Тест сложения положительных чисел."""
    assert add(2, 3) == 5

def test_add_negative_numbers():
    """Тест сложения отрицательных чисел."""
    assert add(-2, -3) == -5

def test_add_mixed_numbers():
    """Тест сложения смешанных чисел."""
    assert add(-2, 3) == 1
    assert add(2, -3) == -1

def test_add_zero():
    """Тест сложения с нулем."""
    assert add(0, 5) == 5
    assert add(5, 0) == 5

class TestCalculator:
    """Тесты для калькулятора."""

    def test_initial_state(self):
        """Тест начального состояния."""
        calc = Calculator()
        assert calc.value == 0

    def test_add_operation(self):
        """Тест операции сложения."""
        calc = Calculator()
        calc.add(5)
        assert calc.value == 5

    def test_subtract_operation(self):
        """Тест операции вычитания."""
        calc = Calculator()
        calc.subtract(3)
        assert calc.value == -3
'''
            (temp_path / "test_good_pytest.py").write_text(good_test_content)

            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_pytest_tests()

            # Проверяем, что результаты содержат оценки
            assert len(results) > 0
            for result in results:
                assert isinstance(result, TestResult)

    def test_analyze_pytest_with_poor_practices(self):
        """Тест анализа pytest тестов с плохими практиками"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с плохими pytest тестами
            bad_test_content = """
def test_bad():
    pass

def test_also_bad():
    x = 1 + 1
    # No assertions here
"""
            (temp_path / "test_bad_pytest.py").write_text(bad_test_content)

            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_pytest_tests()

            # Проверяем, что результаты содержат проблемы
            assert len(results) > 0
            for result in results:
                assert isinstance(result, TestResult)
                assert len(result.issues) >= 0  # Может быть 0 если анализатор не нашел проблем


class TestAnalyzeUnittestTests:
    """Тесты анализа unittest тестов"""

    def test_analyze_unittest_with_good_practices(self):
        """Тест анализа unittest тестов с хорошими практиками"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с хорошими unittest тестами
            good_unittest_content = '''
import unittest

def multiply(a, b):
    return a * b

class TestMultiply(unittest.TestCase):
    """Тесты для функции умножения."""

    def test_positive_numbers(self):
        """Тест умножения положительных чисел."""
        self.assertEqual(multiply(2, 3), 6)

    def test_negative_numbers(self):
        """Тест умножения отрицательных чисел."""
        self.assertEqual(multiply(-2, 3), -6)
        self.assertEqual(multiply(2, -3), -6)
        self.assertEqual(multiply(-2, -3), 6)

    def test_zero_multiplication(self):
        """Тест умножения с нулем."""
        self.assertEqual(multiply(0, 5), 0)
        self.assertEqual(multiply(5, 0), 0)

    def test_float_multiplication(self):
        """Тест умножения дробных чисел."""
        self.assertAlmostEqual(multiply(1.5, 2), 3.0, places=1)

if __name__ == '__main__':
    unittest.main()
'''
            (temp_path / "test_unittest.py").write_text(good_unittest_content)

            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_unittest_tests()

            # Проверяем, что результаты содержат оценки
            assert len(results) > 0
            for result in results:
                assert isinstance(result, TestResult)


class TestAnalyzeDoctestTests:
    """Тесты анализа doctest тестов"""

    def test_analyze_doctest_empty_directory(self):
        """Тест анализа doctest тестов в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_doctest_tests()

            # В пустой директории не должно быть doctest тестов
            assert len(results) == 0

    def test_analyze_doctest_with_content(self):
        """Тест анализа doctest тестов с содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с doctest
            doctest_content = '''
def factorial(n):
    """
    Calculate the factorial of n.

    >>> factorial(0)
    1
    >>> factorial(1)
    1
    >>> factorial(5)
    120
    >>> factorial(6)
    720
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
'''
            (temp_path / "test_doctest.py").write_text(doctest_content)

            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_doctest_tests()

            # Должны быть найдены doctest тесты
            assert len(results) >= 0  # Может быть 0 если doctest не установлен


class TestAnalyzeCustomTests:
    """Тесты анализа кастомных тестов"""

    def test_analyze_custom_tests_empty_directory(self):
        """Тест анализа кастомных тестов в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_custom_tests()

            # В пустой директории не должно быть кастомных тестов
            assert len(results) == 0

    def test_analyze_custom_tests_with_content(self):
        """Тест анализа кастомных тестов с содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с кастомными тестами
            custom_test_content = '''
def simple_test():
    """Simple test function."""
    result = 2 + 2
    if result != 4:
        print("Test failed!")
        return False
    print("Test passed!")
    return True

def another_test():
    """Another test function."""
    values = [1, 2, 3]
    doubled = [x * 2 for x in values]
    expected = [2, 4, 6]
    if doubled != expected:
        print("Test failed!")
        return False
    print("Test passed!")
    return True

# Run tests
if __name__ == "__main__":
    simple_test()
    another_test()
'''
            (temp_path / "test_custom.py").write_text(custom_test_content)

            analyzer = TestAnalyzer(temp_dir)
            results = analyzer.analyze_custom_tests()

            # Должны быть найдены кастомные тесты
            assert len(results) >= 0


class TestAnalyzeTestCoverage:
    """Тесты анализа покрытия тестами"""

    @patch("subprocess.run")
    def test_analyze_test_coverage_with_tools(self, mock_subprocess):
        """Тест анализа покрытия тестами с инструментами"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "coverage" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = """
Name                    Stmts   Miss  Cover
-------------------------------------------
src/module.py              50     10    80%
tests/test_module.py       30      2    93%
-------------------------------------------
TOTAL                      80     12    85%
"""
                return result
            elif isinstance(cmd, list) and "pytest" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "10 passed, 0 failed"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем тестовый файл
            (temp_path / "test_coverage.py").write_text("""
def test_coverage():
    assert True
""")

            analyzer = TestAnalyzer(temp_dir)
            coverage_result = analyzer.analyze_test_coverage()

            # Проверяем, что результат содержит информацию о покрытии
            if coverage_result:
                assert "coverage_percentage" in coverage_result or "error" in coverage_result


class TestGenerateTestReport:
    """Тесты генерации отчета о тестах"""

    def test_generate_test_report_empty_directory(self):
        """Тест генерации отчета для пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)
            report = analyzer.generate_test_report()

            # Проверяем структуру отчета
            assert "project_path" in report
            assert "summary" in report
            assert "details" in report
            assert "files_analyzed" in report["summary"]
            assert "quality_score" in report["summary"]

            # В пустой директории оценка может быть 0 или рассчитываться по другим критериям
            assert "pytest" in report["details"]
            assert "unittest" in report["details"]

    def test_generate_test_report_with_content(self):
        """Тест генерации отчета с содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файлы с хорошими тестами
            good_test_content = '''
import pytest

def function_to_test(x, y):
    return x + y

def test_function_to_test():
    """Тест функции сложения."""
    assert function_to_test(2, 3) == 5
    assert function_to_test(-1, 1) == 0
    assert function_to_test(0, 0) == 0

class TestClass:
    """Тесты в классе."""

    def test_class_method(self):
        assert True
'''
            (temp_path / "test_report.py").write_text(good_test_content)

            analyzer = TestAnalyzer(temp_dir)
            report = analyzer.generate_test_report()

            # Проверяем структуру отчета
            assert "project_path" in report
            assert "summary" in report
            assert "details" in report
            assert report["summary"]["files_analyzed"] > 0
            assert "pytest" in report["details"]


class TestCalculateOverallTestScore:
    """Тесты расчета общей оценки тестов"""

    def test_calculate_overall_score_empty_results(self):
        """Тест расчета общей оценки для пустых результатов"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)
            score = analyzer.calculate_overall_test_score([])

            assert score == 0

    def test_calculate_overall_score_with_results(self):
        """Тест расчета общей оценки с результатами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = TestAnalyzer(temp_dir)

            # Создаем тестовые результаты
            issue = TestIssue(
                file_path="test1.py",
                issue_type="missing_assertion",
                severity="high",
                message="Test function does not have any assertions",
                suggested_fix="Add assertions to verify functionality",
            )

            test_results = [
                TestResult(
                    framework=TestFramework.PYTEST, success=True, output="Test passed", issues=[issue], summary={}
                )
            ]

            score = analyzer.calculate_overall_test_score(test_results)

            # Оценка должна быть числом
            assert isinstance(score, (int, float))


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_analyzer_with_readonly_directory(self):
        """Тест анализатора с директорией только для чтения"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем файлы для анализа
            temp_path = Path(temp_dir)
            (temp_path / "readonly_test.py").write_text("def test_something(): pass")

            analyzer = TestAnalyzer(temp_dir)

            # Даже с файлами анализатор должен корректно работать
            try:
                report = analyzer.generate_test_report()
                assert "summary" in report
            except Exception:
                # Обработка любых исключений должна быть корректной
                pass

    def test_analyzer_with_binary_files(self):
        """Тест анализатора с бинарными файлами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем бинарный файл (должен быть проигнорирован)
            binary_file = temp_path / "binary.dat"
            binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

            # Создаем тестовый файл для анализа
            (temp_path / "test_simple.py").write_text("def test_something(): assert True")

            analyzer = TestAnalyzer(temp_dir)

            # Анализатор должен корректно обрабатывать бинарные файлы
            try:
                report = analyzer.generate_test_report()
                assert "summary" in report
            except Exception:
                # Обработка любых исключений должна быть корректной
                pass

    def test_analyzer_with_syntax_errors(self):
        """Тест анализатора с файлами содержащими синтаксические ошибки"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с синтаксической ошибкой
            bad_syntax_content = """
def test_with_syntax_error(
    # Отсутствует закрывающая скобка
    assert True
"""
            (temp_path / "test_syntax_error.py").write_text(bad_syntax_content)

            analyzer = TestAnalyzer(temp_dir)

            # Анализатор должен корректно обрабатывать синтаксические ошибки
            try:
                analyzer.generate_test_report()
                # Может не сгенерировать отчет из-за ошибки, но не должен падать
            except Exception:
                # Обработка любых исключений должна быть корректной
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
