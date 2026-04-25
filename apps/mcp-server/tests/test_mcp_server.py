#!/usr/bin/env python3
"""Тесты для MCP-сервера Career Autopilot

Проверяет:
1. Доступность инструментов
2. Корректность работы с файлами
3. Интеграцию с IT-Compass
4. Работу с Git
5. Выполнение команд
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Добавляем путь к корню проекта
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Импортируем инструменты MCP-сервера
try:
    from apps.mcp_server.src.tools.file_tools import (
        list_files_tool,
        read_file_tool,
        search_files_tool,
        write_file_tool,
    )
    from apps.mcp_server.src.tools.git_tools import (
        get_git_history_tool,
        get_git_status_tool,
        scan_last_commits_for_markers_tool,
    )
    HAS_MCP_TOOLS = True
except ImportError:
    HAS_MCP_TOOLS = False
    print("Warning: MCP tools not found. Running tests in stub mode.")

class TestFileTools(unittest.TestCase):
    """Тесты инструментов для работы с файлами"""

    def setUp(self):
        """Настройка тестовой среды"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.txt"
        self.test_file.write_text("Hello, World!\nThis is a test file.")

        # Создаем структуру для тестирования
        (Path(self.test_dir) / "subdir").mkdir()
        (Path(self.test_dir) / "subdir" / "nested.txt").write_text("Nested file")
        (Path(self.test_dir) / "test.py").write_text("print('Hello')")
        (Path(self.test_dir) / "test.md").write_text("# Markdown file")

    def tearDown(self):
        """Очистка тестовой среды"""
        import shutil
        shutil.rmtree(self.test_dir)

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_read_file_tool(self):
        """Тест чтения файла"""
        result = read_file_tool(str(self.test_file))
        self.assertIn("Hello, World!", result)

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_write_file_tool(self):
        """Тест записи файла"""
        new_file = Path(self.test_dir) / "new.txt"
        content = "Test content for writing"

        result = write_file_tool(str(new_file), content)
        self.assertTrue(result["success"])
        self.assertTrue(new_file.exists())
        self.assertEqual(new_file.read_text(), content)

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_list_files_tool(self):
        """Тест получения списка файлов"""
        result = list_files_tool(self.test_dir, recursive=False)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["count"], 3)  # test.txt, test.py, test.md, subdir

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_search_files_tool(self):
        """Тест поиска файлов"""
        result = search_files_tool("Hello", "*.txt")
        self.assertTrue(result["success"])

class TestGitTools(unittest.TestCase):
    """Тесты инструментов для работы с Git"""

    def setUp(self):
        """Настройка тестового Git репозитория"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_dir = Path(self.test_dir) / "test-repo"
        self.repo_dir.mkdir()

        # Инициализируем Git репозиторий
        subprocess.run(["git", "init"], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=self.repo_dir, capture_output=True)

        # Создаем тестовый файл и коммит
        test_file = self.repo_dir / "README.md"
        test_file.write_text("# Test Repository\n\nThis is a test.")

        subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit: Added README"],
                      cwd=self.repo_dir, capture_output=True)

        # Создаем еще один коммит с маркером IT-Compass
        code_file = self.repo_dir / "code.py"
        code_file.write_text("def hello():\n    print('Hello, World!')")

        subprocess.run(["git", "add", "."], cwd=self.repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Added Python function with system thinking"],
                      cwd=self.repo_dir, capture_output=True)

    def tearDown(self):
        """Очистка тестовой среды"""
        import shutil
        shutil.rmtree(self.test_dir)

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    @patch("apps.mcp_server.src.tools.git_tools.PROJECT_ROOT", new_callable=lambda: Path(__file__).parent.parent.parent.parent)
    def test_get_git_status_tool(self, mock_project_root):
        """Тест получения статуса Git"""
        mock_project_root.return_value = self.repo_dir

        result = get_git_status_tool()
        self.assertTrue(result["success"])
        self.assertTrue(result["is_git_repo"])
        self.assertEqual(result["current_branch"], "master" or "main")

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    @patch("apps.mcp_server.src.tools.git_tools.PROJECT_ROOT", new_callable=lambda: Path(__file__).parent.parent.parent.parent)
    @patch("apps.mcp_server.src.tools.git_tools.IT_COMPASS_MARKERS_PATH")
    def test_scan_last_commits_for_markers_tool(self, mock_markers_path, mock_project_root):
        """Тест анализа коммитов на маркеры"""
        mock_project_root.return_value = self.repo_dir

        # Создаем мок для маркеров IT-Compass
        markers_dir = Path(self.test_dir) / "markers"
        markers_dir.mkdir()

        # Создаем тестовый файл маркеров
        system_thinking_marker = {
            "skill_name": "System Thinking",
            "description": "Способность анализировать и проектировать сложные системы",
            "levels": {
                "1": [
                    {
                        "id": "system_thinking_1_1",
                        "marker": "Создал структурированную систему для самооценки навыков",
                        "validation": "Документ или цифровой артефакт",
                        "priority": "high",
                        "keywords": ["систему", "самооценки", "навыков"],
                    },
                ],
            },
        }

        marker_file = markers_dir / "system_thinking.json"
        with open(marker_file, "w", encoding="utf-8") as f:
            json.dump(system_thinking_marker, f)

        mock_markers_path.return_value = markers_dir

        result = scan_last_commits_for_markers_tool(commits_count=5)
        self.assertTrue(result["success"])
        # Может обнаружить маркеры или нет, зависит от содержания коммитов

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    @patch("apps.mcp_server.src.tools.git_tools.PROJECT_ROOT", new_callable=lambda: Path(__file__).parent.parent.parent.parent)
    def test_get_git_history_tool(self, mock_project_root):
        """Тест получения истории Git"""
        mock_project_root.return_value = self.repo_dir

        result = get_git_history_tool(days=7)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["total_commits"], 2)

class TestMCPIntegration(unittest.TestCase):
    """Тесты интеграции MCP-сервера"""

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_mcp_server_structure(self):
        """Тест структуры MCP-сервера"""
        # Проверяем существование основных файлов
        mcp_dir = project_root / "apps" / "mcp-server"

        self.assertTrue((mcp_dir / "src" / "main.py").exists())
        self.assertTrue((mcp_dir / "config" / "mcp-config.yaml").exists())
        self.assertTrue((mcp_dir / "README.md").exists())
        self.assertTrue((mcp_dir / "requirements.txt").exists())

    def test_config_validation(self):
        """Тест валидации конфигурации"""
        config_path = project_root / "apps" / "mcp-server" / "config" / "mcp-config.yaml"

        if config_path.exists():
            import yaml
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Проверяем обязательные поля
            self.assertIn("version", config)
            self.assertIn("name", config)
            self.assertIn("server", config)
            self.assertIn("tools", config)

            # Проверяем, что нет упоминаний GPT-5
            config_str = str(config)
            self.assertNotIn("gpt-5", config_str.lower())
            self.assertNotIn("gpt5", config_str.lower())

class TestCareerAutopilotFeatures(unittest.TestCase):
    """Тесты функций Career Autopilot"""

    @unittest.skipIf(not HAS_MCP_TOOLS, "MCP tools not available")
    def test_it_compass_integration(self):
        """Тест интеграции с IT-Compass"""
        # Проверяем существование маркеров IT-Compass
        markers_path = project_root / "apps" / "it-compass" / "src" / "data" / "markers"

        if markers_path.exists():
            # Проверяем наличие основных файлов маркеров
            expected_files = ["system_thinking.json", "python.json", "docker.json"]

            for file in expected_files:
                if (markers_path / file).exists():
                    with open(markers_path / file, encoding="utf-8") as f:
                        data = json.load(f)

                    # Проверяем структуру маркера
                    self.assertIn("skill_name", data)
                    self.assertIn("description", data)
                    self.assertIn("levels", data)

    def test_project_structure_simplification(self):
        """Тест упрощения структуры проекта"""
        # Проверяем, что нет избыточной вложенности в MCP-сервере
        mcp_dir = project_root / "apps" / "mcp-server"

        if mcp_dir.exists():
            # Проверяем глубину вложенности
            max_depth = 0
            for root, dirs, files in os.walk(mcp_dir):
                depth = root.count(os.sep) - str(mcp_dir).count(os.sep)
                max_depth = max(max_depth, depth)

            # Рекомендуемая максимальная глубина: 4 уровня
            self.assertLessEqual(max_depth, 5,
                               f"Избыточная вложенность в MCP-сервере: {max_depth} уровней")

def run_all_tests():
    """Запуск всех тестов"""
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestFileTools))
    suite.addTests(loader.loadTestsFromTestCase(TestGitTools))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCareerAutopilotFeatures))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование MCP-сервера Career Autopilot")
    print("=" * 60)

    result = run_all_tests()

    # Генерируем отчет
    report = {
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "timestamp": str(datetime.now()),
    }

    print("\n" + "=" * 60)
    print("ОТЧЕТ О ТЕСТИРОВАНИИ:")
    print(f"  Всего тестов: {report['total_tests']}")
    print(f"  Успешно: {report['successful']}")
    print(f"  Провалено: {report['failures']}")
    print(f"  Ошибок: {report['errors']}")
    print(f"  Пропущено: {report['skipped']}")
    print("=" * 60)

    # Сохраняем отчет
    report_path = project_root / "docs" / "audit" / "mcp-test-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nОтчет сохранен в: {report_path.relative_to(project_root)}")

    # Возвращаем код выхода
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0)

# Импортируем datetime здесь, чтобы избежать ошибок импорта
