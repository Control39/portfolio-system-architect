"""
Модуль сканирования проекта для Cognitive Agent
Часть модульного рефакторинга autonomous_agent.py
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

import aiofiles
from tenacity import retry, stop_after_attempt, wait_exponential

from agents.cognitive_agent.src.logging_config import logger


class ProjectScanner:
    """
    Расширенный сканер проекта для анализа структуры кода
    """

    def __init__(self, scan_depth: int = 3):
        self.scan_depth = scan_depth
        self.python_extensions = [".py"]
        self.config_extensions = [".yml", ".yaml", ".json", ".toml", ".ini", ".env"]
        self.docs_extensions = [".md", ".rst", ".txt"]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def scan_project(
        self, project_path: str, scan_mode: str = "auto", target_paths: list[str] | None = None
    ) -> dict:
        """
        Сканировать проект с поддержкой разных режимов

        Args:
            project_path: Путь к проекту для сканирования
            scan_mode: Режим сканирования ("auto", "git_diff", "full", "paths")
            target_paths: Конкретные пути для сканирования (в режиме "paths")

        Returns:
            Результат сканирования
        """
        start_time = time.time()
        logger.info("Starting project scan", path=project_path, mode=scan_mode)

        try:
            if scan_mode == "git_diff":
                files_to_scan = await self._get_changed_files(project_path)
            elif scan_mode == "paths" and target_paths:
                files_to_scan = target_paths
            elif scan_mode == "full":
                files_to_scan = await self._get_all_files(project_path)
            else:  # auto mode
                files_to_scan = await self._get_changed_files(project_path)
                if not files_to_scan:
                    files_to_scan = await self._get_all_files(project_path)

            scan_results = await self._scan_files_concurrently(files_to_scan)

            # Сохраняем результаты сканирования
            results_path = Path(project_path) / ".agent_data" / "scan_results"
            results_path.mkdir(parents=True, exist_ok=True)

            timestamp = int(time.time())
            result_file = results_path / f"scan_result_{timestamp}.json"

            async with aiofiles.open(result_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(scan_results, indent=2, ensure_ascii=False))

            scan_duration = time.time() - start_time
            logger.info("Project scan completed", duration=scan_duration, files_scanned=len(files_to_scan))

            return {
                "scan_results": scan_results,
                "scan_duration": scan_duration,
                "files_scanned": len(files_to_scan),
                "timestamp": timestamp,
                "result_file": str(result_file),
            }

        except Exception as e:
            logger.error("Project scan failed", error=str(e))
            raise

    async def _get_changed_files(self, project_path: str) -> list[str]:
        """Получить список измененных файлов через git diff"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                # Фильтруем файлы по типу
                filtered_files = [
                    f
                    for f in changed_files
                    if any(
                        f.endswith(ext)
                        for ext in self.python_extensions + self.config_extensions + self.docs_extensions
                    )
                ]
                return [str(Path(project_path) / f) for f in filtered_files]
            else:
                logger.warning("Git diff failed, falling back to full scan", error=result.stderr)
                return []
        except subprocess.TimeoutExpired:
            logger.warning("Git diff timed out, falling back to full scan")
            return []
        except Exception as e:
            logger.warning("Error getting changed files, falling back to full scan", error=str(e))
            return []

    async def _get_all_files(self, project_path: str) -> list[str]:
        """Получить все файлы в проекте до указанной глубины"""
        files = []
        project_root = Path(project_path)

        for root, dirs, filenames in os.walk(project_root):
            # Ограничиваем глубину сканирования
            root_path = Path(root)
            relative_path = root_path.relative_to(project_root)
            depth = len(relative_path.parts) if relative_path.parts != (".",) else 0

            if depth >= self.scan_depth:
                dirs.clear()  # Очищаем dirs, чтобы не заходить глубже
                continue

            for filename in filenames:
                filepath = root_path / filename
                if any(
                    filename.endswith(ext)
                    for ext in self.python_extensions + self.config_extensions + self.docs_extensions
                ):
                    files.append(str(filepath))

        return files

    async def _scan_files_concurrently(self, file_paths: list[str]) -> dict:
        """Асинхронно просканировать файлы параллельно"""
        semaphore = asyncio.Semaphore(10)  # Ограничение на 10 одновременных операций

        async def scan_single_file(filepath: str):
            async with semaphore:
                try:
                    return await self._analyze_file(filepath)
                except Exception as e:
                    logger.error("Error analyzing file", filepath=filepath, error=str(e))
                    return {filepath: {"error": str(e)}}

        tasks = [scan_single_file(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Объединяем результаты
        final_results = {}
        for result in results:
            if isinstance(result, dict):
                final_results.update(result)

        return final_results

    async def _analyze_file(self, filepath: str) -> dict[str, any]:
        """
        Анализировать отдельный файл
        """
        try:
            async with aiofiles.open(filepath, encoding="utf-8") as f:
                content = await f.read()

            file_info = {
                "path": filepath,
                "size": len(content),
                "lines": len(content.splitlines()),
                "extension": Path(filepath).suffix,
                "last_modified": os.path.getmtime(filepath),
            }

            if filepath.endswith(".py"):
                # Дополнительный анализ Python файлов
                file_info.update(await self._analyze_python_file(content, filepath))

            return {filepath: file_info}
        except Exception as e:
            logger.error("Error analyzing file", filepath=filepath, error=str(e))
            return {filepath: {"error": str(e)}}

    async def _analyze_python_file(self, content: str, filepath: str) -> dict:
        """Анализировать Python файл с использованием AST"""
        try:
            import ast

            tree = ast.parse(content)

            analysis = {
                "classes": [],
                "functions": [],
                "imports": [],
                "docstrings": [],
                "has_async": False,
                "has_decorators": False,
                "complexity_score": 0,  # Простая метрика сложности
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                            "line_start": node.lineno,
                            "docstring": ast.get_docstring(node),
                        }
                    )
                    analysis["complexity_score"] += 1
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(
                        {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args if arg.arg != "self"],
                            "line_start": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "docstring": ast.get_docstring(node),
                        }
                    )
                    analysis["complexity_score"] += 1
                    if isinstance(node, ast.AsyncFunctionDef):
                        analysis["has_async"] = True
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis["imports"].append(ast.unparse(node))
                elif isinstance(node, ast.AsyncFunctionDef):
                    analysis["has_async"] = True
                elif (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id in ["property", "staticmethod", "classmethod"]
                ):
                    analysis["has_decorators"] = True

            return analysis
        except SyntaxError:
            logger.warning("Syntax error in Python file", filepath=filepath)
            return {"syntax_error": True}
        except Exception as e:
            logger.error("Error parsing Python file", filepath=filepath, error=str(e))
            return {"parse_error": str(e)}

    async def get_project_summary(self, project_path: str) -> dict:
        """
        Получить краткое описание проекта
        """
        structure = await self._get_project_structure_summary(project_path)
        tech_stack = await self._infer_tech_stack(project_path)

        return {
            "project_path": project_path,
            "structure_summary": structure,
            "technology_stack": tech_stack,
            "estimated_complexity": self._estimate_complexity(structure, tech_stack),
        }

    async def _get_project_structure_summary(self, project_path: str) -> dict:
        """Получить краткое описание структуры проекта"""
        structure = {
            "total_files": 0,
            "total_lines": 0,
            "python_files": 0,
            "config_files": 0,
            "doc_files": 0,
            "directories": set(),
            "top_level_dirs": [],
        }

        for root, dirs, files in os.walk(project_path):
            # Ограничиваем глубину
            root_path = Path(root)
            relative_path = root_path.relative_to(Path(project_path))
            depth = len(relative_path.parts) if relative_path.parts != (".",) else 0

            if depth >= 2:  # Только верхние 2 уровня
                dirs.clear()
                continue

            structure["directories"].update([d for d in dirs])

            if depth == 1:  # Только директории первого уровня
                structure["top_level_dirs"].extend([str(Path(d)) for d in dirs])

            for file in files:
                filepath = root_path / file
                structure["total_files"] += 1

                try:
                    if file.endswith(".py"):
                        structure["python_files"] += 1
                        with open(filepath, encoding="utf-8") as f:
                            structure["total_lines"] += len(f.readlines())
                    elif any(file.endswith(ext) for ext in self.config_extensions):
                        structure["config_files"] += 1
                    elif any(file.endswith(ext) for ext in self.docs_extensions):
                        structure["doc_files"] += 1
                except Exception:
                    continue  # Пропускаем файлы, которые не удается прочитать

        structure["directories"] = list(structure["directories"])
        structure["top_level_dirs"] = list(set(structure["top_level_dirs"]))

        return structure

    async def _infer_tech_stack(self, project_path: str) -> dict:
        """Определить стек технологий проекта"""
        tech_stack = {"python_version": None, "frameworks": [], "libraries": [], "tools": []}

        # Поиск файлов конфигурации
        config_files = {
            "requirements.txt": "pip",
            "pyproject.toml": "poetry/pip",
            "setup.py": "setuptools",
            "Pipfile": "pipenv",
            "Dockerfile": "docker",
            "docker-compose.yml": "docker-compose",
            ".gitignore": "git",
            "README.md": "documentation",
        }

        for root, _dirs, files in os.walk(project_path):
            for file in files:
                if file in config_files:
                    tech_stack["tools"].append(config_files[file])

                if file == "requirements.txt":
                    try:
                        with open(Path(root) / file, encoding="utf-8") as f:
                            content = f.read()
                            # Извлечение библиотек из requirements.txt
                            for line in content.splitlines():
                                line = line.strip()
                                if line and not line.startswith("#") and not line.startswith("-"):
                                    lib = line.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0]
                                    if lib not in tech_stack["libraries"]:
                                        tech_stack["libraries"].append(lib)
                    except Exception:
                        pass

        # Поиск известных фреймворков в коде
        known_frameworks = [
            ("fastapi", "FastAPI"),
            ("flask", "Flask"),
            ("django", "Django"),
            ("uvicorn", "ASGI Server"),
            ("celery", "Task Queue"),
            ("sqlalchemy", "ORM"),
            ("alembic", "Migration Tool"),
            ("pytest", "Testing Framework"),
            ("unittest", "Testing Framework"),
            ("requests", "HTTP Library"),
            ("aiohttp", "Async HTTP"),
            ("asyncio", "Async Library"),
        ]

        # Поиск в файлах
        for root, _dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(Path(root) / file, encoding="utf-8") as f:
                            content = f.read().lower()
                            for import_name, framework_name in known_frameworks:
                                if f"import {import_name}" in content or f"from {import_name}" in content:
                                    if framework_name not in tech_stack["frameworks"]:
                                        tech_stack["frameworks"].append(framework_name)
                    except Exception:
                        continue

        return tech_stack

    def _estimate_complexity(self, structure: dict, tech_stack: dict) -> str:
        """Оценить сложность проекта"""
        score = 0
        score += structure["python_files"] * 0.5
        score += len(tech_stack["frameworks"]) * 2
        score += structure["total_lines"] / 1000

        if score < 10:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 100:
            return "high"
        else:
            return "very high"
