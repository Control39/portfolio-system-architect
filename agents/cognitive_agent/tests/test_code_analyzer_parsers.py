"""
Unit-тесты для парсеров код-анализатора.
Проверяет корректность обработки вывода инструментов анализа (mypy, ruff, bandit, pyright).
"""

import json
import pytest
import tempfile
from pathlib import Path
from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer, AnalysisTool


# --- Fixtures (реалистичные данные от инструментов) ---


@pytest.fixture
def mypy_json_output() -> str:
    """Реальный формат вывода mypy --json"""
    return json.dumps(
        {
            "files": {
                "src/my_module.py": {
                    "messages": [
                        {
                            "line": 10,
                            "column": 5,
                            "message": "Cannot find implementation or library stub for module named 'unknown'",
                            "type": "error",
                        },
                        {"line": 15, "column": 1, "message": "Missing return statement", "type": "error"},
                    ]
                }
            }
        }
    )


@pytest.fixture
def ruff_json_output() -> str:
    """Реальный формат вывода ruff check --output-format=json"""
    return json.dumps(
        [
            {
                "code": "E501",
                "message": "Line too long (89 > 79 characters)",
                "location": {"row": 15, "column": 80},
                "end_location": {"row": 15, "column": 90},
                "filename": "src/another_module.py",
                "level": "warning",
                "fix": None,
            },
            {
                "code": "F401",
                "message": "'os' imported but unused",
                "location": {"row": 3, "column": 1},
                "end_location": {"row": 3, "column": 4},
                "filename": "src/my_module.py",
                "level": "warning",
                "fix": None,
            },
        ]
    )


@pytest.fixture
def bandit_json_output() -> str:
    """Реальный формат вывода bandit -f json"""
    return json.dumps(
        {
            "results": [
                {
                    "filename": "src/security_module.py",
                    "test_id": "B101",
                    "issue_severity": "HIGH",
                    "issue_text": "Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.",
                    "line_number": 12,
                    "line_range": [12],
                    "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html",
                },
                {
                    "filename": "src/security_module.py",
                    "test_id": "B301",
                    "issue_severity": "MEDIUM",
                    "issue_text": "Pickling and unpickling can execute arbitrary code",
                    "line_number": 25,
                    "line_range": [25],
                    "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b301_pickling.html",
                },
            ],
            "generated_at": "2024-01-01T00:00:00Z",
            "summary": {
                "errors": [],
                "files": 1,
                "filtered": 0,
                "ignores": [],
                "init_errors": [],
                "lines": 100,
                "nosec": 0,
                "skipped": 0,
                "test_results": 0,
                "total": 0,
                "vulns": 2,
            },
        }
    )


@pytest.fixture
def pyright_json_output() -> str:
    """Реальный формат вывода pyright --outputjson"""
    return json.dumps(
        {
            "version": "1.1.350",
            "time": "2024-01-01T00:00:00.000Z",
            "generalDiagnostics": [
                {
                    "file": "src/type_module.py",
                    "severity": "error",
                    "message": "Cannot find reference 'undefined_function' in 'mymodule'",
                    "range": {"start": {"line": 5, "character": 10}, "end": {"line": 5, "character": 30}},
                },
                {
                    "file": "src/type_module.py",
                    "severity": "warning",
                    "message": 'Type of "unused_var" is partially unknown',
                    "range": {"start": {"line": 8, "character": 4}, "end": {"line": 8, "character": 15}},
                },
            ],
            "summary": {
                "filesAnalyzed": 1,
                "errorCount": 1,
                "warningCount": 1,
                "informationCount": 0,
                "timeInSec": 0.5,
            },
        }
    )


@pytest.fixture
def empty_mypy_output() -> str:
    """Пустой вывод mypy (успешный анализ без ошибок)"""
    return json.dumps({"files": {}})


@pytest.fixture
def empty_ruff_output() -> str:
    """Пустой вывод ruff (без ошибок)"""
    return json.dumps([])


@pytest.fixture
def empty_bandit_output() -> str:
    """Пустой вывод bandit"""
    return json.dumps({"results": []})


@pytest.fixture
def empty_pyright_output() -> str:
    """Пустой вывод pyright"""
    return json.dumps(
        {
            "version": "1.1.350",
            "time": "2024-01-01T00:00:00.000Z",
            "generalDiagnostics": [],
            "summary": {
                "filesAnalyzed": 0,
                "errorCount": 0,
                "warningCount": 0,
                "informationCount": 0,
                "timeInSec": 0.1,
            },
        }
    )


@pytest.fixture
def analyzer_instance(tmp_path):
    """Создает изолированный экземпляр анализатора во временной директории"""
    # Создаем фиктивные файлы для тестов
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "my_module.py").write_text("print('hello')\n" * 20)
    (tmp_path / "src" / "another_module.py").write_text("x = 1\n" * 20)
    (tmp_path / "src" / "security_module.py").write_text("import os\n" * 30)
    (tmp_path / "src" / "type_module.py").write_text("x: int = 1\n" * 20)

    return CodeAnalyzer(str(tmp_path))


# --- Тесты парсеров ---


class TestMypyParser:
    """Тесты парсера mypy"""

    def test_parse_mypy_valid(self, analyzer_instance, mypy_json_output):
        """Тест парсинга валидного вывода mypy"""
        issues, summary = analyzer_instance._parse_mypy(mypy_json_output)

        assert len(issues) == 2
        assert issues[0]["tool"] == "mypy"
        assert issues[0]["file"] == "src/my_module.py"
        assert issues[0]["line"] == 10
        assert "Cannot find implementation" in issues[0]["message"]
        assert issues[0]["severity"] == "error"

        assert issues[1]["line"] == 15
        assert "Missing return statement" in issues[1]["message"]

    def test_parse_mypy_empty(self, analyzer_instance, empty_mypy_output):
        """Тест парсинга пустого вывода mypy"""
        issues, summary = analyzer_instance._parse_mypy(empty_mypy_output)

        assert len(issues) == 0
        assert summary["error_count"] == 0
        assert summary["warning_count"] == 0
        assert summary["note_count"] == 0

    def test_parse_mypy_invalid_json(self, analyzer_instance):
        """Тест обработки некорректного JSON"""
        issues, summary = analyzer_instance._parse_mypy("invalid json {")

        assert len(issues) == 0
        assert "error" not in summary  # Ошибка логируется, но не прерывает выполнение


class TestRuffParser:
    """Тесты парсера ruff"""

    def test_parse_ruff_valid(self, analyzer_instance, ruff_json_output):
        """Тест парсинга валидного вывода ruff"""
        issues, summary = analyzer_instance._parse_ruff(ruff_json_output)

        assert len(issues) == 2
        assert issues[0]["tool"] == "ruff"
        assert issues[0]["file"] == "src/another_module.py"
        assert issues[0]["line"] == 15
        assert "Line too long" in issues[0]["message"]
        assert "E501" in issues[0]["message"]
        assert issues[0]["severity"] == "warning"

        assert issues[1]["file"] == "src/my_module.py"
        assert issues[1]["line"] == 3
        assert "imported but unused" in issues[1]["message"]
        assert "F401" in issues[1]["message"]

    def test_parse_ruff_empty(self, analyzer_instance, empty_ruff_output):
        """Тест парсинга пустого вывода ruff"""
        issues, summary = analyzer_instance._parse_ruff(empty_ruff_output)

        assert len(issues) == 0
        assert summary["error_count"] == 0
        assert summary["warning_count"] == 0

    def test_parse_ruff_invalid_json(self, analyzer_instance):
        """Тест обработки некорректного JSON"""
        issues, summary = analyzer_instance._parse_ruff("invalid json {")

        assert len(issues) == 0


class TestBanditParser:
    """Тесты парсера bandit"""

    def test_parse_bandit_valid(self, analyzer_instance, bandit_json_output):
        """Тест парсинга валидного вывода bandit"""
        issues, summary = analyzer_instance._parse_bandit(bandit_json_output)

        assert len(issues) == 2
        assert issues[0]["tool"] == "bandit"
        assert issues[0]["file"] == "src/security_module.py"
        assert issues[0]["line"] == 12
        assert "Use of assert detected" in issues[0]["message"]
        assert issues[0]["severity"] == "high"
        assert issues[0]["rule"] == "B101"

        assert issues[1]["line"] == 25
        assert "Pickling and unpickling" in issues[1]["message"]
        assert issues[1]["severity"] == "medium"

    def test_parse_bandit_empty(self, analyzer_instance, empty_bandit_output):
        """Тест парсинга пустого вывода bandit"""
        issues, summary = analyzer_instance._parse_bandit(empty_bandit_output)

        assert len(issues) == 0
        assert summary["security_issue_count"] == 0

    def test_parse_bandit_high_severity(self, analyzer_instance, bandit_json_output):
        """Тест подсчета high severity проблем"""
        issues, summary = analyzer_instance._parse_bandit(bandit_json_output)

        assert summary["high_severity_count"] == 1


class TestPyrightParser:
    """Тесты парсера pyright"""

    def test_parse_pyright_valid(self, analyzer_instance, pyright_json_output):
        """Тест парсинга валидного вывода pyright"""
        issues, summary = analyzer_instance._parse_pyright(pyright_json_output)

        assert len(issues) == 2
        assert issues[0]["tool"] == "pyright"
        assert issues[0]["file"] == "src/type_module.py"
        assert issues[0]["line"] == 5  # line в pyright 0-indexed
        assert "Cannot find reference" in issues[0]["message"]
        assert issues[0]["severity"] == "error"

        assert issues[1]["line"] == 8
        assert issues[1]["severity"] == "warning"

    def test_parse_pyright_empty(self, analyzer_instance, empty_pyright_output):
        """Тест парсинга пустого вывода pyright"""
        issues, summary = analyzer_instance._parse_pyright(empty_pyright_output)

        assert len(issues) == 0
        assert summary["error_count"] == 0
        assert summary["warning_count"] == 0

    def test_parse_pyright_invalid_json(self, analyzer_instance):
        """Тест обработки некорректного JSON"""
        issues, summary = analyzer_instance._parse_pyright("invalid json {")

        assert len(issues) == 0


# --- Тесты интеграции ---


class TestCodeAnalyzerIntegration:
    """Интеграционные тесты CodeAnalyzer"""

    def test_full_analysis_with_fixed_files(self, analyzer_instance, tmp_path):
        """Полный анализ с реальными файлами"""
        # Создаем файл с известными проблемами
        test_file = tmp_path / "src" / "test_issues.py"
        test_file.write_text("""
import os  # unused import
import sys

def bad_function():
    x = 1  # unused variable
    return 42

class SomeClass:
    def method(self):
        pass  # TODO: implement
""")

        analyzer = CodeAnalyzer(str(tmp_path))
        results = analyzer.run_full_analysis()

        # Проверяем, что анализ запустился
        assert len(results) > 0
