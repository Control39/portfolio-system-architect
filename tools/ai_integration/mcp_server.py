#!/usr/bin/env python3
"""
MCP сервер для портфолио системного архитектора.
Предоставляет инструменты для работы с IT-Compass, RAG системой и профессиональным контекстом.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess

# Добавляем путь к проекту для импорта модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp import Server, StdioServerTransport, Tool
    from mcp.types import TextContent, Tool as ToolType
    from pydantic import BaseModel, Field
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("MCP библиотека не установлена. Установите: pip install mcp", file=sys.stderr)

class ProjectContext(BaseModel):
    """Контекст проекта"""
    name: str = "portfolio-system-architect"
    author: str = "Ekaterina Kudelya"
    description: str = "Когнитивная архитектура для системного мышления"
    components: List[str] = Field(default_factory=lambda: [
        "IT-Compass", "RAG System", "System Thinking Markers", 
        "Portfolio Organizer", "Cloud-Reason", "Career Development"
    ])

class ITCompassQuery(BaseModel):
    """Запрос к IT-Compass"""
    domain: Optional[str] = None
    level: Optional[str] = None

class FileReadRequest(BaseModel):
    """Запрос на чтение файла"""
    path: str

class PortfolioMCP:
    """MCP сервер для портфолио"""
    
    def __init__(self):
        self.server = Server("portfolio-mcp-server", "0.1.0")
        self.setup_tools()
        
    def setup_tools(self):
        """Настройка инструментов MCP"""
        
        @self.server.tool()
        async def get_project_context() -> List[TextContent]:
            """Получить контекст проекта"""
            context = ProjectContext()
            return [TextContent(
                type="text",
                text=json.dumps(context.dict(), indent=2, ensure_ascii=False)
            )]
        
        @self.server.tool()
        async def read_ai_context() -> List[TextContent]:
            """Прочитать файл .ai-context.md"""
            try:
                path = project_root / ".ai-context.md"
                content = path.read_text(encoding="utf-8")
                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]
        
        @self.server.tool()
        async def list_it_compass_domains() -> List[TextContent]:
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
                    domains = ["IT-Compass маркеры находятся в apps/it-compass/"]
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"domains": domains}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]
        
        @self.server.tool()
        async def get_professional_journey() -> List[TextContent]:
            """Получить профессиональный путь автора"""
            try:
                readme_path = project_root / "docs" / "professional-journey" / "README.md"
                content = readme_path.read_text(encoding="utf-8")
                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]
        
        @self.server.tool()
        async def list_project_files(directory: str = ".") -> List[TextContent]:
            """Список файлов в проекте"""
            try:
                target_path = project_root / directory
                if not target_path.exists():
                    return [TextContent(type="text", text=f"Директория не существует: {directory}")]
                
                files = []
                for item in target_path.iterdir():
                    files.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"directory": directory, "files": files}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]
        
        @self.server.tool()
        async def check_project_health() -> List[TextContent]:
            """Проверить здоровье проекта"""
            try:
                checks = []
                
                # Проверка существования ключевых файлов
                key_files = [
                    ".ai-context.md",
                    "pyproject.toml",
                    "README.md",
                    "docs/professional-journey/README.md"
                ]
                
                for file in key_files:
                    path = project_root / file
                    checks.append({
                        "file": file,
                        "exists": path.exists(),
                        "size": path.stat().st_size if path.exists() else 0
                    })
                
                # Проверка Python окружения
                try:
                    import fastapi
                    checks.append({"check": "FastAPI", "status": "OK", "version": fastapi.__version__})
                except ImportError:
                    checks.append({"check": "FastAPI", "status": "NOT_INSTALLED"})
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"health_checks": checks}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

        @self.server.tool()
        async def read_project_file(path: str) -> List[TextContent]:
            """Прочитать любой файл проекта"""
            try:
                file_path = project_root / path
                if not file_path.exists():
                    return [TextContent(type="text", text=f"Файл не существует: {path}")]
                if file_path.is_dir():
                    return [TextContent(type="text", text=f"Это директория, а не файл: {path}")]
                
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                return [TextContent(type="text", text=content)]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка чтения файла: {str(e)}")]

        @self.server.tool()
        async def get_system_thinking_markers() -> List[TextContent]:
            """Получить маркеры системного мышления"""
            try:
                markers_path = project_root / "apps" / "it-compass"
                marker_files = []
                
                if markers_path.exists():
                    for item in markers_path.rglob("*.json"):
                        if "system" in item.name.lower() or "thinking" in item.name.lower():
                            try:
                                content = json.loads(item.read_text(encoding="utf-8"))
                                marker_files.append({
                                    "file": str(item.relative_to(project_root)),
                                    "markers_count": len(content.get("markers", [])) if isinstance(content, dict) else "unknown"
                                })
                            except:
                                marker_files.append({"file": str(item.relative_to(project_root)), "error": "parse_error"})
                
                if not marker_files:
                    # Попробуем найти в других местах
                    search_paths = [project_root / "docs", project_root / "src"]
                    for sp in search_paths:
                        if sp.exists():
                            for item in sp.rglob("system_thinking*.json"):
                                marker_files.append({"file": str(item.relative_to(project_root))})
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"system_thinking_markers": marker_files}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

        @self.server.tool()
        async def get_rag_status() -> List[TextContent]:
            """Получить статус RAG системы"""
            try:
                rag_paths = [
                    project_root / "apps" / "cloud-reason",
                    project_root / "apps" / "system-proof",
                    project_root / "gateway"
                ]
                
                status = {}
                for path in rag_paths:
                    if path.exists():
                        files = list(path.rglob("*.py")) + list(path.rglob("*.yaml")) + list(path.rglob("*.yml"))
                        status[str(path.relative_to(project_root))] = {
                            "exists": True,
                            "file_count": len(files),
                            "has_docker": (path / "Dockerfile").exists()
                        }
                    else:
                        status[str(path.relative_to(project_root))] = {"exists": False}
                
                # Проверка Chroma DB
                chroma_path = project_root / "chroma_db"
                status["chroma_db"] = {
                    "exists": chroma_path.exists(),
                    "is_dir": chroma_path.is_dir() if chroma_path.exists() else False
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"rag_system_status": status}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

        @self.server.tool()
        async def search_in_project(query: str, file_pattern: str = "*.py") -> List[TextContent]:
            """Поиск текста в файлах проекта"""
            try:
                import fnmatch
                
                results = []
                for root, dirs, files in os.walk(project_root):
                    # Пропускаем некоторые директории
                    skip_dirs = ['.git', '__pycache__', 'node_modules', '.venv']
                    dirs[:] = [d for d in dirs if d not in skip_dirs]
                    
                    for file in files:
                        if fnmatch.fnmatch(file, file_pattern):
                            file_path = Path(root) / file
                            try:
                                content = file_path.read_text(encoding="utf-8", errors="ignore")
                                if query.lower() in content.lower():
                                    results.append({
                                        "file": str(file_path.relative_to(project_root)),
                                        "matches": content.lower().count(query.lower())
                                    })
                            except:
                                continue
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "query": query,
                        "file_pattern": file_pattern,
                        "results_count": len(results),
                        "results": results[:20]  # Ограничиваем вывод
                    }, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

        @self.server.tool()
        async def get_service_status(service: str = "all") -> List[TextContent]:
            """Получить статус сервисов проекта"""
            try:
                services = {
                    "gateway": {
                        "path": "gateway/main.py",
                        "description": "API Gateway для маршрутизации запросов"
                    },
                    "portfolio-organizer": {
                        "path": "apps/portfolio-organizer/src/app.py",
                        "description": "Организатор портфолио"
                    },
                    "career-development": {
                        "path": "apps/career-development/src",
                        "description": "Система развития карьеры"
                    },
                    "cloud-reason": {
                        "path": "apps/cloud-reason",
                        "description": "RAG и reasoning система"
                    },
                    "system-proof": {
                        "path": "apps/system-proof",
                        "description": "Система доказательств и верификации"
                    }
                }
                
                status = {}
                for name, info in services.items():
                    if service != "all" and service != name:
                        continue
                    
                    path = project_root / info["path"]
                    exists = path.exists()
                    files = []
                    
                    if exists:
                        if path.is_file():
                            files = [{"name": path.name, "size": path.stat().st_size}]
                        elif path.is_dir():
                            py_files = list(path.rglob("*.py"))
                            files = [{"name": f.name, "size": f.stat().st_size} for f in py_files[:5]]
                    
                    status[name] = {
                        "exists": exists,
                        "description": info["description"],
                        "file_count": len(files) if path.is_dir() else 1,
                        "files_sample": files
                    }
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"services_status": status}, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

        @self.server.tool()
        async def analyze_project_structure() -> List[TextContent]:
            """Анализ структуры проекта"""
            try:
                structure = {
                    "apps": {},
                    "docs": {},
                    "scripts": {},
                    "tools": {}
                }
                
                for section in structure.keys():
                    section_path = project_root / section
                    if section_path.exists() and section_path.is_dir():
                        items = list(section_path.iterdir())
                        structure[section] = {
                            "item_count": len(items),
                            "items": [{"name": item.name, "type": "dir" if item.is_dir() else "file"} for item in items[:10]]
                        }
                
                # Подсчет файлов по типам
                file_types = {}
                for root, dirs, files in os.walk(project_root):
                    # Пропускаем скрытые директории
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        ext = os.path.splitext(file)[1]
                        if ext:
                            file_types[ext] = file_types.get(ext, 0) + 1
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "project_structure": structure,
                        "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10])
                    }, indent=2, ensure_ascii=False)
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

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
