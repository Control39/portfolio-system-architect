"""
Модуль для интеграции агента с инструментами статического анализа кода
"""

import contextlib
import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AnalysisTool(Enum):
    """Перечисление инструментов статического анализа"""

    MYPY = "mypy"
    RUFF = "ruff"
    BANDIT = "bandit"
    PYRIGHT = "pyright"
    PYTEST_COVERAGE = "pytest_coverage"


@dataclass
class AnalysisResult:
    """Результат анализа кода"""

    tool: AnalysisTool
    success: bool
    output: str
    issues: list[dict[str, Any]]
    summary: dict[str, Any]


class AICache:
    """Класс для кеширования AI-ответов"""

    def __init__(self, cache_dir: str = ".ai_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get(self, issue: dict) -> str | None:
        """Получить закешированный ответ"""
        key = self._make_key(issue)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    return json.load(f).get("fix")
            except (json.JSONDecodeError, KeyError):
                return None
        return None

    def set(self, issue: dict, fix: str):
        """Сохранить ответ в кеш"""
        key = self._make_key(issue)
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({"fix": fix, "issue": issue}, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _make_key(self, issue: dict) -> str:
        """Создать ключ для кеша"""
        # Убираем специфичные детали (номера строк, имена файлов)
        issue_copy = {k: v for k, v in issue.items() if k != "line"}
        return hashlib.md5(json.dumps(issue_copy, sort_keys=True).encode()).hexdigest()


class SmartFixer:
    """Класс для безопасного применения исправлений с бэкапами"""

    def __init__(self, backup_dir: str = ".code_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def apply_fix_with_backup(self, file_path: str, issue: dict, fix_result: dict) -> bool:
        """Применить исправление с созданием бэкапа"""
        file = Path(file_path)

        if not file.exists():
            logger.error(f"File not found: {file_path}")
            return False

        # 1. Создаем бэкап
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file.name}.{timestamp}.bak"
        try:
            backup_path.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

        # 2. Применяем исправление
        try:
            content = file.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Применяем исправление к строке
            line_number = issue.get("line", 0)
            if isinstance(line_number, str):
                try:
                    line_number = int(line_number)
                except ValueError:
                    line_number = 0

            if line_number > 0 and line_number <= len(lines):
                # Заменяем строку (простая замена)
                lines[line_number - 1] = fix_result["fix"]
            else:
                # Если строка неизвестна, добавляем исправление в конец файла
                lines.append(f"# Fix: {fix_result['fix']}")

            # Сохраняем файл
            file.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"✅ Fix applied to {file_path}, backup saved to {backup_path}")
            return True
        except Exception as e:
            # Восстанавливаем из бэкапа в случае ошибки
            try:
                original_content = backup_path.read_text(encoding="utf-8")
                file.write_text(original_content, encoding="utf-8")
                logger.warning(f"Fix failed, restored from backup: {e}")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
            return False

    def rollback_fix(self, file_path: str, backup_timestamp: str = None) -> bool:
        """Откатить исправление"""
        file = Path(file_path)

        # Находим последний бэкап
        backups = list(self.backup_dir.glob(f"{file.name}.*.bak"))
        if not backups:
            logger.error(f"No backups found for {file_path}")
            return False

        # Используем последний бэкап или указанный по времени
        if backup_timestamp:
            target_backup = self.backup_dir / f"{file.name}.{backup_timestamp}.bak"
            if not target_backup.exists():
                logger.error(f"Specific backup not found: {target_backup}")
                return False
        else:
            target_backup = sorted(backups)[-1]  # Последний бэкап

        try:
            file.write_text(target_backup.read_text(encoding="utf-8"), encoding="utf-8")
            logger.info(f"Rollback successful from {target_backup}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


class CodeAnalyzer:
    """Класс для интеграции с инструментами статического анализа"""

    def __init__(self, project_path: str, thought_manager=None):
        self.project_path = Path(project_path)
        self.tools_available = self._check_tool_availability()
        self.ai_available = self._check_ai_availability()
        self.ai_cache = AICache()
        self.smart_fixer = SmartFixer()
        self.use_ai = os.getenv("USE_AI_FOR_FIXES", "true").lower() == "true"
        self.file_cache = {}  # Кеш результатов анализа
        self.thought_manager = thought_manager  # Интеграция с мыслительным менеджером
        self.file_hashes = {}  # Хеши файлов для отслеживания изменений

    def _check_ai_availability(self) -> dict[str, bool]:
        """Проверить доступность AI-сервисов"""
        status = {"gigachat": False, "ollama": False, "reason": []}

        # Проверяем GigaChat
        try:
            import gigachat_bridge

            if os.getenv("GIGACHAT_API_KEY"):
                status["gigachat"] = True
            else:
                status["reason"].append("GIGACHAT_API_KEY not set")
        except ImportError:
            status["reason"].append("gigachat_bridge not installed")

        # Проверяем Ollama
        try:
            import ollama_agent

            # Проверяем, запущен ли сервер
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                status["ollama"] = True
            else:
                status["reason"].append("Ollama server not responding")
        except ImportError:
            status["reason"].append("ollama_agent not installed")
        except requests.exceptions.ConnectionError:
            status["reason"].append("Ollama not running")
        except Exception as e:
            status["reason"].append(f"Ollama connection error: {str(e)}")

        return status

    def _check_tool_availability(self) -> dict[AnalysisTool, bool]:
        """Проверить доступность инструментов анализа"""
        import shutil

        tools = {}
        for tool in AnalysisTool:
            try:
                # Для Bandit, Pyright, MyPy и Ruff сначала проверяем через shutil.which
                tool_cmd = tool.value

                # Для Pytest и Coverage проверяем через Python модули
                if tool == AnalysisTool.PYTEST_COVERAGE:
                    try:
                        # Проверяем pytest
                        result = subprocess.run(
                            [sys.executable, "-m", "pytest", "--version"],
                            capture_output=True,
                            text=True,
                            cwd=self.project_path,
                            shell=False,
                        )
                        pytest_available = result.returncode == 0

                        # Проверяем coverage
                        result = subprocess.run(
                            [sys.executable, "-m", "coverage", "--version"],
                            capture_output=True,
                            text=True,
                            cwd=self.project_path,
                            shell=False,
                        )
                        coverage_available = result.returncode == 0

                        tools[tool] = pytest_available and coverage_available
                    except Exception:
                        tools[tool] = False
                else:
                    # Для остальных инструментов проверяем наличие через shutil.which
                    tool_path = shutil.which(tool_cmd)
                    if tool_path:
                        tools[tool] = True
                    else:
                        # Если инструмент не найден в PATH, пробуем использовать python -m для модулей
                        if tool in [AnalysisTool.MYPY, AnalysisTool.RUFF, AnalysisTool.BANDIT]:
                            try:
                                result = subprocess.run(
                                    [sys.executable, "-m", tool.value, "--version"],
                                    capture_output=True,
                                    text=True,
                                    cwd=self.project_path,
                                    shell=False,
                                )
                                tools[tool] = result.returncode == 0
                            except Exception:
                                tools[tool] = False
                        elif tool == AnalysisTool.PYRIGHT:
                            try:
                                result = subprocess.run(
                                    ["npx", "pyright", "--version"],
                                    capture_output=True,
                                    text=True,
                                    cwd=self.project_path,
                                    shell=False,
                                )
                                tools[tool] = result.returncode == 0
                            except Exception:
                                tools[tool] = False
                        else:
                            tools[tool] = False
            except Exception:
                tools[tool] = False

        return tools

    def run_mypy_analysis(self) -> AnalysisResult:
        """Запустить анализ с помощью MyPy"""
        if not self.tools_available[AnalysisTool.MYPY]:
            return AnalysisResult(
                tool=AnalysisTool.MYPY,
                success=False,
                output="MyPy не установлен или недоступен",
                issues=[],
                summary={"error": "MyPy not available"},
            )

        try:
            # Запускаем mypy с выводом в формате JSON
            cmd = ["mypy", "--no-error-summary", "--show-error-codes", "."]
            result = self._safe_run(cmd)

            success = result.returncode == 0
            output = result.stdout + result.stderr

            # Парсим результаты mypy
            issues = []
            for line in output.split("\n"):
                if ":" in line and ("error:" in line or "note:" in line):
                    parts = line.split(":", 3)
                    if len(parts) >= 4:
                        issues.append(
                            {
                                "file": parts[0].strip(),
                                "line": parts[1].strip(),
                                "column": parts[2].strip(),
                                "message": parts[3].strip(),
                                "type": "error" if "error:" in line else "warning",
                            }
                        )

            summary = {
                "total_errors": len([issue for issue in issues if issue["type"] == "error"]),
                "total_warnings": len([issue for issue in issues if issue["type"] == "warning"]),
                "success": success,
            }

            return AnalysisResult(
                tool=AnalysisTool.MYPY, success=success, output=output, issues=issues, summary=summary
            )
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.MYPY,
                success=False,
                output=f"Ошибка при запуске MyPy: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

    def run_ruff_analysis(self) -> AnalysisResult:
        """Запустить анализ с помощью Ruff"""
        if not self.tools_available[AnalysisTool.RUFF]:
            return AnalysisResult(
                tool=AnalysisTool.RUFF,
                success=False,
                output="Ruff не установлен или недоступен",
                issues=[],
                summary={"error": "Ruff not available"},
            )

        try:
            # Сначала проверим, есть ли конфигурация ruff
            config_args = ["ruff", "check", ".", "--output-format=json"]
            result = self._safe_run(config_args)

            success = result.returncode in [0, 1]  # 1 означает найденные ошибки, но не сбой выполнения
            output = result.stdout + result.stderr

            # Парсим результаты ruff (в формате JSON)
            issues = []
            try:
                # Ruff может выводить результаты в JSON строку за строкой
                for line in output.strip().split("\n"):
                    if line.strip():
                        try:
                            issue = json.loads(line)
                            issues.append(issue)
                        except json.JSONDecodeError:
                            # Если не JSON, попробуем другой формат
                            if ":" in line and ("Error" in line or "Warning" in line):
                                parts = line.split(":", 3)
                                if len(parts) >= 4:
                                    issues.append(
                                        {
                                            "filename": parts[0].strip(),
                                            "line": parts[1].strip(),
                                            "col": parts[2].strip(),
                                            "message": parts[3].strip(),
                                        }
                                    )
            except:
                pass

            summary = {"total_issues": len(issues), "success": success, "raw_return_code": result.returncode}

            return AnalysisResult(
                tool=AnalysisTool.RUFF, success=success, output=output, issues=issues, summary=summary
            )
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.RUFF,
                success=False,
                output=f"Ошибка при запуске Ruff: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

    def run_bandit_analysis(self) -> AnalysisResult:
        """Запустить анализ безопасности с помощью Bandit"""
        if not self.tools_available[AnalysisTool.BANDIT]:
            return AnalysisResult(
                tool=AnalysisTool.BANDIT,
                success=False,
                output="Bandit не установлен или недоступен",
                issues=[],
                summary={"error": "Bandit not available"},
            )

        try:
            # Запускаем bandit с выводом в формате JSON
            cmd = [
                "bandit",
                "-r",  # Рекурсивный анализ
                ".",  # Текущая директория
                "-f",
                "json",  # Формат вывода
            ]
            result = self._safe_run(cmd)

            success = result.returncode in [0, 1]  # 0 - нет проблем, 1 - найдены проблемы
            output = result.stdout

            issues = []
            summary = {"success": success}

            try:
                if output.strip():
                    data = json.loads(output)
                    issues = data.get("results", [])
                    summary.update(
                        {
                            "total_issues": len(issues),
                            "severity_stats": {
                                "LOW": len([r for r in issues if r["issue_severity"] == "LOW"]),
                                "MEDIUM": len([r for r in issues if r["issue_severity"] == "MEDIUM"]),
                                "HIGH": len([r for r in issues if r["issue_severity"] == "HIGH"]),
                            },
                        }
                    )
            except json.JSONDecodeError:
                # Если не удается расарсить JSON, возвращаем ошибку
                return AnalysisResult(
                    tool=AnalysisTool.BANDIT,
                    success=False,
                    output=f"Ошибка при парсинге результатов Bandit: {output}",
                    issues=[],
                    summary={"error": "Failed to parse Bandit output as JSON"},
                )

            return AnalysisResult(
                tool=AnalysisTool.BANDIT, success=success, output=output, issues=issues, summary=summary
            )
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.BANDIT,
                success=False,
                output=f"Ошибка при запуске Bandit: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

    def run_pyright_analysis(self) -> AnalysisResult:
        """Запустить анализ с помощью Pyright"""
        if not self.tools_available[AnalysisTool.PYRIGHT]:
            return AnalysisResult(
                tool=AnalysisTool.PYRIGHT,
                success=False,
                output="Pyright не установлен или недоступен",
                issues=[],
                summary={"error": "Pyright not available"},
            )

        try:
            # Запускаем pyright с выводом в формате JSON
            cmd = ["pyright", "--outputjson"]
            result = self._safe_run(cmd)

            success = result.returncode == 0
            output = result.stdout

            issues = []
            summary = {"success": success}

            try:
                if output.strip():
                    data = json.loads(output)
                    issues = data.get("diagnostics", [])
                    summary.update(
                        {
                            "total_issues": len(issues),
                            "files_analyzed": data.get("filesAnalyzed", 0),
                            "summary": data.get("summary", {}),
                        }
                    )
            except json.JSONDecodeError:
                # Если не удается распарсить JSON, возвращаем ошибку
                return AnalysisResult(
                    tool=AnalysisTool.PYRIGHT,
                    success=False,
                    output=f"Ошибка при парсинге результатов Pyright: {output}",
                    issues=[],
                    summary={"error": "Failed to parse Pyright output as JSON"},
                )

            return AnalysisResult(
                tool=AnalysisTool.PYRIGHT, success=success, output=output, issues=issues, summary=summary
            )
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.PYRIGHT,
                success=False,
                output=f"Ошибка при запуске Pyright: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

    def run_coverage_analysis(self) -> AnalysisResult:
        """Запустить анализ покрытия тестами"""
        if not self.tools_available[AnalysisTool.PYTEST_COVERAGE]:
            return AnalysisResult(
                tool=AnalysisTool.PYTEST_COVERAGE,
                success=False,
                output="Pytest или Coverage не установлены или недоступны",
                issues=[],
                summary={"error": "Coverage tools not available"},
            )

        try:
            # Создаем временный файл для хранения результатов
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tf:
                    temp_file = tf.name

                # Сначала запускаем тесты с coverage
                coverage_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "run", "-m", "pytest"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    shell=False,
                )

                # Затем генерируем отчет
                report_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    shell=False,
                )

                # Сохраняем вывод для последующего использования
                output = coverage_result.stdout + coverage_result.stderr

                # Теперь генерируем JSON-отчет для последующего анализа
                json_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    shell=False,
                )

                # Используем JSON-результат для получения данных о покрытии
                summary = {"success": True, "coverage_output": report_result.stdout}
                if json_result.returncode == 0:
                    try:
                        coverage_data = json.loads(json_result.stdout)
                        summary.update(
                            {
                                "total_coverage": coverage_data.get("totals", {}).get("percent_covered_display", 0),
                                "files_count": len(coverage_data.get("files", {})),
                                "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                            }
                        )
                    except json.JSONDecodeError:
                        pass  # Используем значения по умолчанию

                success = coverage_result.returncode == 0

                issues = []

                # Пытаемся получить данные о покрытии
                try:
                    # Попробуем получить JSON отчет о покрытии
                    json_report_result = subprocess.run(
                        ["coverage", "json"], capture_output=True, text=True, cwd=self.project_path
                    )

                    if json_report_result.returncode == 0:
                        coverage_data = json.loads(json_report_result.stdout)
                        summary.update(
                            {
                                "total_coverage": coverage_data.get("totals", {}).get("percent_covered_display", 0),
                                "files_count": len(coverage_data.get("files", {})),
                                "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                            }
                        )
                except (json.JSONDecodeError, subprocess.CalledProcessError):
                    # Если не удалось получить JSON, используем текстовый отчет
                    for line in report_result.stdout.split("\n"):
                        if "TOTAL" in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                with contextlib.suppress(ValueError):
                                    summary["total_coverage"] = float(parts[-1].replace("%", ""))
                            break

                return AnalysisResult(
                    tool=AnalysisTool.PYTEST_COVERAGE, success=success, output=output, issues=issues, summary=summary
                )
            finally:
                # Убедимся, что мы не оставляем временные файлы
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.PYTEST_COVERAGE,
                success=False,
                output=f"Ошибка при запуске анализа покрытия: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

    def _run_analysis_with_timeout(self, cmd: list, timeout: int = 300) -> subprocess.CompletedProcess:
        """Запуск анализа с таймаутом"""
        try:
            return subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_path, shell=False, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"Command {cmd} timed out after {timeout} seconds")
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Command timed out")

    def _get_full_path(self, cmd: list) -> list:
        """Получить полный путь к исполняемому файлу"""
        import shutil

        if not cmd:
            return cmd

        tool_name = cmd[0]
        full_path = shutil.which(tool_name)

        if full_path:
            cmd[0] = full_path
        elif tool_name in ["mypy", "ruff", "bandit", "coverage", "pytest"]:
            # Используем python -m для модулей
            cmd = [sys.executable, "-m"] + cmd

        return cmd

    def _safe_run(self, cmd: list, use_cwd: bool = True) -> subprocess.CompletedProcess:
        """Безопасный запуск subprocess"""
        try:
            # Получаем полный путь к исполняемому файлу
            cmd = self._get_full_path(cmd)

            # Запускаем команду с таймаутом
            return self._run_analysis_with_timeout(cmd)
        except Exception as e:
            logger.error(f"Error in _safe_run: {e}")
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr=str(e))

    def run_full_analysis(self) -> dict[AnalysisTool, AnalysisResult]:
        """Запустить полный анализ всеми доступными инструментами"""
        results = {}

        # Запускаем каждый инструмент по очереди
        if self.tools_available[AnalysisTool.MYPY]:
            results[AnalysisTool.MYPY] = self.run_mypy_analysis()

        if self.tools_available[AnalysisTool.RUFF]:
            results[AnalysisTool.RUFF] = self.run_ruff_analysis()

        if self.tools_available[AnalysisTool.BANDIT]:
            results[AnalysisTool.BANDIT] = self.run_bandit_analysis()

        if self.tools_available[AnalysisTool.PYRIGHT]:
            results[AnalysisTool.PYRIGHT] = self.run_pyright_analysis()

        if self.tools_available[AnalysisTool.PYTEST_COVERAGE]:
            results[AnalysisTool.PYTEST_COVERAGE] = self.run_coverage_analysis()

        return results

    def generate_quality_report(self) -> dict[str, Any]:
        """Сгенерировать общий отчет о качестве кода"""
        analysis_results = self.run_full_analysis()

        report = {
            "project_path": str(self.project_path),
            "timestamp": str(datetime.now()),
            "tools_run": len(analysis_results),
            "tools_available": {tool.value: available for tool, available in self.tools_available.items()},
            "results": {},
            "summary": {
                "total_errors": 0,
                "total_warnings": 0,
                "total_security_issues": 0,
                "total_style_issues": 0,
                "coverage_percentage": 0,
                "all_good": True,
            },
        }

        for tool, result in analysis_results.items():
            report["results"][tool.value] = {
                "success": result.success,
                "summary": result.summary,
                "issue_count": len(result.issues),
            }

            # Обновляем итоговую статистику
            if tool == AnalysisTool.MYPY:
                report["summary"]["total_errors"] += result.summary.get("total_errors", 0)
                report["summary"]["total_warnings"] += result.summary.get("total_warnings", 0)
            elif tool == AnalysisTool.RUFF:
                report["summary"]["total_style_issues"] += result.summary.get("total_issues", 0)
            elif tool == AnalysisTool.BANDIT:
                report["summary"]["total_security_issues"] += result.summary.get("total_issues", 0)
            elif tool == AnalysisTool.PYTEST_COVERAGE:
                report["summary"]["coverage_percentage"] = result.summary.get("total_coverage", 0)

        # Проверяем, есть ли какие-либо проблемы
        total_problems = (
            report["summary"]["total_errors"]
            + report["summary"]["total_warnings"]
            + report["summary"]["total_style_issues"]
            + report["summary"]["total_security_issues"]
        )
        report["summary"]["all_good"] = total_problems == 0

        return report

    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ РЕКОМЕНДАЦИЙ И AI ====================

    def run_analysis_with_recommendations(self) -> dict[str, Any]:
        """Полный анализ с генерацией рекомендаций (улучшенная версия)"""
        try:
            analysis_results = self.run_full_analysis()

            # Формируем структуру с recommendations и fixes
            all_issues = []
            for tool, result in analysis_results.items():
                for issue in result.issues:
                    # Нормализуем структуру issue для совместимости с AI
                    normalized_issue = self._normalize_issue(issue, tool.value)
                    if normalized_issue:
                        all_issues.append(normalized_issue)

            # Генерируем улучшенные рекомендации
            recommendations = []
            fixes = []

            for issue in all_issues:
                fix_result = self.suggest_fix_enhanced(issue)
                if fix_result["success"]:
                    fixes.append({"issue": issue, "fix": fix_result["fix"], "source": fix_result["source"]})

                    if fix_result["source"] != "rule-based (fallback)":
                        recommendations.append(f"AI suggests: {fix_result['fix']}")

            # Если у нас есть менеджер мыслей, добавляем информацию о проблемах
            if self.thought_manager:
                if fixes:
                    self.thought_manager.capture_thought(
                        f"Найдено {len(fixes)} потенциальных проблем в коде",
                        context=f"Проблемы: {[f['issue']['message'][:50] for f in fixes]}",
                        priority="medium",
                    )

                critical = self.get_critical_issues()
                if critical:
                    self.thought_manager.capture_thought(
                        f"Обнаружено {len(critical)} критических проблем безопасности",
                        context=f"Критические проблемы: {[c['message'][:50] for c in critical]}",
                        priority="high",
                    )

            return {
                "issues": all_issues,
                "recommendations": recommendations,
                "fixes": fixes,
                "summary": {
                    "total_issues": len(all_issues),
                    "tools_analyzed": len(analysis_results),
                    "critical_count": len([i for i in all_issues if i.get("severity") in ["HIGH", "MEDIUM"]]),
                    "ai_fixes_available": len(fixes),
                    "ai_status": self.ai_available,
                },
            }
        except Exception as e:
            logger.error("Error in run_analysis_with_recommendations: %s", e)
            return {"issues": [], "recommendations": [], "fixes": [], "summary": {"error": str(e), "total_issues": 0}}

    def get_critical_issues(self) -> list[dict[str, Any]]:
        """Получить критичные и серьёзные проблемы (HIGH/MEDIUM)"""
        try:
            analysis_results = self.run_full_analysis()
            critical = []

            for tool, result in analysis_results.items():
                for issue in result.issues:
                    severity = self._extract_severity(issue, tool.value)
                    if severity in ["HIGH", "MEDIUM"]:
                        normalized = self._normalize_issue(issue, tool.value)
                        if normalized:
                            normalized["severity"] = severity
                            critical.append(normalized)

            return critical
        except Exception as e:
            logger.error("Error in get_critical_issues: %s", e)
            return []

    def save_results(self, results: dict[str, Any], format: str = "json") -> str | None:
        """Сохранить результаты анализа в файл"""
        try:
            import json

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.project_path / f"code_analysis_results_{timestamp}.{format}"

            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                return str(output_path)
            elif format == "text":
                # Простой текстовый формат
                lines = []
                lines.append("Code Analysis Results")
                lines.append("=" * 50)
                lines.append(f"Project: {self.project_path}")
                lines.append(f"Timestamp: {timestamp}")
                lines.append(f"Total Issues: {results.get('summary', {}).get('total_issues', 0)}")
                lines.append("")

                for issue in results.get("issues", []):
                    lines.append(
                        f"[{issue.get('severity', 'UNKNOWN')}] {issue.get('tool', 'unknown')}: {issue.get('file', 'unknown')}:{issue.get('line', '?')} - {issue.get('message', '')}"
                    )

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                return str(output_path)
            else:
                logger.warning("Unsupported format: %s", format)
                return None
        except (ImportError, json.JSONDecodeError, OSError) as e:
            logger.error("Error saving results: %s", e)
            return None

    def suggest_fix_enhanced(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Предложить исправление с улучшенной логикой и статусом"""

        # 1. Проверяем кеш
        cached = self.ai_cache.get(issue)
        if cached:
            return {"success": True, "source": "cache", "fix": cached}

        # 2. Если AI отключен - сразу rule-based
        if not self.use_ai:
            return {"success": True, "source": "rule-based (AI disabled)", "fix": self._get_rule_based_fix(issue)}

        # 3. Пробуем AI
        fix = None
        source = None

        # GigaChat
        if self.ai_available.get("gigachat"):
            try:
                fix = self._call_gigachat(issue)
                source = "gigachat"
            except Exception as e:
                logger.warning(f"GigaChat failed: {e}")

        # Ollama (если GigaChat не сработал)
        if not fix and self.ai_available.get("ollama"):
            try:
                fix = self._call_ollama(issue)
                source = "ollama"
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")

        # 4. Fallback на правила
        if not fix:
            fix = self._get_rule_based_fix(issue)
            source = "rule-based (fallback)"

        # 5. Сохраняем в кеш если это был AI-ответ
        if source in ["gigachat", "ollama"]:
            self.ai_cache.set(issue, fix)

        return {"success": True, "source": source, "fix": fix, "ai_available": self.ai_available}

    def _get_rule_based_fix(self, issue: dict[str, Any]) -> str | None:
        """Базовые исправления без AI"""
        message = issue.get("message", "").lower()
        tool = issue.get("tool", "")

        # Правила для разных инструментов
        if "unused import" in message:
            return "Remove unused import"

        if "line too long" in message:
            return "Split long line into multiple lines"

        if tool == "ruff" and "E501" in message:
            return "Break line after 88 characters"

        if tool == "bandit" and "security" in message:
            return "Review security issue manually"

        if tool == "mypy" and "error" in message:
            return "Check type annotations and fix type mismatch"

        if tool == "ruff" and "F401" in message:
            return "Remove unused import"

        if tool == "ruff" and "F841" in message:
            return "Remove unused variable"

        # Общий совет
        return f"Issue: {message}. Consider reviewing this code pattern."

    def _call_gigachat(self, issue: dict[str, Any]) -> str | None:
        """Вызов GigaChat для получения исправления"""
        from gigachat_bridge import giga_request

        prompt = (
            f"Исправь проблему в коде:\n"
            f"Инструмент: {issue.get('tool', 'unknown')}\n"
            f"Файл: {issue.get('file', 'unknown')}\n"
            f"Строка: {issue.get('line', 'unknown')}\n"
            f"Сообщение: {issue.get('message', 'unknown')}\n"
            f"Серьезность: {issue.get('severity', 'unknown')}\n\n"
            f"Предложи конкретное исправление в формате JSON: {{'fix': 'код исправления', 'explanation': 'описание'}}"
        )

        response = giga_request(prompt)
        return response

    def _call_ollama(self, issue: dict[str, Any]) -> str | None:
        """Вызов Ollama для получения исправления"""
        from ollama_agent import OllamaAgent

        prompt = (
            f"Ты — эксперт по Python. Исправь проблему в коде:\n"
            f"Инструмент: {issue.get('tool', 'unknown')}\n"
            f"Файл: {issue.get('file', 'unknown')}\n"
            f"Строка: {issue.get('line', 'unknown')}\n"
            f"Сообщение: {issue.get('message', 'unknown')}\n\n"
            f"Предложи исправление в простом тексте."
        )

        agent = OllamaAgent()
        response = agent.ask(prompt)
        return response

    def suggest_fix(self, issue: dict[str, Any]) -> str | None:
        """Предложить исправление через AI (старый метод для обратной совместимости)"""
        result = self.suggest_fix_enhanced(issue)
        return result.get("fix")

    def apply_fix(self, issue: dict[str, Any], file_path: str) -> bool | None:
        """Применить исправление к файлу"""
        try:
            # Получаем исправление от AI
            fix_result = self.suggest_fix_enhanced(issue)
            if not fix_result["success"]:
                logger.warning("No fix suggestion available")
                return None

            # Применяем исправление с бэкапом
            success = self.smart_fixer.apply_fix_with_backup(file_path, issue, fix_result)
            return success
        except Exception as e:
            logger.error("Error in apply_fix: %s", e)
            return None

    def watch_changes(self) -> Any | None:
        """Мониторинг изменений файлов через watchdog"""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class CodeChangeHandler(FileSystemEventHandler):
                def __init__(self, analyzer):
                    self.analyzer = analyzer

                def on_modified(self, event):
                    if event.is_directory:
                        return
                    if event.src_path.endswith(".py"):
                        logger.info("Detected change in %s", event.src_path)
                        # Можно вызывать аналитику для измененного файла
                        # self.analyzer.analyze_changed_file(event.src_path)

            observer = Observer()
            observer.schedule(CodeChangeHandler(self), str(self.project_path), recursive=True)
            observer.start()

            logger.info("Started watching for code changes in %s", self.project_path)
            return observer
        except ImportError:
            logger.warning("watchdog not installed, skipping file monitoring")
            return None
        except Exception as e:
            logger.error("Error in watch_changes: %s", e)
            return None

    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ ИНКРЕМЕНТАЛЬНОГО АНАЛИЗА ====================

    def _get_file_hash(self, file_path: Path) -> str:
        """Получить хеш файла"""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _get_changed_files(self) -> list[Path]:
        """Найти измененные файлы"""
        changed = []
        for file in self.project_path.rglob("*.py"):
            if str(file) not in self.file_hashes:
                changed.append(file)
            else:
                current_hash = self._get_file_hash(file)
                if current_hash != self.file_hashes[str(file)]:
                    changed.append(file)
        return changed

    def analyze_changed_files(self) -> dict[str, AnalysisResult]:
        """Анализировать только измененные файлы"""
        changed_files = self._get_changed_files()
        results = {}

        for file_path in changed_files:
            # Обновляем хеш файла
            self.file_hashes[str(file_path)] = self._get_file_hash(file_path)

        # Запускаем анализ только для проекта в целом, так как инструменты анализируют всю структуру
        return self.run_full_analysis()

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _normalize_issue(self, issue: dict[str, Any], tool: str) -> dict[str, Any] | None:
        """Нормализовать issue для совместимости с AI"""
        try:
            normalized = {
                "tool": tool,
                "file": issue.get("file", issue.get("filename", "unknown")),
                "line": issue.get("line", issue.get("line_number", 0)),
                "message": issue.get("message", issue.get("text", "")),
                "severity": self._extract_severity(issue, tool),
            }

            # Удаляем None значения
            return {k: v for k, v in normalized.items() if v is not None}
        except Exception:
            return None

    def _extract_severity(self, issue: dict[str, Any], tool: str) -> str:
        """Извлечь severity из issue"""
        try:
            # Для Bandit
            if "issue_severity" in issue:
                return issue["issue_severity"]
            # Для Ruff
            if "severity" in issue:
                return issue["severity"]
            # Для Ruff (альтернативный ключ)
            if "type" in issue:
                if issue["type"] == "error":
                    return "HIGH"
                return "LOW"
            # Для Mypy
            if "type" in issue:
                if "error" in issue["type"].lower():
                    return "HIGH"
                return "LOW"
            # По умолчанию
            return "LOW"
        except Exception:
            return "LOW"
