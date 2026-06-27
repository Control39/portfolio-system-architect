"""
Тесты для модуля анализа документации
"""

import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.documentation_analyzer import DocFormat, DocumentationAnalyzer


def test_documentation_analyzer_initialization():
    """Тест инициализации анализатора документации"""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = DocumentationAnalyzer(temp_dir)

        # Проверяем, что анализатор инициализировался
        assert analyzer is not None
        assert hasattr(analyzer, "project_path")
        assert hasattr(analyzer, "documentation_files")

        # Проверяем, что documentation_files - это список
        assert isinstance(analyzer.documentation_files, list)


def test_find_documentation_files():
    """Тест поиска файлов документации"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем несколько файлов документации
        Path(temp_dir, "README.md").write_text("# Test Project\nDescription here.")
        Path(temp_dir, "docs").mkdir()
        Path(temp_dir, "docs", "guide.md").write_text("# User Guide\nContent here.")
        Path(temp_dir, "module.py").write_text('"""Module docstring"""\ndef func(): pass')

        analyzer = DocumentationAnalyzer(temp_dir)
        doc_files = analyzer.documentation_files

        # Проверяем, что найдены все документационные файлы
        file_names = [f.name for f in doc_files]
        assert "README.md" in file_names
        assert "guide.md" in file_names
        assert "module.py" in file_names


def test_analyze_python_documentation():
    """Тест анализа документации в Python файле"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем Python файл с различными уровнями документации
        python_code = '''
def well_documented_func(param1: str) -> str:
    """Хорошо документированная функция.

    Args:
        param1: Описание параметра

    Returns:
        str: Описание возвращаемого значения
    """
    return param1

def poorly_documented_func(param1):
    # Функция без docstring
    return param1

class WellDocumentedClass:
    """Хорошо документированный класс."""

    def method(self):
        """Документированный метод."""
        pass

class PoorlyDocumentedClass:
    def method(self):
        pass
'''
        python_file = Path(temp_dir) / "test_module.py"
        python_file.write_text(python_code)

        analyzer = DocumentationAnalyzer(temp_dir)
        result = analyzer.analyze_python_documentation(python_file)

        # Проверяем, что результат содержит ожидаемые поля
        assert result.format == DocFormat.PYTHON_DOCSTRING
        assert result.success is True
        assert isinstance(result.issues, list)
        assert isinstance(result.summary, dict)


def test_analyze_markdown_documentation():
    """Тест анализа документации в Markdown файле"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем Markdown файл с различными структурными элементами
        markdown_content = """
# Заголовок первого уровня

Это основное описание документа.

## Заголовок второго уровня

Тут содержится некоторая информация.

### Заголовок третьего уровня

Дополнительные детали.

## Еще один заголовок второго уровня

Более информация.
"""
        md_file = Path(temp_dir) / "test_doc.md"
        md_file.write_text(markdown_content)

        analyzer = DocumentationAnalyzer(temp_dir)
        result = analyzer.analyze_markdown_documentation(md_file)

        # Проверяем, что результат содержит ожидаемые поля
        assert result.format == DocFormat.MARKDOWN
        assert result.success is True
        assert isinstance(result.issues, list)
        assert isinstance(result.summary, dict)


def test_analyze_readme():
    """Тест анализа файла README"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем README файл с недостающими секциями
        readme_content = """
# Test Project

Short description of the project.

## Installation

How to install the project.

## Usage

How to use the project.
"""
        readme_file = Path(temp_dir) / "README.md"
        readme_file.write_text(readme_content)

        analyzer = DocumentationAnalyzer(temp_dir)
        result = analyzer.analyze_readme()

        # Проверяем, что результат содержит ожидаемые поля
        assert result.format == DocFormat.MARKDOWN
        assert isinstance(result.issues, list)
        assert isinstance(result.summary, dict)


def test_documentation_consistency_analysis():
    """Тест анализа согласованности документации"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем Python файл с функцией
        python_code = '''
def my_function(param1: str) -> str:
    """Функция для тестирования."""
    return param1
'''
        python_file = Path(temp_dir) / "my_module.py"
        python_file.write_text(python_code)

        # Создаем Markdown файл, который ссылается на функцию
        md_content = """
# Documentation

This document describes my_module.py and its functions, including my_function.
"""
        md_file = Path(temp_dir) / "doc.md"
        md_file.write_text(md_content)

        analyzer = DocumentationAnalyzer(temp_dir)
        consistency_result = analyzer.analyze_documentation_consistency()

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(consistency_result, dict)
        assert "total_code_entities" in consistency_result
        assert "documented_entities" in consistency_result
        assert "consistency_issues" in consistency_result
        assert "documentation_coverage" in consistency_result


def test_run_documentation_analysis():
    """Тест полного анализа документации"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем несколько файлов документации
        Path(temp_dir, "README.md").write_text("# Test Project\nDescription here.")
        Path(temp_dir, "module.py").write_text('def func():\n    """Function docstring."""\n    pass')
        Path(temp_dir, "docs", "guide.md").mkdir(parents=True)
        Path(temp_dir, "docs", "guide.md", "guide.md").write_text("# Guide\nContent here.")

        analyzer = DocumentationAnalyzer(temp_dir)
        full_analysis = analyzer.run_documentation_analysis()

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(full_analysis, dict)
        assert "project_path" in full_analysis
        assert "total_documentation_files" in full_analysis
        assert "files_analyzed" in full_analysis
        assert "readme_analysis" in full_analysis
        assert "consistency_analysis" in full_analysis
        assert "summary" in full_analysis


def test_generate_documentation_improvements():
    """Тест генерации рекомендаций по улучшению документации"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Создаем файлы для анализа
        Path(temp_dir, "README.md").write_text("# Test Project\nBasic description.")
        Path(temp_dir, "module.py").write_text("def func(): pass")  # Без docstring

        analyzer = DocumentationAnalyzer(temp_dir)
        analysis_results = analyzer.run_documentation_analysis()
        improvements = analyzer.generate_documentation_improvements(analysis_results)

        # Проверяем, что результат содержит ожидаемые поля
        assert isinstance(improvements, dict)
        assert "timestamp" in improvements
        assert "project_path" in improvements
        assert "recommendations" in improvements
        assert "priority_actions" in improvements
        assert "implementation_guide" in improvements


if __name__ == "__main__":
    pytest.main([__file__])
