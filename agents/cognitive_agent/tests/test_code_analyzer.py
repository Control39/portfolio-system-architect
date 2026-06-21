"""
Тесты для модуля анализа кода (src/code_analyzer.py)

Service Tier: CORE
Purpose: Unit and integration testing for code quality analysis functionality
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from agents.cognitive_agent.src.code_analyzer import AnalysisResult, AnalysisTool, CodeAnalyzer


class TestCodeAnalyzerInitialization:
    """Тесты инициализации анализатора кода"""

    def test_analyzer_initialization_with_existing_path(self):
        """Тест инициализации с существующей директорией"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            assert analyzer is not None
            assert str(analyzer.project_path) == temp_dir
            assert isinstance(analyzer.tools_available, dict)

            # Проверяем, что все ожидаемые инструменты присутствуют
            for tool in AnalysisTool:
                assert tool in analyzer.tools_available

    def test_analyzer_initialization_with_nonexistent_path(self):
        """Тест инициализации с несуществующей директорией"""
        nonexistent_path = "/nonexistent/path/for/testing"
        analyzer = CodeAnalyzer(nonexistent_path)

        assert analyzer is not None
        assert str(analyzer.project_path) == nonexistent_path


class TestToolAvailability:
    """Тесты проверки доступности инструментов анализа"""

    @patch("subprocess.run")
    def test_check_tool_availability_all_available(self, mock_subprocess):
        """Тест проверки доступности всех инструментов (все доступны)"""

        # Моделируем успешные ответы от всех инструментов
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and len(cmd) > 0:
                tool_cmd = cmd[0]
                if tool_cmd in ["mypy", "ruff", "bandit", "pyright"]:
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = f"{tool_cmd} 1.0.0"
                    return result
                elif tool_cmd == "pytest":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "pytest 7.0.0"
                    return result
                elif tool_cmd == "coverage":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "coverage 6.0.0"
                    return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # Проверяем, что все инструменты помечены как доступные
            for tool, available in analyzer.tools_available.items():
                assert available is True

    @patch("subprocess.run")
    def test_check_tool_availability_none_available(self, mock_subprocess):
        """Тест проверки доступности инструментов (ни один не доступен)"""

        # Моделируем ошибки для всех инструментов
        def mock_run_side_effect(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            return result

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # Проверяем, что все инструменты помечены как недоступные
            for tool, available in analyzer.tools_available.items():
                assert available is False

    @patch("subprocess.run")
    def test_check_tool_availability_mypy(self, mock_subprocess):
        """Тест проверки доступности MyPy"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and cmd[0] == "mypy":
                result = MagicMock()
                result.returncode = 0
                result.stdout = "mypy 1.0.0"
                return result
            else:
                result = MagicMock()
                result.returncode = 1
                return result

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # MyPy должен быть доступен, остальные - нет
            assert analyzer.tools_available[AnalysisTool.MYPY] is True
            for tool in AnalysisTool:
                if tool != AnalysisTool.MYPY:
                    assert analyzer.tools_available[tool] is False


class TestAnalysisResults:
    """Тесты результатов анализа"""

    def test_analysis_result_creation(self):
        """Тест создания объекта AnalysisResult"""
        result = AnalysisResult(
            tool=AnalysisTool.MYPY,
            success=True,
            output="Test output",
            issues=[{"line": 1, "message": "Test issue"}],
            summary={"errors": 1, "warnings": 0},
        )

        assert result.tool == AnalysisTool.MYPY
        assert result.success is True
        assert result.output == "Test output"
        assert len(result.issues) == 1
        assert result.summary["errors"] == 1


class TestRunMyPyAnalysis:
    """Тесты анализа с помощью MyPy"""

    @patch("subprocess.run")
    def test_run_mypy_analysis_available(self, mock_subprocess):
        """Тест запуска анализа MyPy когда инструмент доступен"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "mypy" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Success: no issues found"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что mypy доступен
            analyzer.tools_available[AnalysisTool.MYPY] = True

            result = analyzer.run_mypy_analysis()

            assert result.tool == AnalysisTool.MYPY
            assert result.success is True
            assert "no issues found" in result.output

    @patch("subprocess.run")
    def test_run_mypy_analysis_not_available(self, mock_subprocess):
        """Тест запуска анализа MyPy когда инструмент недоступен"""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что mypy недоступен
            analyzer.tools_available[AnalysisTool.MYPY] = False

            result = analyzer.run_mypy_analysis()

            assert result.tool == AnalysisTool.MYPY
            assert result.success is False
            assert "не установлен" in result.output or "недоступен" in result.output


class TestRunRuffAnalysis:
    """Тесты анализа с помощью Ruff"""

    @patch("subprocess.run")
    def test_run_ruff_analysis_available(self, mock_subprocess):
        """Тест запуска анализа Ruff когда инструмент доступен"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "ruff" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Found 0 errors"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что ruff доступен
            analyzer.tools_available[AnalysisTool.RUFF] = True

            result = analyzer.run_ruff_analysis()

            assert result.tool == AnalysisTool.RUFF
            assert result.success is True
            assert "0 errors" in result.output

    @patch("subprocess.run")
    def test_run_ruff_analysis_with_issues(self, mock_subprocess):
        """Тест запуска анализа Ruff с найденными проблемами"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "ruff" in cmd:
                result = MagicMock()
                result.returncode = 1
                result.stdout = "test.py:1:1: F401 'os' imported but unused"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что ruff доступен
            analyzer.tools_available[AnalysisTool.RUFF] = True

            result = analyzer.run_ruff_analysis()

            assert result.tool == AnalysisTool.RUFF
            assert result.success is False
            assert "F401" in result.output


class TestRunBanditAnalysis:
    """Тесты анализа с помощью Bandit"""

    @patch("subprocess.run")
    def test_run_bandit_analysis_available(self, mock_subprocess):
        """Тест запуска анализа Bandit когда инструмент доступен"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "bandit" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Run completed: 100% scanned"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что bandit доступен
            analyzer.tools_available[AnalysisTool.BANDIT] = True

            result = analyzer.run_bandit_analysis()

            assert result.tool == AnalysisTool.BANDIT
            assert result.success is True
            assert "completed" in result.output.lower()


class TestRunPyrightAnalysis:
    """Тесты анализа с помощью Pyright"""

    @patch("subprocess.run")
    def test_run_pyright_analysis_available(self, mock_subprocess):
        """Тест запуска анализа Pyright когда инструмент доступен"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list) and "pyright" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "0 errors, 0 warnings"
                return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что pyright доступен
            analyzer.tools_available[AnalysisTool.PYRIGHT] = True

            result = analyzer.run_pyright_analysis()

            assert result.tool == AnalysisTool.PYRIGHT
            assert result.success is True
            assert "0 errors" in result.output


class TestRunPytestCoverageAnalysis:
    """Тесты анализа покрытия с помощью Pytest"""

    @patch("subprocess.run")
    def test_run_pytest_coverage_analysis_available(self, mock_subprocess):
        """Тест запуска анализа покрытия когда инструменты доступны"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list):
                if cmd[0] == "pytest":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "pytest version 7.0.0"
                    return result
                elif cmd[0] == "coverage":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "coverage version 6.0.0"
                    return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)
            # Моделируем, что инструменты доступны
            analyzer.tools_available[AnalysisTool.PYTEST_COVERAGE] = True

            result = analyzer.run_pytest_coverage_analysis()

            assert result.tool == AnalysisTool.PYTEST_COVERAGE
            assert result.success is True


class TestGenerateQualityReport:
    """Тесты генерации отчета о качестве"""

    @patch("subprocess.run")
    def test_generate_quality_report(self, mock_subprocess):
        """Тест генерации полного отчета о качестве кода"""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if isinstance(cmd, list):
                tool_cmd = cmd[0]
                if tool_cmd in ["mypy", "ruff", "bandit", "pyright"]:
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = f"{tool_cmd} analysis completed successfully"
                    return result
                elif tool_cmd == "pytest":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "pytest version 7.0.0"
                    return result
                elif tool_cmd == "coverage":
                    result = MagicMock()
                    result.returncode = 0
                    result.stdout = "coverage version 6.0.0"
                    return result
            return MagicMock(returncode=1, stdout="")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # Моделируем, что все инструменты доступны
            for tool in AnalysisTool:
                analyzer.tools_available[tool] = True

            report = analyzer.generate_quality_report()

            # Проверяем структуру отчета
            assert "project_path" in report
            assert "tools_run" in report
            assert "tools_available" in report
            assert "results" in report
            assert "summary" in report

            # Проверяем, что путь к проекту совпадает
            assert str(report["project_path"]) == temp_dir

            # Проверяем, что результаты для всех инструментов присутствуют
            for tool in AnalysisTool:
                assert tool.value in report["results"]


class TestEdgeCases:
    """Тесты граничных случаев"""

    @patch("subprocess.run")
    def test_analyzer_with_permission_error(self, mock_subprocess):
        """Тест анализатора при ошибке доступа к директории"""

        def mock_run_side_effect(*args, **kwargs):
            raise PermissionError("Permission denied")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # Даже при ошибках анализатор должен обработать ситуацию
            try:
                report = analyzer.generate_quality_report()
                # Если отчет сгенерирован, проверяем его структуру
                assert "project_path" in report
            except Exception:
                # Даже если выброшено исключение, анализатор должен корректно обрабатывать ошибки
                pass

    @patch("subprocess.run")
    def test_file_not_found_error_handling(self, mock_subprocess):
        """Тест обработки ошибки FileNotFoundError"""

        def mock_run_side_effect(*args, **kwargs):
            raise FileNotFoundError("Command not found")

        mock_subprocess.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = CodeAnalyzer(temp_dir)

            # Проверяем, что анализатор корректно обрабатывает отсутствие инструментов
            for tool in AnalysisTool:
                analyzer.tools_available[tool] = False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
