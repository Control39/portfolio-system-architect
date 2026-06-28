"""Модуль для интеграции агента с инструментами статического анализа кода."""

import contextlib
import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class MetricsCollector:
    """Централизованный сборщик метрик производительности."""

    tool_times: Dict[str, float] = field(default_factory=dict)
    ai_calls: int = 0
    ai_total_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    def record_tool_time(self, tool_name: str, duration: float):
        self.tool_times[tool_name] = duration

    def record_ai_call(self, duration: float):
        self.ai_calls += 1
        self.ai_total_time += duration

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_cache_miss(self):
        self.cache_misses += 1

    def to_dict(self) -> Dict[str, Any]:
        hit_rate = (
            (self.cache_hits / (self.cache_hits + self.cache_misses) * 100)
            if (self.cache_hits + self.cache_misses) > 0
            else 0.0
        )
        avg_ai_time = (self.ai_total_time / self.ai_calls) if self.ai_calls > 0 else 0.0

        return {
            "tool_execution_times": self.tool_times,
            "ai_metrics": {
                "total_calls": self.ai_calls,
                "avg_response_time": round(avg_ai_time, 3),
                "cache_hit_rate_percent": round(hit_rate, 2),
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
            },
        }


class AnalysisTool(Enum):
    """Перечисление инструментов статического анализа."""

    MYPY = "mypy"
    RUFF = "ruff"
    BANDIT = "bandit"
    PYRIGHT = "pyright"
    PYTEST_COVERAGE = "pytest_coverage"


@dataclass
class AnalysisResult:
    """Результат анализа кода."""

    tool: AnalysisTool
    success: bool
    output: str
    issues: list[dict[str, Any]]
    summary: dict[str, Any]


class AICache:
    """Кэш AI-ответов."""

    def __init__(self, cache_dir: str = ".ai_cache", metrics_collector: MetricsCollector | None = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metrics_collector = metrics_collector

    def get(self, issue: dict) -> str | None:
        key = self._make_key(issue)
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    fix = json.load(f).get("fix")
                if self.metrics_collector:
                    self.metrics_collector.record_cache_hit()
                return fix
            except (json.JSONDecodeError, KeyError):
                if self.metrics_collector:
                    self.metrics_collector.record_cache_miss()
                return None

        if self.metrics_collector:
            self.metrics_collector.record_cache_miss()
        return None

    def set(self, issue: dict, fix: str) -> None:
        key = self._make_key(issue)
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"fix": fix, "issue": issue}, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _make_key(self, issue: dict) -> str:
        # Исключаем нестабильные поля (строки)
        issue_copy = {k: v for k, v in issue.items() if k != "line"}
        return hashlib.md5(json.dumps(issue_copy, sort_keys=True).encode()).hexdigest()


class SmartFixer:
    """Класс для применения исправлений с бэкапами (fallback-путь)."""

    def __init__(self, backup_dir: str = ".code_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def apply_fix_with_backup(self, file_path: str, issue: dict, fix_result: dict) -> bool:
        file = Path(file_path)
        if not file.exists():
            logger.error(f"File not found: {file_path}")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file.name}.{timestamp}.bak"
        try:
            backup_path.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

        try:
            content = file.read_text(encoding="utf-8")
            lines = content.split("\n")

            line_number = issue.get("line", 0)
            if isinstance(line_number, str):
                try:
                    line_number = int(line_number)
                except ValueError:
                    line_number = 0

            if line_number > 0 and line_number <= len(lines):
                lines[line_number - 1] = fix_result["fix"]
            else:
                lines.append(f"# Fix: {fix_result['fix']}")

            file.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"✅ Fix applied to {file_path}, backup saved to {backup_path}")
            return True
        except Exception as e:
            try:
                original_content = backup_path.read_text(encoding="utf-8")
                file.write_text(original_content, encoding="utf-8")
                logger.warning(f"Fix failed, restored from backup: {e}")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
            return False


class CodeAnalyzer:
    """Класс для интеграции с инструментами статического анализа.

    Примечание по безопасности:
    если установлен флаг AGENT_ACTIONS_READONLY=1, то любые действия,
    потенциально связанные с изменением файлов (auto-fix/apply_fix),
    должны быть запрещены.
    """

    # ==================== Парсеры вывода инструментов ====================

    def _parse_mypy(self, output: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        summary: dict[str, Any] = {"error_count": 0, "warning_count": 0, "note_count": 0}

        try:
            data = json.loads(output) if output else {}
        except json.JSONDecodeError:
            return issues, summary

        files = data.get("files", {}) if isinstance(data, dict) else {}
        if not isinstance(files, dict):
            return issues, summary

        for file_path, file_data in files.items():
            if not isinstance(file_data, dict):
                continue
            for msg in file_data.get("messages", []) or []:
                if not isinstance(msg, dict):
                    continue
                m_type = str(msg.get("type", "error"))
                severity = "error" if m_type.lower() == "error" else "warning"
                issues.append(
                    {
                        "tool": "mypy",
                        "file": file_path,
                        "line": msg.get("line"),
                        "message": msg.get("message", ""),
                        "severity": severity,
                    }
                )
                if severity == "error":
                    summary["error_count"] += 1
                else:
                    summary["warning_count"] += 1

        return issues, summary

    def _parse_ruff(self, output: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        summary: dict[str, Any] = {"error_count": 0, "warning_count": 0}

        try:
            data = json.loads(output) if output else []
        except json.JSONDecodeError:
            return issues, summary

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("errors") or data.get("violations") or []
        else:
            items = []

        if not isinstance(items, list):
            items = []

        for item in items:
            if not isinstance(item, dict):
                continue
            level = str(item.get("level", "warning"))
            severity = "warning" if level.lower() in ["warning", "warn"] else "error"
            loc = item.get("location") or {}
            line = loc.get("row") if isinstance(loc, dict) else item.get("line")

            message = item.get("message", "")
            code = item.get("code")
            if code and code not in str(message):
                message = f"{message} ({code})" if message else str(code)

            issues.append(
                {
                    "tool": "ruff",
                    "file": item.get("filename", item.get("file", "")),
                    "line": line,
                    "message": message,
                    "rule": code,
                    "severity": severity,
                }
            )

            if severity == "error":
                summary["error_count"] += 1
            else:
                summary["warning_count"] += 1

        return issues, summary

    def _parse_bandit(self, output: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        summary: dict[str, Any] = {"security_issue_count": 0, "high_severity_count": 0}

        try:
            data = json.loads(output) if output else {}
        except json.JSONDecodeError:
            return issues, summary

        results = data.get("results", []) if isinstance(data, dict) else []
        if not isinstance(results, list):
            results = []

        for r in results:
            if not isinstance(r, dict):
                continue
            sev = str(r.get("issue_severity", "low")).lower()
            issues.append(
                {
                    "tool": "bandit",
                    "file": r.get("filename", ""),
                    "line": r.get("line_number"),
                    "message": r.get("issue_text", ""),
                    "severity": sev,
                    "rule": r.get("test_id"),
                }
            )

        summary["security_issue_count"] = len(issues)
        summary["high_severity_count"] = sum(1 for i in issues if i.get("severity") == "high")
        return issues, summary

    def _parse_pyright(self, output: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        summary: dict[str, Any] = {"error_count": 0, "warning_count": 0}

        try:
            data = json.loads(output) if output else {}
        except json.JSONDecodeError:
            return issues, summary

        diags = data.get("generalDiagnostics", []) if isinstance(data, dict) else []
        if not isinstance(diags, list):
            diags = []

        for d in diags:
            if not isinstance(d, dict):
                continue
            severity_raw = str(d.get("severity", "error"))
            severity = "error" if severity_raw.lower() == "error" else "warning"

            line = None
            rng = d.get("range") or {}
            if isinstance(rng, dict):
                start = rng.get("start") or {}
                if isinstance(start, dict):
                    line = start.get("line")
            if line is None:
                line = d.get("line")

            issues.append(
                {
                    "tool": "pyright",
                    "file": d.get("file", ""),
                    "line": line,
                    "message": d.get("message", ""),
                    "severity": severity,
                }
            )

            if severity == "error":
                summary["error_count"] += 1
            else:
                summary["warning_count"] += 1

        return issues, summary

    def __init__(self, project_path: str, thought_manager=None):
        self.project_path = Path(project_path)
        self.tools_available = self._check_tool_availability()
        self.ai_available = self._check_ai_availability()

        self.metrics = self._create_metrics_collector()
        self.ai_cache = AICache(metrics_collector=self.metrics)
        self.smart_fixer = SmartFixer()

        self.use_ai = os.getenv("USE_AI_FOR_FIXES", "true").lower() == "true"

        self.thought_manager = thought_manager
        self.file_hashes: dict[str, str] = {}

    def _create_metrics_collector(self) -> MetricsCollector:
        return MetricsCollector()

    def _check_ai_availability(self) -> dict[str, bool]:
        status = {"gigachat": False, "ollama": False, "reason": []}

        try:
            # Импортируем из правильного пути (src/ai/gigachat_bridge.py)
            import sys
            from pathlib import Path

            # Добавляем src/ в sys.path для импорта
            repo_root = Path(__file__).resolve().parents[3]  # agents/cognitive_agent/src/../../..
            src_path = repo_root / "src"
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))

            from ai.gigachat_bridge import GigaMCPBridge  # noqa: F401

            if os.getenv("GIGACHAT_API_KEY"):
                status["gigachat"] = True
            else:
                status["reason"].append("GIGACHAT_API_KEY not set")
        except ImportError as e:
            status["reason"].append(f"gigachat_bridge not available: {e}")

        try:
            # Ollama агент находится в agents/cognitive_agent/
            from agents.cognitive_agent.src.ollama_agent import OllamaAgent  # noqa: F401
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            status["ollama"] = response.status_code == 200
            if not status["ollama"]:
                status["reason"].append("Ollama server not responding")
        except ImportError as e:
            status["reason"].append(f"ollama_agent not available: {e}")
        except Exception as e:
            status["reason"].append(f"Ollama connection error: {str(e)}")

        return status

    def _check_tool_availability(self) -> dict[AnalysisTool, bool]:
        import shutil

        tools: dict[AnalysisTool, bool] = {}
        for tool in AnalysisTool:
            try:
                tool_cmd = tool.value
                if tool == AnalysisTool.PYTEST_COVERAGE:
                    try:
                        result = subprocess.run(
                            [sys.executable, "-m", "pytest", "--version"],
                            capture_output=True,
                            text=True,
                            cwd=self.project_path,
                            shell=False,
                        )
                        pytest_available = result.returncode == 0

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
                elif tool in [AnalysisTool.MYPY, AnalysisTool.RUFF, AnalysisTool.BANDIT]:
                    if shutil.which(tool_cmd):
                        tools[tool] = True
                    else:
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
                    if shutil.which("pyright"):
                        tools[tool] = True
                    else:
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
                    tools[tool] = bool(shutil.which(tool_cmd))
            except Exception:
                tools[tool] = False

        return tools

    def _run_analysis_with_timeout(self, cmd: list, timeout: int = 300) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_path, shell=False, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"Command {cmd} timed out after {timeout} seconds")
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Command timed out")

    def _get_full_path(self, cmd: list) -> list:
        import shutil

        if not cmd:
            return cmd

        tool_name = cmd[0]
        full_path = shutil.which(tool_name)
        if full_path:
            cmd[0] = full_path
        elif tool_name in ["mypy", "ruff", "bandit", "coverage", "pytest"]:
            cmd = [sys.executable, "-m"] + cmd
        return cmd

    def _safe_run(self, cmd: list) -> subprocess.CompletedProcess:
        try:
            cmd = self._get_full_path(cmd)
            return self._run_analysis_with_timeout(cmd)
        except Exception as e:
            logger.error(f"Error in _safe_run: {e}")
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr=str(e))

    def run_mypy_analysis(self) -> AnalysisResult:
        if not self.tools_available.get(AnalysisTool.MYPY):
            return AnalysisResult(
                AnalysisTool.MYPY, False, "MyPy не установлен или недоступен", [], {"error": "MyPy not available"}
            )

        try:
            cmd = ["mypy", "--no-error-summary", "--show-error-codes", "."]
            result = self._safe_run(cmd)
            success = result.returncode == 0
            output = result.stdout + result.stderr

            issues: list[dict[str, Any]] = []
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
                "total_errors": len([i for i in issues if i.get("type") == "error"]),
                "total_warnings": len([i for i in issues if i.get("type") == "warning"]),
                "success": success,
            }

            return AnalysisResult(AnalysisTool.MYPY, success, output, issues, summary)
        except Exception as e:
            return AnalysisResult(AnalysisTool.MYPY, False, f"Ошибка при запуске MyPy: {e}", [], {"error": str(e)})

    def run_ruff_analysis(self) -> AnalysisResult:
        if not self.tools_available.get(AnalysisTool.RUFF):
            return AnalysisResult(
                AnalysisTool.RUFF, False, "Ruff не установлен или недоступен", [], {"error": "Ruff not available"}
            )

        try:
            config_args = ["ruff", "check", ".", "--output-format=json"]
            result = self._safe_run(config_args)
            success = result.returncode in [0, 1]
            output = result.stdout + result.stderr

            issues: list[dict[str, Any]] = []
            try:
                for line in output.strip().split("\n"):
                    if not line.strip():
                        continue
                    try:
                        issues.append(json.loads(line))
                    except json.JSONDecodeError:
                        # heuristic fallback
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
            except Exception:
                pass

            summary = {"total_issues": len(issues), "success": success, "raw_return_code": result.returncode}
            return AnalysisResult(AnalysisTool.RUFF, success, output, issues, summary)
        except Exception as e:
            return AnalysisResult(AnalysisTool.RUFF, False, f"Ошибка при запуске Ruff: {e}", [], {"error": str(e)})

    def run_bandit_analysis(self) -> AnalysisResult:
        if not self.tools_available.get(AnalysisTool.BANDIT):
            return AnalysisResult(
                AnalysisTool.BANDIT, False, "Bandit не установлен или недоступен", [], {"error": "Bandit not available"}
            )

        try:
            cmd = ["bandit", "-r", ".", "-f", "json"]
            result = self._safe_run(cmd)
            success = result.returncode in [0, 1]
            output = result.stdout

            issues: list[dict[str, Any]] = []
            summary: dict[str, Any] = {"success": success}

            try:
                if output.strip():
                    data = json.loads(output)
                    issues = data.get("results", [])
                    summary.update(
                        {
                            "total_issues": len(issues),
                            "severity_stats": {
                                "LOW": len([r for r in issues if r.get("issue_severity") == "LOW"]),
                                "MEDIUM": len([r for r in issues if r.get("issue_severity") == "MEDIUM"]),
                                "HIGH": len([r for r in issues if r.get("issue_severity") == "HIGH"]),
                            },
                        }
                    )
            except json.JSONDecodeError:
                return AnalysisResult(
                    tool=AnalysisTool.BANDIT,
                    success=False,
                    output=f"Ошибка при парсинге результатов Bandit: {output}",
                    issues=[],
                    summary={"error": "Failed to parse Bandit output as JSON"},
                )

            return AnalysisResult(AnalysisTool.BANDIT, success, output, issues, summary)
        except Exception as e:
            return AnalysisResult(AnalysisTool.BANDIT, False, f"Ошибка при запуске Bandit: {e}", [], {"error": str(e)})

    def run_pyright_analysis(self) -> AnalysisResult:
        if not self.tools_available.get(AnalysisTool.PYRIGHT):
            return AnalysisResult(
                AnalysisTool.PYRIGHT,
                False,
                "Pyright не установлен или недоступен",
                [],
                {"error": "Pyright not available"},
            )

        try:
            cmd = ["pyright", "--outputjson"]
            result = self._safe_run(cmd)
            success = result.returncode == 0
            output = result.stdout

            issues: list[dict[str, Any]] = []
            summary: dict[str, Any] = {"success": success}

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
                return AnalysisResult(
                    tool=AnalysisTool.PYRIGHT,
                    success=False,
                    output=f"Ошибка при парсинге результатов Pyright: {output}",
                    issues=[],
                    summary={"error": "Failed to parse Pyright output as JSON"},
                )

            return AnalysisResult(AnalysisTool.PYRIGHT, success, output, issues, summary)
        except Exception as e:
            return AnalysisResult(
                AnalysisTool.PYRIGHT, False, f"Ошибка при запуске Pyright: {e}", [], {"error": str(e)}
            )

    def run_coverage_analysis(self) -> AnalysisResult:
        if not self.tools_available.get(AnalysisTool.PYTEST_COVERAGE):
            return AnalysisResult(
                AnalysisTool.PYTEST_COVERAGE,
                False,
                "Pytest или Coverage не установлены или недоступны",
                [],
                {"error": "Coverage tools not available"},
            )

        try:
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tf:
                    temp_file = tf.name

                coverage_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "run", "-m", "pytest"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    shell=False,
                )

                report_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_path,
                    shell=False,
                )

                output = coverage_result.stdout + coverage_result.stderr

                summary = {"success": True, "coverage_output": report_result.stdout}
                if report_result.returncode == 0:
                    try:
                        coverage_data = json.loads(report_result.stdout)
                        summary.update(
                            {
                                "total_coverage": coverage_data.get("totals", {}).get("percent_covered_display", 0),
                                "files_count": len(coverage_data.get("files", {})),
                                "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                            }
                        )
                    except json.JSONDecodeError:
                        pass

                success = coverage_result.returncode == 0
                return AnalysisResult(AnalysisTool.PYTEST_COVERAGE, success, output, [], summary)
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
        except Exception as e:
            return AnalysisResult(
                AnalysisTool.PYTEST_COVERAGE,
                False,
                f"Ошибка при запуске анализа покрытия: {e}",
                [],
                {"error": str(e)},
            )

    def run_full_analysis(self) -> dict[AnalysisTool, AnalysisResult]:
        results: dict[AnalysisTool, AnalysisResult] = {}
        if self.tools_available.get(AnalysisTool.MYPY):
            results[AnalysisTool.MYPY] = self.run_mypy_analysis()
        if self.tools_available.get(AnalysisTool.RUFF):
            results[AnalysisTool.RUFF] = self.run_ruff_analysis()
        if self.tools_available.get(AnalysisTool.BANDIT):
            results[AnalysisTool.BANDIT] = self.run_bandit_analysis()
        if self.tools_available.get(AnalysisTool.PYRIGHT):
            results[AnalysisTool.PYRIGHT] = self.run_pyright_analysis()
        if self.tools_available.get(AnalysisTool.PYTEST_COVERAGE):
            results[AnalysisTool.PYTEST_COVERAGE] = self.run_coverage_analysis()
        return results

    def generate_quality_report(self) -> dict[str, Any]:
        analysis_results = self.run_full_analysis()

        report: dict[str, Any] = {
            "project_path": str(self.project_path),
            "timestamp": str(datetime.now()),
            "tools_run": len(analysis_results),
            "tools_available": {tool.value: available for tool, available in self.tools_available.items()},
            "results": {},
            "metrics": self.metrics.to_dict(),
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

            if tool == AnalysisTool.MYPY:
                report["summary"]["total_errors"] += result.summary.get("total_errors", 0)
                report["summary"]["total_warnings"] += result.summary.get("total_warnings", 0)
            elif tool == AnalysisTool.RUFF:
                report["summary"]["total_style_issues"] += result.summary.get("total_issues", 0)
            elif tool == AnalysisTool.BANDIT:
                report["summary"]["total_security_issues"] += result.summary.get("total_issues", 0)
            elif tool == AnalysisTool.PYTEST_COVERAGE:
                report["summary"]["coverage_percentage"] = result.summary.get("total_coverage", 0)

        total_problems = (
            report["summary"]["total_errors"]
            + report["summary"]["total_warnings"]
            + report["summary"]["total_style_issues"]
            + report["summary"]["total_security_issues"]
        )
        report["summary"]["all_good"] = total_problems == 0
        return report

    def _normalize_issue(self, issue: dict[str, Any], tool: str) -> dict[str, Any] | None:
        try:
            normalized = {
                "tool": tool,
                "file": issue.get("file", issue.get("filename", "unknown")),
                "line": issue.get("line", issue.get("line_number", 0)),
                "message": issue.get("message", issue.get("text", "")),
                "severity": self._extract_severity(issue, tool),
            }
            return {k: v for k, v in normalized.items() if v is not None}
        except Exception:
            return None

    def _extract_severity(self, issue: dict[str, Any], tool: str) -> str:
        try:
            if "issue_severity" in issue:
                return issue["issue_severity"]
            if "severity" in issue:
                return issue["severity"]
            if "type" in issue:
                if issue["type"] == "error" or "error" in str(issue["type"]).lower():
                    return "HIGH"
                return "LOW"
            return "LOW"
        except Exception:
            return "LOW"

    def run_analysis_with_recommendations(self) -> dict[str, Any]:
        try:
            analysis_results = self.run_full_analysis()
            all_issues = []
            for tool, result in analysis_results.items():
                for issue in result.issues:
                    normalized_issue = self._normalize_issue(issue, tool.value)
                    if normalized_issue:
                        all_issues.append(normalized_issue)

            recommendations: list[str] = []
            fixes: list[dict[str, Any]] = []

            for issue in all_issues:
                fix_result = self.suggest_fix_enhanced(issue)
                if fix_result["success"]:
                    fixes.append({"issue": issue, "fix": fix_result["fix"], "source": fix_result["source"]})
                    if fix_result["source"] != "rule-based (fallback)":
                        recommendations.append(f"AI suggests: {fix_result['fix']}")

            if self.thought_manager and fixes:
                self.thought_manager.capture_thought(
                    f"Найдено {len(fixes)} потенциальных проблем в коде",
                    context=f"Проблемы: {[f['issue']['message'][:50] for f in fixes]}",
                    priority="medium",
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
        try:
            analysis_results = self.run_full_analysis()
            critical: list[dict[str, Any]] = []
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

    def _get_rule_based_fix(self, issue: dict[str, Any]) -> str | None:
        message = str(issue.get("message", "")).lower()
        tool = str(issue.get("tool", ""))

        if "unused import" in message:
            return "Remove unused import"
        if "line too long" in message:
            return "Split long line into multiple lines"
        if tool == "ruff" and "e501" in message:
            return "Break line after 88 characters"
        if tool == "bandit" and "security" in message:
            return "Review security issue manually"
        if tool == "mypy" and "error" in message:
            return "Check type annotations and fix type mismatch"
        if tool == "ruff" and "f401" in message:
            return "Remove unused import"
        if tool == "ruff" and "f841" in message:
            return "Remove unused variable"
        return f"Issue: {message}. Consider reviewing this code pattern."

    def suggest_fix_enhanced(self, issue: dict[str, Any]) -> dict[str, Any]:
        cached = self.ai_cache.get(issue)
        if cached:
            return {"success": True, "source": "cache", "fix": cached}

        if not self.use_ai:
            return {"success": True, "source": "rule-based (AI disabled)", "fix": self._get_rule_based_fix(issue)}

        fix = None
        source = None

        if self.ai_available.get("gigachat"):
            try:
                fix = self._call_gigachat(issue)
                source = "gigachat"
            except Exception as e:
                logger.warning(f"GigaChat failed: {e}")

        if not fix and self.ai_available.get("ollama"):
            try:
                fix = self._call_ollama(issue)
                source = "ollama"
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")

        if not fix:
            fix = self._get_rule_based_fix(issue)
            source = "rule-based (fallback)"

        if source in ["gigachat", "ollama"]:
            self.ai_cache.set(issue, fix)

        return {"success": True, "source": source, "fix": fix, "ai_available": self.ai_available}

    def _call_gigachat(self, issue: dict[str, Any]) -> str | None:
        from ai.gigachat_bridge import giga_request

        prompt = (
            f"Исправь проблему в коде:\n"
            f"Инструмент: {issue.get('tool', 'unknown')}\n"
            f"Файл: {issue.get('file', 'unknown')}\n"
            f"Строка: {issue.get('line', 'unknown')}\n"
            f"Сообщение: {issue.get('message', 'unknown')}\n"
            f"Серьезность: {issue.get('severity', 'unknown')}\n\n"
            "Предложи конкретное исправление в формате JSON: {\"fix\": \"код\", \"explanation\": \"описание\"}"
        )

        return giga_request(prompt)

    def _call_ollama(self, issue: dict[str, Any]) -> str | None:
        from agents.cognitive_agent.src.ollama_agent import OllamaAgent

        prompt = (
            f"Ты — эксперт по Python. Исправь проблему в коде:\n"
            f"Инструмент: {issue.get('tool', 'unknown')}\n"
            f"Файл: {issue.get('file', 'unknown')}\n"
            f"Строка: {issue.get('line', 'unknown')}\n"
            f"Сообщение: {issue.get('message', 'unknown')}\n\n"
            "Предложи исправление в простом тексте."
        )
        agent = OllamaAgent()
        return agent.ask(prompt)

    def apply_fix(self, issue: dict[str, Any], file_path: str) -> bool | None:
        """Применить фикс.

        Если AGENT_ACTIONS_READONLY=1 — фикс не применяется (только анализ).
        """
        try:
            if os.getenv("AGENT_ACTIONS_READONLY", "0") == "1":
                logger.warning(
                    "AGENT_ACTIONS_READONLY=1: apply_fix is disabled for safety (file=%s, tool=%s)",
                    file_path,
                    issue.get("tool"),
                )
                return None

            fix_result = self.suggest_fix_enhanced(issue)
            if not fix_result.get("success"):
                logger.warning("No fix suggestion available")
                return None
            return self.smart_fixer.apply_fix_with_backup(file_path, issue, fix_result)
        except Exception as e:
            logger.error("Error in apply_fix: %s", e)
            return None
