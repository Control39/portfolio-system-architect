#!/usr/bin/env python3
"""MCP сервер для портфолио системного архитектора.
Предоставляет инструменты для работы с IT-Compass, RAG системой и профессиональным контекстом.
"""

import json
import os
import sys
from pathlib import Path

# Добавляем путь к проекту для импорта модулей
project_root = Path(__file__).parent.parent

try:
    import importlib.util

    if importlib.util.find_spec("mcp") is not None:
        from mcp import Server, StdioServerTransport, Tool  # noqa: F401
        from mcp.types import (
            TextContent,
        )
        from mcp.types import (
            Tool as ToolType,  # noqa: F401
        )

        HAS_MCP = True
    else:
        HAS_MCP = False

    if importlib.util.find_spec("pydantic") is not None:
        from pydantic import BaseModel, Field
    else:
        HAS_MCP = False
except ImportError:
    HAS_MCP = False
    print("MCP библиотека не установлена. Установите: pip install mcp", file=sys.stderr)


class ProjectContext(BaseModel):
    """Контекст проекта"""

    name: str = "portfolio-system-architect"
    author: str = "Ekaterina Kudelya"
    description: str = "Когнитивная архитектура для системного мышления"
    components: list[str] = Field(
        default_factory=lambda: [
            "IT-Compass",
            "RAG System",
            "System Thinking Markers",
            "Portfolio Organizer",
            "Decision Engine",
            "Career Development",
        ]
    )


class ITCompassQuery(BaseModel):
    """Запрос к IT-Compass"""

    domain: str | None = None
    level: str | None = None


class FileReadRequest(BaseModel):
    """Запрос на чтение файла"""

    path: str


class PortfolioMCP:
    """MCP сервер для портфолио"""

    def __init__(self):
        self.server = Server("portfolio-mcp-server", "0.1.0")
        self.giga_bridge = None
        self.setup_tools()
        self._initialize_giga_bridge()

    def _initialize_giga_bridge(self) -> None:
        """Initialize GigaChat bridge if available."""
        try:
            # Пытаемся импортировать GigaMCPBridge
            import logging
            logger = logging.getLogger(__name__)
            
            sys.path.insert(0, str(project_root))
            from src.ai.gigachat_bridge import GigaMCPBridge
            self.giga_bridge = GigaMCPBridge()
            logger.info("GigaChat bridge initialized successfully")
        except ImportError:
            logger.warning("GigaChat bridge module not available")
            self.giga_bridge = None
        except Exception as e:
            logger.warning(f"GigaChat bridge not available: {e}")
            self.giga_bridge = None

    def setup_tools(self):
        """Настройка инструментов MCP"""

        @self.server.tool()
        async def get_project_context() -> list[TextContent]:
            """Получить контекст проекта"""
            context = ProjectContext()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(context.dict(), indent=2, ensure_ascii=False),
                )
            ]

        @self.server.tool()
        async def read_ai_context() -> list[TextContent]:
            """Прочитать файл .ai-context.md"""
            try:
                path = project_root / ".ai-context.md"
                content = path.read_text(encoding="utf-8")
                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {e!s}")]

        @self.server.tool()
        async def list_it_compass_domains() -> list[TextContent]:
            """Получить список доменов IT-Compass"""
            try:
                # Попробуем найти файлы IT-Compass
                domains = []
                markers_path = project_root / "apps" / "it-compass"
                if markers_path.exists():
                    for item in markers_path.rglob("*.json"):
                        if "marker" in item.name.lower() or "system" in item.name.lower():
                            domains.append(str(item.relative_to(project_root)))

                if not domains:
                    domains = ["IT-Compass маркеры находятся в apps/it_compass/"]

                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"domains": domains}, indent=2, ensure_ascii=False),
                    )
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {e!s}")]

        @self.server.tool()
        async def search_knowledge_base(query: str) -> list[TextContent]:
            """Поиск в базе знаний"""
            try:
                # Простая реализация поиска
                results = []
                for root, dirs, files in os.walk(project_root):
                    for file in files:
                        if query.lower() in file.lower():
                            results.append(os.path.join(root, file))
                
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"results": results[:10]}, indent=2, ensure_ascii=False),
                    )
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {e!s}")]

        @self.server.tool()
        async def get_system_status() -> list[TextContent]:
            """Получить статус системы"""
            status = {
                "server_name": "portfolio-mcp-server",
                "version": "0.1.0",
                "has_mcp": HAS_MCP,
                "giga_bridge_available": self.giga_bridge is not None,
                "project_root": str(project_root),
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(status, indent=2, ensure_ascii=False),
                )
            ]


async def main():
    """Основная функция"""
    if not HAS_MCP:
        print("Ошибка: библиотека MCP не установлена.", file=sys.stderr)
        print("Установите: pip install mcp", file=sys.stderr)
        sys.exit(1)

    server = PortfolioMCP()
    transport = StdioServerTransport()

    print("Запуск MCP сервера для портфолио...", file=sys.stderr)
    await server.server.connect(transport)
    print("MCP сервер запущен на stdio", file=sys.stderr)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
