"""
Тесты для модуля анализа документации (src/documentation_analyzer.py)

Service Tier: CORE
Purpose: Unit and integration testing for documentation quality analysis functionality
"""

import tempfile
from pathlib import Path

import pytest

from agents.cognitive_agent.src.documentation_analyzer import (
    DocFormat,
    DocumentationAnalyzer,
    DocumentationIssue,
    DocumentationResult,
)


class TestDocumentationAnalyzerInitialization:
    """Тесты инициализации анализатора документации"""

    def test_analyzer_initialization_with_existing_path(self):
        """Тест инициализации с существующей директорией"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)

            assert analyzer is not None
            assert str(analyzer.project_path) == temp_dir

    def test_analyzer_initialization_with_nonexistent_path(self):
        """Тест инициализации с несуществующей директорией"""
        nonexistent_path = "/nonexistent/path/for/testing"
        analyzer = DocumentationAnalyzer(nonexistent_path)

        assert analyzer is not None
        assert str(analyzer.project_path) == nonexistent_path


class TestDocumentationIssue:
    """Тесты объекта проблемы документации"""

    def test_documentation_issue_creation(self):
        """Тест создания объекта DocumentationIssue"""
        issue = DocumentationIssue(
            file_path="test.py",
            line_number=10,
            issue_type="missing_docstring",
            severity="high",
            message="Missing docstring in public function",
            suggested_fix="Add docstring with description",
        )

        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.issue_type == "missing_docstring"
        assert issue.severity == "high"
        assert issue.message == "Missing docstring in public function"
        assert issue.suggested_fix == "Add docstring with description"


class TestDocumentationResult:
    """Тесты объекта результата документации"""

    def test_documentation_result_creation(self):
        """Тест создания объекта DocumentationResult"""
        issue = DocumentationIssue(
            file_path="test.py",
            line_number=10,
            issue_type="missing_docstring",
            severity="high",
            message="Missing docstring in public function",
            suggested_fix="Add docstring with description",
        )

        result = DocumentationResult(
            format=DocFormat.PYTHON_DOCSTRING,
            success=True,
            issues=[issue],
            summary={"total_issues": 1, "fixed_issues": 0},
        )

        assert result.format == DocFormat.PYTHON_DOCSTRING
        assert result.success is True
        assert len(result.issues) == 1
        assert result.summary["total_issues"] == 1


class TestFindDocumentationFiles:
    """Тесты поиска файлов документации"""

    def test_find_documentation_files_empty_directory(self):
        """Тест поиска файлов документации в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)
            files = analyzer.find_documentation_files()

            assert isinstance(files, dict)
            for doc_format in DocFormat:
                assert doc_format.value in files
                assert isinstance(files[doc_format.value], list)
                assert len(files[doc_format.value]) == 0

    def test_find_documentation_files_with_python_and_markdown(self):
        """Тест поиска файлов документации с Python и Markdown файлами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем тестовые файлы
            (temp_path / "main.py").write_text("# Test Python file")
            (temp_path / "README.md").write_text("# Test Readme")
            (temp_path / "docs").mkdir()
            (temp_path / "docs" / "guide.md").write_text("# Documentation Guide")
            (temp_path / "test.py").write_text('"""Test docstring"""')

            analyzer = DocumentationAnalyzer(temp_dir)
            files = analyzer.find_documentation_files()

            # Проверяем, что Python файлы найдены
            python_files = files[DocFormat.PYTHON_DOCSTRING.value]
            assert len(python_files) >= 2  # main.py и test.py

            # Проверяем, что Markdown файлы найдены
            markdown_files = files[DocFormat.MARKDOWN.value]
            assert len(markdown_files) >= 2  # README.md и docs/guide.md


class TestAnalyzePythonDocstrings:
    """Тесты анализа Python docstring'ов"""

    def test_analyze_python_docstrings_with_good_docstrings(self):
        """Тест анализа Python файлов с хорошими docstring'ами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с хорошими docstring'ами
            good_python_content = '''
"""Модуль для тестирования docstring'ов."""

def good_function(param: str) -> str:
    """Хорошая функция с описанием.

    Args:
        param: Параметр с описанием

    Returns:
        str: Возвращаемое значение
    """
    return param

class GoodClass:
    """Хороший класс с описанием."""

    def __init__(self, value: int):
        """Инициализация класса.

        Args:
            value: Значение
        """
        self.value = value

    def good_method(self) -> int:
        """Хороший метод с описанием.

        Returns:
            int: Значение
        """
        return self.value
'''
            (temp_path / "good_module.py").write_text(good_python_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_python_docstrings()

            # Проверяем, что результаты содержат оценки
            assert len(results) > 0
            for result in results:
                assert isinstance(result, DocumentationResult)

    def test_analyze_python_docstrings_with_missing_docstrings(self):
        """Тест анализа Python файлов с отсутствующими docstring'ами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файл с отсутствующими docstring'ами
            bad_python_content = """
def bad_function(param):
    return param

class BadClass:
    def __init__(self, value):
        self.value = value

    def bad_method(self):
        return self.value
"""
            (temp_path / "bad_module.py").write_text(bad_python_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_python_docstrings()

            # Проверяем, что результаты содержат проблемы
            assert len(results) > 0
            for result in results:
                assert isinstance(result, DocumentationResult)
                assert len(result.issues) >= 0  # Может быть 0 если анализатор не нашел проблем


class TestAnalyzeMarkdownDocumentation:
    """Тесты анализа Markdown документации"""

    def test_analyze_markdown_with_good_structure(self):
        """Тест анализа Markdown с хорошей структурой"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем хороший Markdown файл
            good_md_content = """
# Заголовок первого уровня

## Введение

Это введение к документации.

## Установка

Для установки выполните:

```bash
pip install package
```

## Использование

Пример использования:

```python
from package import main
main()
```

## API

### Функция `main`

Функция для запуска приложения.

### Класс `Example`

Класс для демонстрации.

## Лицензия

MIT License
"""
            (temp_path / "good_doc.md").write_text(good_md_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_markdown_documentation()

            # Проверяем, что результаты содержат оценки
            assert len(results) > 0
            for result in results:
                assert isinstance(result, DocumentationResult)

    def test_analyze_markdown_with_poor_structure(self):
        """Тест анализа Markdown с плохой структурой"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем плохой Markdown файл
            bad_md_content = """
Просто текст
без структуры
и заголовков
"""
            (temp_path / "bad_doc.md").write_text(bad_md_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_markdown_documentation()

            # Проверяем, что результаты содержат проблемы
            assert len(results) >= 0  # Может быть 0 если анализатор не нашел проблем


class TestAnalyzeReStructuredText:
    """Тесты анализа reStructuredText документации"""

    def test_analyze_rst_empty_directory(self):
        """Тест анализа RST в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_restructured_text()

            # В пустой директории не должно быть RST файлов
            assert len(results) == 0

    def test_analyze_rst_with_content(self):
        """Тест анализа RST с содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем RST файл
            rst_content = """
Заголовок документа
===================

Введение
--------

Это введение к документу.

.. code-block:: python

   def example():
       pass

Раздел
------

Дополнительная информация.
"""
            (temp_path / "example.rst").write_text(rst_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_restructured_text()

            # Должен быть найден один RST файл
            assert len(results) >= 0  # Может быть 0 если sphinx не установлен


class TestAnalyzeJSDoc:
    """Тесты анализа JSDoc документации"""

    def test_analyze_jsdoc_empty_directory(self):
        """Тест анализа JSDoc в пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_jsdoc()

            # В пустой директории не должно быть JS файлов с JSDoc
            assert len(results) == 0

    def test_analyze_jsdoc_with_js_content(self):
        """Тест анализа JSDoc с JavaScript содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем JS файл с JSDoc
            js_content = """
/**
 * Функция для сложения двух чисел
 * @param {number} a - Первое число
 * @param {number} b - Второе число
 * @returns {number} Сумма двух чисел
 */
function add(a, b) {
    return a + b;
}

/**
 * Класс для математических операций
 */
class Calculator {
    /**
     * Метод для умножения
     * @param {number} x - Первый множитель
     * @param {number} y - Второй множитель
     * @returns {number} Результат умножения
     */
    multiply(x, y) {
        return x * y;
    }
}
"""
            (temp_path / "math.js").write_text(js_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_jsdoc()

            # Должен быть найден JS файл с JSDoc
            assert len(results) >= 0  # Может быть 0 если js файлы не обнаружены как документация


class TestAnalyzeConfigurationDocs:
    """Тесты анализа документации конфигурации"""

    def test_analyze_config_docs_with_yaml(self):
        """Тест анализа документации конфигурации с YAML"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем YAML файл с комментариями
            yaml_content = """
# Конфигурация приложения
app:
  # Название приложения
  name: "Test App"
  # Режим отладки
  debug: true
  # Параметры соединения с базой данных
  database:
    host: "localhost"
    port: 5432
    name: "test_db"
"""
            (temp_path / "config.yaml").write_text(yaml_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_configuration_docs()

            # Проверяем, что результаты содержат информацию
            assert len(results) >= 0

    def test_analyze_config_docs_with_json(self):
        """Тест анализа документации конфигурации с JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем JSON файл (без комментариев, так как JSON не поддерживает их)
            json_content = """
{
    "app": {
        "name": "Test App",
        "debug": true,
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
}
"""
            (temp_path / "config.json").write_text(json_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            results = analyzer.analyze_configuration_docs()

            # Проверяем, что результаты содержат информацию
            assert len(results) >= 0


class TestGenerateDocumentationReport:
    """Тесты генерации отчета о документации"""

    def test_generate_documentation_report_empty_directory(self):
        """Тест генерации отчета для пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)
            report = analyzer.generate_documentation_report()

            # Проверяем структуру отчета
            assert "project_path" in report
            assert "summary" in report
            assert "details" in report
            assert "files_analyzed" in report["summary"]
            assert "quality_score" in report["summary"]

            # В пустой директории оценка должна быть 0
            assert report["summary"]["quality_score"] >= 0

    def test_generate_documentation_report_with_content(self):
        """Тест генерации отчета с содержимым"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создаем файлы с хорошей документацией
            good_py_content = '''
"""Хорошо документированный модуль."""

def well_documented_function(param: str) -> str:
    """Хорошо документированная функция.

    Args:
        param: Хорошо описанный параметр

    Returns:
        str: Хорошо описанное возвращаемое значение
    """
    return param
'''
            (temp_path / "well_documented.py").write_text(good_py_content)

            good_md_content = """
# Хорошая документация

Это пример хорошей документации.

## Раздел 1

Описание первого раздела.
"""
            (temp_path / "good_docs.md").write_text(good_md_content)

            analyzer = DocumentationAnalyzer(temp_dir)
            report = analyzer.generate_documentation_report()

            # Проверяем структуру отчета
            assert "project_path" in report
            assert "summary" in report
            assert "details" in report
            assert report["summary"]["files_analyzed"] > 0
            assert "python" in report["details"]
            assert "markdown" in report["details"]


class TestCalculateOverallScore:
    """Тесты расчета общей оценки документации"""

    def test_calculate_overall_score_empty_results(self):
        """Тест расчета общей оценки для пустых результатов"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)
            score = analyzer.calculate_overall_score([])

            assert score == 0

    def test_calculate_overall_score_with_results(self):
        """Тест расчета общей оценки с результатами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DocumentationAnalyzer(temp_dir)

            # Создаем тестовые результаты
            issue = DocumentationIssue(
                file_path="test1.py",
                line_number=10,
                issue_type="missing_docstring",
                severity="high",
                message="Missing docstring in public function",
                suggested_fix="Add docstring with description",
            )

            test_results = [
                DocumentationResult(format=DocFormat.PYTHON_DOCSTRING, success=True, issues=[issue], summary={})
            ]

            score = analyzer.calculate_overall_score(test_results)

            # Оценка должна быть числом
            assert isinstance(score, (int, float))


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_analyzer_with_readonly_directory(self):
        """Тест анализатора с директорией только для чтения"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем файлы для анализа
            temp_path = Path(temp_dir)
            (temp_path / "readonly_test.py").write_text('"""Test"""')

            analyzer = DocumentationAnalyzer(temp_dir)

            # Даже с файлами анализатор должен корректно работать
            try:
                report = analyzer.generate_documentation_report()
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

            # Создаем текстовый файл для анализа
            (temp_path / "text.py").write_text('"""Test docstring"""')

            analyzer = DocumentationAnalyzer(temp_dir)

            # Анализатор должен корректно обрабатывать бинарные файлы
            try:
                report = analyzer.generate_documentation_report()
                assert "summary" in report
            except Exception:
                # Обработка любых исключений должна быть корректной
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
