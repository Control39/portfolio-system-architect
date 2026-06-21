"""
Модуль для интеграции агента с инструментами статического анализа кода
"""

import json
import logging
import subprocess
from dataclasses import dataclass
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


class CodeAnalyzer:
    """Класс для интеграции с инструментами статического анализа"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.tools_available = self._check_tool_availability()

    def _check_tool_availability(self) -> dict[AnalysisTool, bool]:
        """Проверить доступность инструментов анализа"""
        tools = {}
        for tool in AnalysisTool:
            try:
                if tool == AnalysisTool.MYPY:
                    result = subprocess.run(
                        ["mypy", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    tools[tool] = result.returncode == 0
                elif tool == AnalysisTool.RUFF:
                    result = subprocess.run(
                        ["ruff", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    tools[tool] = result.returncode == 0
                elif tool == AnalysisTool.BANDIT:
                    result = subprocess.run(
                        ["bandit", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    tools[tool] = result.returncode == 0
                elif tool == AnalysisTool.PYRIGHT:
                    result = subprocess.run(
                        ["pyright", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    tools[tool] = result.returncode == 0
                elif tool == AnalysisTool.PYTEST_COVERAGE:
                    # Проверяем наличие pytest и coverage
                    pytest_result = subprocess.run(
                        ["pytest", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    coverage_result = subprocess.run(
                        ["coverage", "--version"], capture_output=True, text=True, cwd=self.project_path
                    )
                    tools[tool] = pytest_result.returncode == 0 and coverage_result.returncode == 0
            except FileNotFoundError:
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
            result = subprocess.run(
                ["mypy", "--no-error-summary", "--show-error-codes", "."],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )

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
            result = subprocess.run(config_args, capture_output=True, text=True, cwd=self.project_path)

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
            result = subprocess.run(
                [
                    "bandit",
                    "-r",  # Рекурсивный анализ
                    ".",  # Текущая директория
                    "-f",
                    "json",  # Формат вывода
                ],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )

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
                # Если не удается распарсить JSON, возвращаем ошибку
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
            result = subprocess.run(["pyright", "--outputjson"], capture_output=True, text=True, cwd=self.project_path)

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
            # Сначала запускаем тесты с coverage
            coverage_result = subprocess.run(
                ["coverage", "run", "-m", "pytest"], capture_output=True, text=True, cwd=self.project_path
            )

            # Затем генерируем отчет
            report_result = subprocess.run(
                ["coverage", "report", "--format=json"], capture_output=True, text=True, cwd=self.project_path
            )

            success = coverage_result.returncode == 0
            output = coverage_result.stdout + coverage_result.stderr + report_result.stdout + report_result.stderr

            issues = []
            summary = {"success": success, "coverage_output": report_result.stdout}

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
                            try:
                                summary["total_coverage"] = float(parts[-1].replace("%", ""))
                            except ValueError:
                                pass
                        break

            return AnalysisResult(
                tool=AnalysisTool.PYTEST_COVERAGE, success=success, output=output, issues=issues, summary=summary
            )
        except Exception as e:
            return AnalysisResult(
                tool=AnalysisTool.PYTEST_COVERAGE,
                success=False,
                output=f"Ошибка при запуске анализа покрытия: {str(e)}",
                issues=[],
                summary={"error": str(e)},
            )

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


{
    "text": '    def generate_quality_report(self) -> Dict[str, Any]:\n        """Сгенерировать общий отчет о качестве кода"""\n        analysis_results = self.run_full_analysis()\n\n        report = {\n            "project_path": str(self.project_path),\n            "timestamp": str(self.project_path),\n            "tools_run": len(analysis_results),\n            "tools_available": {tool.value: available for tool, available in self.tools_available.items()},\n            "results": {},\n            "summary": {\n                "total_errors": 0,\n                "total_warnings": 0,\n                "total_security_issues": 0,\n                "total_style_issues": 0,\n                "coverage_percentage": 0,\n                "all_good": True\n            }\n        }\n\n        for tool, result in analysis_results.items():\n            report["results"][tool.value] = {\n                "success": result.success,\n                "summary": result.summary,\n                "issue_count": len(result.issues)\n            }\n\n            # Обновляем итоговую статистику\n            if tool == AnalysisTool.MYPY:\n                report["summary"]["total_errors"] += result.summary.get("total_errors", 0)\n                report["summary"]["total_warnings"] += result.summary.get("total_warnings", 0)\n            elif tool == AnalysisTool.RUFF:\n                report["summary"]["total_style_issues"] += result.summary.get("total_issues", 0)\n            elif tool == AnalysisTool.BANDIT:\n                report["summary"]["total_security_issues"] += result.summary.get("total_issues", 0)\n            elif tool == AnalysisTool.PYTEST_COVERAGE:\n                report["summary"]["coverage_percentage"] = result.summary.get("total_coverage", 0)\n\n        # Проверяем, есть ли какие-либо проблемы\n        total_problems = (\n            report["summary"]["total_errors"] +\n            report["summary"]["total_warnings"] +\n            report["summary"]["total_style_issues"] +\n            report["summary"]["total_security_issues"]\n        )\n        report["summary"]["all_good"] = total_problems == 0\n\n        return report\n\n    # ==================== НОВЫЕ МЕТОДЫ ДЛЯ РЕКОМЕНДАЦИЙ И AI ====================\n\n    def run_analysis_with_recommendations(self) -> Dict[str, Any]:\n        """Полный анализ с генерацией рекомендаций (заглушки для AI)"""\n        try:\n            analysis_results = self.run_full_analysis()\n            \n            # Формируем структуру с recommendations и fixes\n            all_issues = []\n            for tool, result in analysis_results.items():\n                for issue in result.issues:\n                    # Нормализуем структуру issue для совместимости с AI\n                    normalized_issue = self._normalize_issue(issue, tool.value)\n                    if normalized_issue:\n                        all_issues.append(normalized_issue)\n            \n            return {\n                "issues": all_issues,\n                "recommendations": [],  # Заглушка для будущей AI-генерации\n                "fixes": [],            # Заглушка для будущих AI-исправлений\n                "summary": {\n                    "total_issues": len(all_issues),\n                    "tools_analyzed": len(analysis_results),\n                    "critical_count": len([i for i in all_issues if i.get("severity") in ["HIGH", "MEDIUM"]])\n                }\n            }\n        except Exception as e:\n            logger.error("Error in run_analysis_with_recommendations: %s", e)\n            return {\n                "issues": [],\n                "recommendations": [],\n                "fixes": [],\n                "summary": {"error": str(e), "total_issues": 0}\n            }\n\n    def get_critical_issues(self) -> List[Dict[str, Any]]:\n        """Получить критичные и серьёзные проблемы (HIGH/MEDIUM)"""\n        try:\n            analysis_results = self.run_full_analysis()\n            critical = []\n            \n            for tool, result in analysis_results.items():\n                for issue in result.issues:\n                    severity = self._extract_severity(issue, tool.value)\n                    if severity in ["HIGH", "MEDIUM"]:\n                        normalized = self._normalize_issue(issue, tool.value)\n                        if normalized:\n                            normalized["severity"] = severity\n                            critical.append(normalized)\n            \n            return critical\n        except Exception as e:\n            logger.error("Error in get_critical_issues: %s", e)\n            return []\n\n    def save_results(self, results: Dict[str, Any], format: str = "json") -> Optional[str]:\n        """Сохранить результаты анализа в файл"""\n        try:\n            import json\n            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")\n            output_path = self.project_path / f"code_analysis_results_{timestamp}.{format}"\n            \n            if format == "json":\n                with open(output_path, "w", encoding="utf-8") as f:\n                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)\n                return str(output_path)\n            elif format == "text":\n                # Простой текстовый формат\n                lines = []\n                lines.append("Code Analysis Results")\n                lines.append("=" * 50)\n                lines.append(f"Project: {self.project_path}")\n                lines.append(f"Timestamp: {timestamp}")\n                lines.append(f"Total Issues: {results.get(\'summary\', {}).get(\'total_issues\', 0)}")\n                lines.append("")\n                \n                for issue in results.get("issues", []):\n                    lines.append(f"[{issue.get(\'severity\', \'UNKNOWN\')}] {issue.get(\'tool\', \'unknown\')}: {issue.get(\'file\', \'unknown\')}:{issue.get(\'line\', \'?\')} - {issue.get(\'message\', \'\')}")\n                \n                with open(output_path, "w", encoding="utf-8") as f:\n                    f.write("\\n".join(lines))\n                return str(output_path)\n            else:\n                logger.warning("Unsupported format: %s", format)\n                return None\n        except (ImportError, json.JSONDecodeError, OSError) as e:\n            logger.error("Error saving results: %s", e)\n            return None\n\n    def suggest_fix(self, issue: Dict[str, Any]) -> Optional[str]:\n        """Предложить исправление через AI (GigaChat или Ollama)"""\n        try:\n            # Проверяем наличие GigaChat\n            try:\n                from gigachat_bridge import giga_request\n                \n                prompt = (\n                    f"Исправь проблему в коде:\\n"\n                    f"Инструмент: {issue.get(\'tool\', \'unknown\')}\\n"\n                    f"Файл: {issue.get(\'file\', \'unknown\')}\\n"\n                    f"Строка: {issue.get(\'line\', \'unknown\')}\\n"\n                    f"Сообщение: {issue.get(\'message\', \'unknown\')}\\n"\n                    f"Серьезность: {issue.get(\'severity\', \'unknown\')}\\n\\n"\n                    f"Предложи конкретное исправление в формате JSON: {{\'fix\': \'код исправления\', \'explanation\': \'описание\'}}"\n                )\n                \n                response = giga_request(prompt)\n                if response:\n                    return response\n            except Exception as e:\n                logger.debug("GigaChat not available, trying Ollama: %s", e)\n            \n            # Fallback на Ollama\n            try:\n                from ollama_agent import OllamaAgent\n                \n                prompt = (\n                    f"Ты — эксперст по Python. Исправь проблему в коде:\\n"\n                    f"Инструмент: {issue.get(\'tool\', \'unknown\')}\\n"\n                    f"Файл: {issue.get(\'file\', \'unknown\')}\\n"\n                    f"Строка: {issue.get(\'line\', \'unknown\')}\\n"\n                    f"Сообщение: {issue.get(\'message\', \'unknown\')}\\n\\n"\n                    f"Предложи исправление в простом тексте."\n                )\n                \n                agent = OllamaAgent()\n                response = agent.ask(prompt)\n                if response:\n                    return response\n            except Exception as e:\n                logger.debug("Ollama not available: %s", e)\n            \n            # Все AI недоступны\n            logger.info("No AI available for suggest_fix (GigaChat/Ollama)")\n            return None\n        except Exception as e:\n            logger.error("Error in suggest_fix: %s", e)\n            return None\n\n    def apply_fix(self, issue: Dict[str, Any], file_path: str) -> Optional[bool]:\n        """Применить исправление к файлу"""\n        try:\n            import re\n            from pathlib import Path\n            \n            file = Path(file_path)\n            if not file.exists():\n                logger.error("File not found: %s", file_path)\n                return None\n            \n            content = file.read_text(encoding="utf-8")\n            lines = content.split("\\n")\n            \n            # Получаем исправление от AI\n            fix_suggestion = self.suggest_fix(issue)\n            if not fix_suggestion:\n                logger.warning("No fix suggestion available")\n                return None\n            \n            # Пытаемся извлечь исправление из JSON или текста\n            fix_code = None\n            try:\n                import json\n                data = json.loads(fix_suggestion)\n                fix_code = data.get("fix", fix_suggestion)\n            except json.JSONDecodeError:\n                # Если не JSON, используем весь текст как исправление\n                fix_code = fix_suggestion\n            \n            if not fix_code:\n                logger.warning("Empty fix code")\n                return None\n            \n            # Применяем исправление к строке\n            line_number = issue.get("line", 0)\n            if isinstance(line_number, str):\n                try:\n                    line_number = int(line_number)\n                except ValueError:\n                    line_number = 0\n            \n            if line_number > 0 and line_number <= len(lines):\n                # Заменяем строку (простая замена)\n                lines[line_number - 1] = fix_code\n            else:\n                # Если строка неизвестна, добавляем исправление в конец файла\n                lines.append(f"# Fix: {fix_code}")\n            \n            # Сохраняем файл\n            file.write_text("\\n".join(lines), encoding="utf-8")\n            return True\n        except Exception as e:\n            logger.error("Error in apply_fix: %s", e)\n            return None\n\n    def watch_changes(self) -> Optional[Any]:\n        """Мониторинг изменений файлов через watchdog"""\n        try:\n            from watchdog.observers import Observer\n            from watchdog.events import FileSystemEventHandler\n            \n            class CodeChangeHandler(FileSystemEventHandler):\n                def __init__(self, analyzer):\n                    self.analyzer = analyzer\n                \n                def on_modified(self, event):\n                    if event.is_directory:\n                        return\n                    if event.src_path.endswith(".py"):\n                        logger.info("Detected change in %s", event.src_path)\n                        # Можно вызывать аналитику для измененного файла\n                        # self.analyzer.analyze_changed_file(event.src_path)\n            \n            observer = Observer()\n            observer.schedule(CodeChangeHandler(self), str(self.project_path), recursive=True)\n            observer.start()\n            \n            logger.info("Started watching for code changes in %s", self.project_path)\n            return observer\n        except ImportError:\n            logger.warning("watchdog not installed, skipping file monitoring")\n            return None\n        except Exception as e:\n            logger.error("Error in watch_changes: %s", e)\n            return None\n\n    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================\n\n    def _normalize_issue(self, issue: Dict[str, Any], tool: str) -> Optional[Dict[str, Any]]:\n        """Нормализовать issue для совместимости с AI"""\n        try:\n            normalized = {\n                "tool": tool,\n                "file": issue.get("file", issue.get("filename", "unknown")),\n                "line": issue.get("line", issue.get("line_number", 0)),\n                "message": issue.get("message", issue.get("text", "")),\n                "severity": self._extract_severity(issue, tool)\n            }\n            \n            # Удаляем None значения\n            return {k: v for k, v in normalized.items() if v is not None}\n        except Exception:\n            return None\n\n    def _extract_severity(self, issue: Dict[str, Any], tool: str) -> str:\n        """Извлечь severity из issue"""\n        try:\n            # Для Bandit\n            if "issue_severity" in issue:\n                return issue["issue_severity"]\n            # Для Ruff\n            if "severity" in issue:\n                return issue["severity"]\n            # Для Ruff (альтернативный ключ)\n            if "type" in issue:\n                if issue["type"] == "error":\n                    return "HIGH"\n                return "LOW"\n            # Для Mypy\n            if "type" in issue:\n                if "error" in issue["type"].lower():\n                    return "HIGH"\n                return "LOW"\n            # По умолчанию\n            return "LOW"\n        except Exception:\n            return "LOW"'
}
