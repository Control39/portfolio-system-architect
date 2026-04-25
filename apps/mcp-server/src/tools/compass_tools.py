#!/usr/bin/env python3
"""
IT-Compass Tools для MCP Server

Инструменты для работы с маркерами компетенций IT-Compass.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Инициализация MCP (будет передан из main)
mcp: Optional[FastMCP] = None

def init_compass_tools(mcp_server: FastMCP, project_root: Path) -> None:
    """Инициализация инструментов IT-Compass"""
    global mcp
    mcp = mcp_server
    
    markers_path = project_root / "apps" / "it-compass" / "src" / "data" / "markers"
    
    @mcp.tool()
    def evaluate_by_compass(domain: str, level: Optional[int] = None) -> Dict[str, Any]:
        """
        Оценка компетенций по домену IT-Compass
        
        Аргументы:
            domain: Домен (system_thinking, python, docker, devops, etc.)
            level: Уровень (1-5), если None - все уровни
        
        Возвращает:
            Dict с маркерами и статусами
        """
        domain_file = markers_path / f"{domain}.json"
        
        if not domain_file.exists():
            return {
                "error": f"Домен '{domain}' не найден",
                "available_domains": get_available_domains()
            }
        
        try:
            with open(domain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = {
                "domain": domain,
                "skill_name": data.get("skill_name", domain),
                "description": data.get("description", ""),
                "levels": {}
            }
            
            all_levels = data.get("levels", {})
            
            if level:
                if str(level) in all_levels:
                    result["levels"][str(level)] = all_levels[str(level)]
                else:
                    result["error"] = f"Уровень {level} не найден"
            else:
                result["levels"] = all_levels
            
            result["total_markers"] = sum(len(markers) for markers in result["levels"].values())
            
            return result
            
        except Exception as e:
            return {"error": f"Ошибка при чтении домена: {str(e)}"}
    
    @mcp.tool()
    def get_markers_by_domain(domain: str) -> List[Dict[str, Any]]:
        """
        Получение всех маркеров для домена
        
        Аргументы:
            domain: Домен IT-Compass
        
        Возвращает:
            Список маркеров с уровнями
        """
        domain_file = markers_path / f"{domain}.json"
        
        if not domain_file.exists():
            return []
        
        try:
            with open(domain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            markers = []
            for level_num, level_markers in data.get("levels", {}).items():
                for marker in level_markers:
                    markers.append({
                        "level": int(level_num),
                        "marker": marker.get("marker", ""),
                        "description": marker.get("description", "")
                    })
            
            return markers
            
        except Exception:
            return []
    
    @mcp.tool()
    def get_available_domains() -> List[str]:
        """
        Получение списка доступных доменов IT-Compass
        
        Возвращает:
            Список названий доменов
        """
        if not markers_path.exists():
            return []
        
        domains = []
        for file in markers_path.glob("*.json"):
            domain_name = file.stem
            domains.append(domain_name)
        
        return sorted(domains)
    
    @mcp.tool()
    def auto_detect_markers_from_code(code_path: str) -> List[Dict[str, str]]:
        """
        Автоматическое обнаружение маркеров из кода
        
        Аргументы:
            code_path: Путь к файлу или директории с кодом
        
        Возвращает:
            Список обнаруженных маркеров с доменами и уровнями
        """
        detected = []
        
        # Паттерны для обнаружения маркеров
        marker_patterns = {
            "python": {
                "type_hints": {"level": 2, "pattern": ["def ", ": ", "->"]},
                "async_await": {"level": 3, "pattern": ["async ", "await "]},
                "decorators": {"level": 2, "pattern": ["@"]},
                "context_managers": {"level": 3, "pattern": ["with ", "__enter__", "__exit__"]},
                "generators": {"level": 3, "pattern": ["yield ", "yield from"]},
                "dataclasses": {"level": 2, "pattern": ["@dataclass", "from dataclasses"]},
                "pydantic": {"level": 3, "pattern": ["from pydantic", "BaseModel"]},
                "pytest": {"level": 2, "pattern": ["def test_", "@pytest", "assert "]},
            },
            "docker": {
                "multi_stage": {"level": 3, "pattern": ["FROM.*AS", "COPY --from="]},
                "healthcheck": {"level": 2, "pattern": ["HEALTHCHECK"]},
                "volumes": {"level": 1, "pattern": ["VOLUME", "mounts"]},
                "env": {"level": 1, "pattern": ["ENV ", "ARG "]},
            },
            "devops": {
                "github_actions": {"level": 2, "pattern": ["on:", "jobs:", "steps:"]},
                "kubernetes": {"level": 3, "pattern": ["apiVersion:", "kind:", "spec:"]},
                "terraform": {"level": 3, "pattern": ["resource ", "provider "]},
            }
        }
        
        code_file = Path(code_path)
        
        if not code_file.exists():
            return [{"error": f"Файл не найден: {code_path}"}]
        
        try:
            if code_file.is_file():
                files_to_check = [code_file]
            else:
                files_to_check = list(code_file.glob("**/*.py")) + \
                                list(code_file.glob("**/Dockerfile")) + \
                                list(code_file.glob("**/*.yml"))
            
            for file in files_to_check[:10]:  # Ограничим 10 файлами
                try:
                    content = file.read_text(encoding='utf-8')
                    file_type = detect_file_type(file)
                    
                    if file_type in marker_patterns:
                        for marker_name, marker_info in marker_patterns[file_type].items():
                            if any(pattern in content for pattern in marker_info["pattern"]):
                                detected.append({
                                    "domain": file_type,
                                    "marker": marker_name,
                                    "level": marker_info["level"],
                                    "file": str(file.relative_to(project_root)) if str(file).startswith(str(project_root)) else str(file)
                                })
                except Exception:
                    continue
            
            return detected
            
        except Exception as e:
            return [{"error": f"Ошибка при анализе: {str(e)}"}]
    
    def detect_file_type(file: Path) -> Optional[str]:
        """Определение типа файла"""
        if file.suffix == ".py":
            return "python"
        elif file.name == "Dockerfile" or file.suffix == ".dockerfile":
            return "docker"
        elif file.suffix in [".yml", ".yaml"] and "docker-compose" in file.name.lower():
            return "docker"
        elif file.suffix in [".yml", ".yaml"] and any(x in file.name.lower() for x in ["workflow", "github", "action"]):
            return "devops"
        elif file.suffix == ".tf":
            return "devops"
        return None
