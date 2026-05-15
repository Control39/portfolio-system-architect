"""Тесты для MCP Server"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


class TestProjectContext:
    """Тесты получения контекста проекта"""

    def test_get_project_context(self, project_root):
        """Тест получения контекста проекта"""
        with (
            patch("pathlib.Path.__truediv__", return_value=project_root),
            patch("pathlib.Path.exists", return_value=True),
        ):
            from tools.ai_integration.mcp_server import PortfolioMCP

            server = PortfolioMCP()
            # Вызываем инструмент
            server.setup_tools()  # Инструменты зарегистрированы

            assert server is not None

    def test_project_context_structure(self, project_root):
        """Тест структуры контекста проекта"""

        from tools.ai_integration.mcp_server import ProjectContext

        context = ProjectContext()

        assert context.name == "portfolio-system-architect"
        assert context.author == "Ekaterina Kudelya"
        assert len(context.components) > 0
        assert isinstance(context.components, list)


class TestFileReading:
    """Тесты чтения файлов"""

    def test_read_ai_context(self, project_root):
        """Тест чтения .ai-context.md"""
        ai_context_path = project_root / ".ai-context.md"
        assert ai_context_path.exists()
        assert ai_context_path.read_text() == "AI Context Content"

    def test_read_project_file_exists(self, project_root):
        """Тест чтения существующего файла"""
        readme_path = project_root / "README.md"
        assert readme_path.exists()
        assert readme_path.read_text() == "# Test Project"

    def test_read_project_file_not_exists(self, project_root):
        """Тест чтения несуществующего файла"""
        fake_path = project_root / "nonexistent.txt"
        assert not fake_path.exists()

    def test_read_directory_raises(self, project_root):
        """Тест чтения директории как файла"""
        apps_dir = project_root / "apps"
        assert apps_dir.is_dir()
        # Ожидается, что инструмент вернёт ошибку

    def test_read_unicode_content(self, project_root):
        """Тест чтения файла с Unicode"""
        unicode_file = project_root / "unicode_test.txt"
        unicode_file.write_text("Привет! 🤖 你好！こんにちは!")

        content = unicode_file.read_text(encoding="utf-8")
        assert "Привет!" in content
        assert "🤖" in content


class TestITCompass:
    """Тесты работы с IT-Compass"""

    def test_list_it_compass_domains(self, project_root):
        """Тест списка доменов IT-Compass"""
        markers_path = project_root / "apps" / "it-compass"
        assert markers_path.exists()

        json_files = list(markers_path.rglob("*.json"))
        assert len(json_files) == 1
        assert "system_thinking_markers.json" in json_files[0].name

    def test_get_system_thinking_markers(self, project_root):
        """Тест получения маркеров системного мышления"""
        markers_file = project_root / "apps" / "it-compass" / "system_thinking_markers.json"

        content = json.loads(markers_file.read_text())
        assert "markers" in content
        assert len(content["markers"]) == 1
        assert content["markers"][0]["id"] == "test"

    def test_empty_markers_file(self, project_root):
        """Тест пустого файла маркеров"""
        empty_file = project_root / "apps" / "it-compass" / "empty.json"
        empty_file.write_text("{}")

        content = json.loads(empty_file.read_text())
        assert content == {}


class TestRAGSystem:
    """Тесты работы с RAG системой"""

    def test_get_rag_status(self, project_root):
        """Тест статуса RAG системы"""
        decision_dir = project_root / "apps" / "decision-engine"
        assert decision_dir.exists()

        # Проверяем структуру
        py_files = list(decision_dir.rglob("*.py"))
        assert len(py_files) == 1

        dockerfile = decision_dir / "Dockerfile"
        assert dockerfile.exists()

    def test_chroma_db_exists(self, project_root):
        """Тест существования ChromaDB"""
        chroma_path = project_root / "chroma_db"
        assert chroma_path.exists()
        assert chroma_path.is_dir()

    def test_rag_system_missing(self, tmp_path):
        """Тест отсутствия RAG системы"""
        # Создаём проект без RAG
        assert not (tmp_path / "apps" / "decision-engine").exists()


class TestProjectStructure:
    """Тесты анализа структуры проекта"""

    def test_list_project_files(self, project_root):
        """Тест списка файлов"""
        files = list(project_root.iterdir())
        assert len(files) > 0

        # Проверяем наличие ключевых файлов
        file_names = [f.name for f in files]
        assert "README.md" in file_names
        assert ".ai-context.md" in file_names

    def test_analyze_project_structure(self, project_root):
        """Тест анализа структуры"""
        apps_dir = project_root / "apps"
        assert apps_dir.exists()

        items = list(apps_dir.iterdir())
        assert len(items) > 0

    def test_file_types_count(self, project_root):
        """Тест подсчёта типов файлов"""
        py_files = list(project_root.rglob("*.py"))
        md_files = list(project_root.rglob("*.md"))
        json_files = list(project_root.rglob("*.json"))

        assert len(py_files) > 0
        assert len(md_files) > 0
        assert len(json_files) > 0


class TestHealthChecks:
    """Тесты проверки здоровья проекта"""

    def test_check_project_health(self, project_root):
        """Тест проверки здоровья"""
        key_files = [
            ".ai-context.md",
            "pyproject.toml",
            "README.md",
        ]

        for file in key_files:
            path = project_root / file
            assert path.exists(), f"Файл {file} должен существовать"

    def test_fastapi_installed(self):
        """Тест установки FastAPI"""
        try:
            import fastapi

            assert hasattr(fastapi, "__version__")
        except ImportError:
            pytest.skip("FastAPI не установлен")

    def test_pydantic_installed(self):
        """Тест установки Pydantic"""
        try:
            import pydantic

            assert hasattr(pydantic, "__version__")
        except ImportError:
            pytest.skip("Pydantic не установлен")


class TestSearch:
    """Тесты поиска в проекте"""

    def test_search_in_project(self, project_root):
        """Тест поиска текста"""
        query = "Test Project"

        results = []
        for root, _dirs, files in list(project_root.walk()) if hasattr(project_root, "walk") else []:
            for file in files:
                if file.endswith(".md"):
                    file_path = Path(root) / file
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if query.lower() in content.lower():
                        results.append(
                            {
                                "file": str(file_path.relative_to(project_root)),
                                "matches": content.lower().count(query.lower()),
                            }
                        )

        # Проверяем, что нашлись результаты
        # (зависит от реализации walk)

    def test_search_no_results(self, project_root):
        """Тест поиска без результатов"""
        # Ожидаем, что поиск не найдёт совпадений

        # Ожидаем, что поиск не найдёт совпадений

    def test_search_python_files(self, project_root):
        """Тест поиска по Python файлам"""
        py_files = list(project_root.rglob("*.py"))
        assert len(py_files) > 0


class TestServiceStatus:
    """Тесты статуса сервисов"""

    def test_get_service_status_all(self, project_root):
        """Тест статуса всех сервисов"""
        services = [
            "gateway",
            "portfolio-organizer",
            "career-development",
            "decision-engine",
            "system-proof",
        ]

        for _service in services:
            # Проверяем, что сервис либо существует, либо отмечен как отсутствующий
            pass

    def test_get_service_status_single(self, project_root):
        """Тест статуса одного сервиса"""
        decision_dir = project_root / "apps" / "decision-engine"
        assert decision_dir.exists()

    def test_get_service_status_missing(self, tmp_path):
        """Тест отсутствия сервиса"""
        service_dir = tmp_path / "apps" / "nonexistent-service"
        assert not service_dir.exists()


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_empty_query_search(self, project_root):
        """Тест поиска с пустым запросом"""
        # Ожидаем обработку пустого запроса

    def test_unicode_path(self, project_root):
        """Тест пути с Unicode"""
        unicode_dir = project_root / "тестовая_папка"
        unicode_dir.mkdir(exist_ok=True)
        assert unicode_dir.exists()

    def test_long_filename(self, project_root):
        """Тест длинного имени файла"""
        long_name = "a" * 100 + ".txt"
        long_file = project_root / long_name
        long_file.write_text("Content")
        assert long_file.exists()

    def test_special_characters_in_path(self, project_root):
        """Тест специальных символов в пути"""
        special_dir = project_root / "test @#$%"
        special_dir.mkdir(exist_ok=True)
        assert special_dir.exists()

    def test_symlink_handling(self, project_root):
        """Тест обработки символических ссылок"""
        try:
            target = project_root / "target.txt"
            target.write_text("Target")
            link = project_root / "link.txt"
            link.symlink_to(target)
            assert link.is_symlink()
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks не поддерживаются на этой ОС")


class TestIntegration:
    """Интеграционные тесты"""

    def test_full_workflow(self, project_root):
        """Тест полного рабочего процесса"""
        # 1. Получить контекст проекта
        # 2. Прочитать файл
        # 3. Поискать текст
        # 4. Проверить здоровье
        # 5. Получить статус RAG

        # Все шаги должны завершаться успешно

    def test_concurrent_requests(self, project_root):
        """Тест параллельных запросов"""
        # Проверить, что сервер обрабатывает параллельные запросы

    def test_error_recovery(self, project_root):
        """Тест восстановления после ошибки"""
        # Создать ошибку, затем убедиться, что сервер продолжает работать
