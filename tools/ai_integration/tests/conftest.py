"""Конфигурация для тестов MCP сервера"""

import json
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def project_root(tmp_path):
    """Создание временной структуры проекта"""
    # Создаем тестовые файлы
    (tmp_path / ".ai-context.md").write_text("AI Context Content")
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "pyproject.toml").write_text("[project]")

    # Создаем директории
    apps_dir = tmp_path / "apps" / "it-compass"
    apps_dir.mkdir(parents=True)
    (apps_dir / "system_thinking_markers.json").write_text(
        json.dumps({"markers": [{"id": "test", "name": "Test Marker"}]})
    )

    docs_dir = tmp_path / "docs" / "professional-journey"
    docs_dir.mkdir(parents=True)
    (docs_dir / "README.md").write_text("# Professional Journey")

    # Создаем chroma_db
    (tmp_path / "chroma_db").mkdir()

    # Создаем decision-engine
    decision_dir = tmp_path / "apps" / "decision-engine"
    decision_dir.mkdir(parents=True)
    (decision_dir / "main.py").write_text("# Decision Engine")
    (decision_dir / "Dockerfile").write_text("# Dockerfile")

    return tmp_path


@pytest.fixture
def mcp_server(project_root):
    """Создание экземпляра MCP сервера"""
    import sys
    from unittest.mock import patch

    # Мокируем MCP библиотеку
    with patch.dict(
        sys.modules,
        {"mcp": MagicMock(), "mcp.types": MagicMock()},
    ):
        from tools.ai_integration.mcp_server import PortfolioMCP

        return PortfolioMCP()
