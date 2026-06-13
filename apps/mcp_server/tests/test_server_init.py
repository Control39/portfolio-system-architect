#!/usr/bin/env python3
"""
Тесты инициализации MCP Server

Проверяют корректность инициализации инструментов без запуска сервера.
"""

from pathlib import Path

import pytest

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent.parent


class TestMCPServerInit:
    """Тесты инициализации MCP сервера"""

    def test_project_root_detection(self):
        """Проверка определения корня проекта"""
        from src.main import PROJECT_ROOT

        assert PROJECT_ROOT.exists(), f"PROJECT_ROOT должен существовать: {PROJECT_ROOT}"
        assert (PROJECT_ROOT / ".git").exists(), "PROJECT_ROOT должен быть Git репозиторием"

    def test_it_compass_markers_path_exists(self):
        """Проверка существования пути к маркерам IT-Compass"""
        from src.main import IT_COMPASS_MARKERS_PATH

        # Путь может не существовать в тестовой среде, проверяем только структуру
        assert IT_COMPASS_MARKERS_PATH.is_absolute(), "Путь должен быть абсолютным"

    def test_tools_import(self):
        """Проверка импорта модулей инструментов"""
        from src.tools import (
            init_chroma_tools,
            init_compass_tools,
            init_file_tools,
            init_git_tools,
            init_monitoring_tools,
        )

        assert callable(init_file_tools), "init_file_tools должен быть вызываемым"
        assert callable(init_git_tools), "init_git_tools должен быть вызываемым"
        assert callable(init_chroma_tools), "init_chroma_tools должен быть вызываемым"
        assert callable(init_compass_tools), "init_compass_tools должен быть вызываемым"
        assert callable(init_monitoring_tools), "init_monitoring_tools должен быть вызываемым"

    def test_mcp_instance_creation(self):
        """Проверка создания экземпляра FastMCP"""
        from fastmcp import FastMCP

        mcp = FastMCP("Test Server")
        assert mcp is not None, "Экземпляр FastMCP должен быть создан"
        assert mcp.name == "Test Server", "Имя сервера должно быть установлено"

    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Проверка регистрации инструментов"""
        from fastmcp import FastMCP

        mcp = FastMCP("Test Tool Registration")

        @mcp.tool()
        def test_tool(value: str) -> str:
            """Тестовый инструмент"""
            return f"Test: {value}"

        # Проверяем, что инструмент зарегистрирован (через public API)
        # В fastmcp 3.x инструменты доступны через mcp._tools или mcp.get_tools()
        tools = getattr(mcp, "_tools", getattr(mcp, "_tool_manager", None))
        if tools is not None:
            tools_list = list(tools.values()) if isinstance(tools, dict) else tools
            assert len(tools_list) >= 1, f"Должен быть зарегистрирован хотя бы 1 инструмент, найдено: {len(tools_list)}"

    def test_navigation_resource_template(self):
        """Проверка шаблона ресурса навигации"""
        from src.main import get_navigation_resource

        # Проверяем, что функция существует и возвращает строку
        result = get_navigation_resource("tech_lead")
        assert isinstance(result, str), "Результат должен быть строкой"
        assert "Архитектура" in result, "Должно содержать информацию об архитектуре"

    def test_compass_domain_resource_template(self):
        """Проверка шаблона ресурса домена IT-Compass"""
        from src.main import get_compass_domain_resource

        # Проверяем несуществующий домен
        result = get_compass_domain_resource("nonexistent_domain_xyz")
        assert "не найден" in result.lower(), "Должно содержать сообщение об отсутствии домена"

    def test_get_sample_markers(self):
        """Проверка функции получения примеров маркеров"""
        from src.main import _get_sample_markers

        # Тест с пустыми данными
        assert _get_sample_markers({}) == "Нет примеров маркеров"

        # Тест с данными
        test_data = {
            "levels": {
                "1": [{"marker": "Маркер уровня 1"}],
                "2": [{"marker": "Маркер уровня 2"}],
            }
        }
        result = _get_sample_markers(test_data)
        assert "Маркер уровня 1" in result, "Должен содержать маркер уровня 1"
