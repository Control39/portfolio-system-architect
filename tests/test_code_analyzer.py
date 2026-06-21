"""
Тесты для модуля анализа качества кода
"""

import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.code_analyzer import AnalysisTool, CodeAnalyzer


def test_code_analyzer_initialization():
    """Тест инициализации анализатора кода"""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = CodeAnalyzer(temp_dir)

        # Проверяем, что анализатор инициализировался
        assert analyzer is not None
        assert hasattr(analyzer, "project_path")
        assert hasattr(analyzer, "tools_available")

        # Проверяем, что tools_available - это словарь
        assert isinstance(analyzer.tools_available, dict)

        # Проверяем, что все ожидаемые инструменты присутствуют в словаре
        for tool in AnalysisTool:
            assert tool in analyzer.tools_available


def test_code_analyzer_with_empty_project():
    """Тест анализатора кода с пустым проектом"""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = CodeAnalyzer(temp_dir)

        # Должен успешно выполнить анализ даже для пустого проекта
        report = analyzer.generate_quality_report()

        # Проверяем, что отчет содержит ожидаемые поля
        assert "project_path" in report
        assert "tools_run" in report
        assert "tools_available" in report
        assert "results" in report
        assert "summary" in report

        # Путь к проекту должен совпадать
        assert report["project_path"] == temp_dir


def test_code_analyzer_with_python_file():
    """Тест анализатора кода с простым Python-файлом"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем простой Python-файл
        python_file = Path(temp_dir) / "test.py"
        python_file.write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

# TODO: Add error handling
result = hello("World")
""")

        analyzer = CodeAnalyzer(temp_dir)
        report = analyzer.generate_quality_report()

        # Проверяем, что отчет сгенерирован
        assert "summary" in report
        assert isinstance(report["summary"], dict)


def test_mypy_analysis_not_available():
    """Тест проверки MyPy когда он недоступен"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем анализатор
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно помечаем MyPy как недоступный
        original_status = analyzer.tools_available[AnalysisTool.MYPY]
        analyzer.tools_available[AnalysisTool.MYPY] = False

        # Запускаем анализ MyPy
        result = analyzer.run_mypy_analysis()

        # Результат должен быть неуспешным
        assert not result.success
        assert "не установлен или недоступен" in result.output

        # Восстанавливаем оригинальный статус
        analyzer.tools_available[AnalysisTool.MYPY] = original_status


def test_ruff_analysis_not_available():
    """Тест проверки Ruff когда он недоступен"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем анализатор
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно помечаем Ruff как недоступный
        original_status = analyzer.tools_available[AnalysisTool.RUFF]
        analyzer.tools_available[AnalysisTool.RUFF] = False

        # Запускаем анализ Ruff
        result = analyzer.run_ruff_analysis()

        # Результат должен быть неуспешным
        assert not result.success
        assert "не установлен или недоступен" in result.output

        # Восстанавливаем оригинальный статус
        analyzer.tools_available[AnalysisTool.RUFF] = original_status


def test_bandit_analysis_not_available():
    """Тест проверки Bandit когда он недоступен"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем анализатор
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно помечаем Bandit как недоступный
        original_status = analyzer.tools_available[AnalysisTool.BANDIT]
        analyzer.tools_available[AnalysisTool.BANDIT] = False

        # Запускаем анализ Bandit
        result = analyzer.run_bandit_analysis()

        # Результат должен быть неуспешным
        assert not result.success
        assert "не установлен или недоступен" in result.output

        # Восстанавливаем оригинальный статус
        analyzer.tools_available[AnalysisTool.BANDIT] = original_status


def test_pyright_analysis_not_available():
    """Тест проверки Pyright когда он недоступен"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем анализатор
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно помечаем Pyright как недоступный
        original_status = analyzer.tools_available[AnalysisTool.PYRIGHT]
        analyzer.tools_available[AnalysisTool.PYRIGHT] = False

        # Запускаем анализ Pyright
        result = analyzer.run_pyright_analysis()

        # Результат должен быть неуспешным
        assert not result.success
        assert "не установлен или недоступен" in result.output

        # Восстанавливаем оригинальный статус
        analyzer.tools_available[AnalysisTool.PYRIGHT] = original_status


def test_coverage_analysis_not_available():
    """Тест проверки Coverage когда он недоступен"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем анализатор
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно помечаем Coverage как недоступный
        original_status = analyzer.tools_available[AnalysisTool.PYTEST_COVERAGE]
        analyzer.tools_available[AnalysisTool.PYTEST_COVERAGE] = False

        # Запускаем анализ Coverage
        result = analyzer.run_coverage_analysis()

        # Результат должен быть неуспешным
        assert not result.success
        assert "не установлены или недоступны" in result.output

        # Восстанавливаем оригинальный статус
        analyzer.tools_available[AnalysisTool.PYTEST_COVERAGE] = original_status


def test_full_analysis_with_all_tools_disabled():
    """Тест полного анализа когда все инструменты недоступны"""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = CodeAnalyzer(temp_dir)

        # Принудительно отключаем все инструменты
        for tool in AnalysisTool:
            analyzer.tools_available[tool] = False

        # Запускаем полный анализ
        results = analyzer.run_full_analysis()

        # Результат должен быть пустым словарем, так как все инструменты недоступны
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__])
