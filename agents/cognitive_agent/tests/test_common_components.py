"""
Тесты для общих компонентов Cognitive Agent
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from cognitive_agent.common import (
    BaseAgentExtensions,
    BaseLogger,
    BaseProjectScanner,
    BaseSecurityChecker,
    calculate_file_hash,
    find_files_by_extension,
    format_bytes,
    load_json_file,
)


class TestCommonComponents:
    """
    Тесты для общих компонентов агента
    """

    def test_base_logger_initialization(self):
        """Тест инициализации базового логгера"""
        logger = BaseLogger("test_logger", log_level="DEBUG", log_format="text")
        assert logger.name == "test_logger"
        assert logger.log_level == 10  # DEBUG level

        logger_json = BaseLogger("test_logger_json", log_level="INFO", log_format="json")
        assert logger_json.name == "test_logger_json"
        assert logger_json.log_level == 20  # INFO level

    def test_base_security_checker_validation(self):
        """Тест проверок безопасности"""
        checker = BaseSecurityChecker()

        # Тест безопасной команды
        is_safe, message = checker.validate_command("ls -la")
        assert is_safe is True
        assert "безопасна" in message

        # Тест опасной команды
        is_safe, message = checker.validate_command("rm -rf /")
        assert is_safe is False
        assert "опасный паттерн" in message.lower()

        # Тест безопасного пути
        is_safe, message = checker.validate_path("./safe/path")
        assert is_safe is True
        assert "безопасен" in message

        # Тест кода с eval
        is_safe, message = checker.validate_code("x = eval(input())")
        assert is_safe is False
        assert "опасный паттерн" in message.lower()

        # Тест критического файла
        assert checker.is_critical_file("requirements.txt") is True
        assert checker.is_critical_file("normal_file.py") is False

    def test_base_project_scanner_initialization(self):
        """Тест инициализации сканера проекта"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создать .gitignore
            gitignore_path = temp_path / ".gitignore"
            with open(gitignore_path, "w") as f:
                f.write("__pycache__/\n*.pyc\n")

            scanner = BaseProjectScanner(str(temp_path))
            assert scanner.project_path == temp_path.resolve()
            assert len(scanner.supported_extensions) > 0

    def test_utils_functions(self):
        """Тест утилитарных функций"""
        # Тест calculate_file_hash
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("test content")
            temp_file_path = Path(temp_file.name)

        file_hash = calculate_file_hash(temp_file_path)
        assert isinstance(file_hash, str)
        assert len(file_hash) == 64  # SHA256 hash length

        # Тест load_json_file
        json_path = temp_file_path.with_suffix(".json")
        with open(json_path, "w") as f:
            f.write('{"key": "value"}')

        data = load_json_file(json_path)
        assert data == {"key": "value"}

        # Тест find_files_by_extension
        py_file = temp_file_path.with_name("test.py")
        with open(py_file, "w") as f:
            f.write("# Python file")

        found_files = find_files_by_extension(temp_file_path.parent, [".py"])
        assert py_file in found_files

        # Тест format_bytes
        assert format_bytes(1024) == "1.00KB"
        assert format_bytes(1024 * 1024) == "1.00MB"
        assert format_bytes(0) == "0B"

        # Очистка
        os.unlink(temp_file_path)
        os.unlink(json_path)
        os.unlink(py_file)

    def test_base_agent_extensions_initialization(self):
        """Тест инициализации базовых расширений агента"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extensions = BaseAgentExtensions(project_path=temp_dir, logger=Mock(), security_checker=Mock())

            # Тест инициализации
            extensions.initialize()
            assert extensions.initialized is True

            # Тест контекста проекта
            context = extensions.get_project_context(scan_mode="full")
            assert "scan_results" in context
            assert "timestamp" in context
            assert "project_hash" in context

            # Тест запоминания решений
            extensions.remember_decision(context={"test": "context"}, decision="test_decision", outcome="success")
            assert len(extensions.decision_history) == 1
            assert extensions.decision_history[0]["decision"] == "test_decision"

            # Тест success rate
            assert extensions.get_success_rate() == 1.0

            # Тест валидации контекста задачи
            valid_context = {"task_description": "test task", "project_path": temp_dir}
            is_valid, message = extensions.validate_task_context(valid_context)
            assert is_valid is True

    def test_base_agent_extensions_caching(self):
        """Тест кэширования в базовых расширениях агента"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extensions = BaseAgentExtensions(project_path=temp_dir)

            # Тест кэширования
            test_key = "test_key"
            test_value = {"data": "test_data"}

            extensions.cache_result(test_key, test_value, ttl=3600)
            cached_result = extensions.get_cached_result(test_key)

            assert cached_result is not None
            assert cached_result["result"] == test_value

    def test_base_project_scanner_scan(self):
        """Тест сканирования проекта"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создать тестовую структуру проекта
            (temp_path / "subdir").mkdir()
            (temp_path / "main.py").write_text("# Python file\nTODO: Add feature\n")
            (temp_path / "subdir" / "module.py").write_text("# Another module\n")
            (temp_path / "config.json").write_text('{"setting": "value"}')

            scanner = BaseProjectScanner(str(temp_path))
            results = scanner.scan(mode="full")

            assert len(results["files"]) >= 3  # main.py, module.py, config.json
            assert len(results["directories"]) >= 2  # temp_dir, subdir
            assert "python" in results["tech_stack"]

            # Проверить, что TODO комментарий найден
            todo_issues = [issue for issue in results["issues"] if issue["type"] == "todo_comment"]
            assert len(todo_issues) >= 1

    def test_base_security_checker_file_modification_validation(self):
        """Тест проверки разрешения на изменение файлов"""
        checker = BaseSecurityChecker()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Тест с обычным файлом
            normal_file = Path(temp_dir) / "normal_file.txt"
            normal_file.write_text("test")

            is_allowed, message = checker.validate_file_modification(str(normal_file), "write")
            assert is_allowed is True

            # Тест с критическим файлом
            critical_file = Path(temp_dir) / "requirements.txt"
            critical_file.write_text("test")

            is_allowed, message = checker.validate_file_modification(str(critical_file), "write")
            assert is_allowed is False
            assert "критического файла" in message

    def test_base_agent_extensions_timeout_execution(self):
        """Тест выполнения функций с таймаутом"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extensions = BaseAgentExtensions(project_path=temp_dir)

            # Тест успешного выполнения
            def quick_func(x):
                return x * 2

            result = extensions.run_with_timeout(quick_func, 5, 5)
            assert result == 10

            # Тест таймаута
            def slow_func():
                import time

                time.sleep(2)
                return "done"

            with pytest.raises(TimeoutError):
                extensions.run_with_timeout(slow_func, 1)

    def test_base_project_scanner_gitignore_handling(self):
        """Тест обработки .gitignore в сканере проекта"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Создать .gitignore
            gitignore_path = temp_path / ".gitignore"
            with open(gitignore_path, "w") as f:
                f.write("ignored_file.txt\n*.tmp\n")

            # Создать файлы
            (temp_path / "included_file.txt").write_text("included")
            (temp_path / "ignored_file.txt").write_text("ignored")
            (temp_path / "temp.tmp").write_text("temp")

            scanner = BaseProjectScanner(str(temp_path))

            # Проверить, что файлы исключены
            assert scanner.is_excluded_by_gitignore(temp_path / "ignored_file.txt") is True
            assert scanner.is_excluded_by_gitignore(temp_path / "temp.tmp") is True
            assert scanner.is_excluded_by_gitignore(temp_path / "included_file.txt") is False


if __name__ == "__main__":
    pytest.main([__file__])
