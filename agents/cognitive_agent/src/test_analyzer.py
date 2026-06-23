"""
Модуль для анализа и управления тестами
"""

import ast
import logging
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TestFramework(Enum):
    """Типы фреймворков тестирования"""

    PYTEST = "pytest"
    UNITTEST = "unittest"
    DOCTEST = "doctest"
    CUSTOM = "custom"


@dataclass
class TestIssue:
    """Проблема с тестами"""

    file_path: str
    issue_type: str
    severity: str  # low, medium, high
    message: str
    suggested_fix: str | None = None


@dataclass
class TestResult:
    """Результат анализа тестов"""

    framework: TestFramework
    success: bool
    output: str
    issues: list[TestIssue]
    summary: dict[str, Any]


class TestAnalyzer:
    """Класс для анализа тестов в проекте"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.test_patterns = ["test_*.py", "*_test.py", "tests/**/test_*.py", "tests/**/*_test.py", "**/test/**/*.py"]
        self.test_files = self._find_test_files()
        self.framework = self._detect_test_framework()

    def _find_test_files(self) -> list[Path]:
        """Найти все файлы тестов в проекте"""
        test_files = []

        # Поиск по распространенным паттернам
        for pattern in self.test_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    test_files.append(file_path)

        # Также ищем в специфичных директориях тестов
        test_dirs = ["tests", "test", "spec", "features"]
        for test_dir in test_dirs:
            dir_path = self.project_path / test_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*.py"):
                    if file_path.is_file() and ("test" in file_path.name.lower() or "spec" in file_path.name.lower()):
                        if file_path not in test_files:
                            test_files.append(file_path)

        return sorted(test_files)

    def _detect_test_framework(self) -> TestFramework:
        """Определить используемый фреймворк тестирования"""
        # Проверяем файлы на использование конкретных фреймворков
        for test_file in self.test_files:
            try:
                with open(test_file, encoding="utf-8") as f:
                    content = f.read()

                if "import pytest" in content or "from pytest" in content:
                    return TestFramework.PYTEST
                elif "import unittest" in content or "from unittest" in content:
                    return TestFramework.UNITTEST
                elif ">>> " in content:  # Doctest
                    return TestFramework.DOCTEST
            except:
                continue

        # Проверяем конфигурационные файлы
        config_files = ["pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"]
        for config_file in config_files:
            config_path = self.project_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        content = f.read().lower()

                    if "pytest" in content:
                        return TestFramework.PYTEST
                    elif "unittest" in content:
                        return TestFramework.UNITTEST
                except:
                    continue

        return TestFramework.CUSTOM

    def analyze_test_structure(self) -> dict[str, Any]:
        """Анализировать структуру тестов"""
        structure_analysis = {
            "total_test_files": len(self.test_files),
            "framework_detected": self.framework.value,
            "test_file_organization": {},
            "test_patterns_found": [],
            "potential_issues": [],
        }

        for test_file in self.test_files:
            # Определяем тип файла
            if "integration" in test_file.name.lower():
                file_type = "integration"
            elif "unit" in test_file.name.lower():
                file_type = "unit"
            elif "e2e" in test_file.name.lower() or "end2end" in test_file.name.lower():
                file_type = "e2e"
            else:
                file_type = "general"

            # Анализируем содержимое файла
            try:
                with open(test_file, encoding="utf-8") as f:
                    content = f.read()

                # Подсчитываем тесты
                test_count = len(re.findall(r"def test_", content))

                # Проверяем наличие setUp/tearDown (для unittest)
                has_setup_teardown = "setUp" in content or "tearDown" in content

                # Проверяем fixtures (для pytest)
                has_fixtures = "@pytest.fixture" in content or "@fixture" in content

                # Проверяем параметризованные тесты
                has_parametrized = "@pytest.mark.parametrize" in content or "parametrize" in content

                structure_analysis["test_file_organization"][str(test_file)] = {
                    "type": file_type,
                    "test_count": test_count,
                    "has_setup_teardown": has_setup_teardown,
                    "has_fixtures": has_fixtures,
                    "has_parametrized": has_parametrized,
                }

                # Проверяем потенциальные проблемы
                if test_count == 0:
                    structure_analysis["potential_issues"].append(
                        {"file": str(test_file), "type": "no_tests", "message": "Файл не содержит тестов"}
                    )

                # Проверяем длинные тесты (более 50 строк)
                lines = content.split("\n")
                current_test_lines = 0
                for line in lines:
                    if line.strip().startswith("def test_"):
                        current_test_lines = 1
                    elif current_test_lines > 0:
                        current_test_lines += 1
                        if current_test_lines > 50:
                            structure_analysis["potential_issues"].append(
                                {
                                    "file": str(test_file),
                                    "type": "long_test",
                                    "message": f"Тест в строке около {lines.index(line)} слишком длинный",
                                }
                            )
                            current_test_lines = 0  # Сбрасываем счетчик после обнаружения

            except Exception as e:
                logger.warning(f"Ошибка при анализе структуры теста {test_file}: {e}")

        return structure_analysis

    def analyze_test_coverage(self) -> dict[str, Any]:
        """Анализировать покрытие тестами"""
        coverage_analysis = {
            "framework": self.framework.value,
            "coverage_available": False,
            "total_coverage": 0,
            "covered_files": 0,
            "uncovered_files": 0,
            "coverage_by_file": {},
            "missing_coverage": [],
        }

        try:
            # Проверяем, установлен ли coverage
            import coverage

            # Создаем экземпляр coverage
            coverage.Coverage()

            # Запускаем тесты с покрытием
            if self.framework == TestFramework.PYTEST:
                # Запускаем pytest с покрытием
                cmd = [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=.",
                    "--cov-report=json",
                    "--cov-report=term-missing",
                    str(self.project_path),
                ]
            else:
                # Запускаем с coverage
                cmd = ["coverage", "run", "-m", "pytest", str(self.project_path)]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_path, timeout=300
            )  # 5 минут таймаут

            if result.returncode == 0:
                coverage_analysis["coverage_available"] = True

                # Получаем отчет о покрытии
                if self.framework == TestFramework.PYTEST:
                    # Если используется pytest-cov, получаем JSON отчет
                    import json

                    json_report_path = self.project_path / ".coverage.json"
                    if json_report_path.exists():
                        with open(json_report_path) as f:
                            json_report = json.load(f)

                        # Обрабатываем JSON отчет
                        coverage_analysis["total_coverage"] = json_report.get("totals", {}).get("percent_covered", 0)
                        coverage_analysis["covered_files"] = len(json_report.get("files", {}))
                else:
                    # Используем coverage для получения отчета
                    subprocess.run(
                        ["coverage", "report", "--format=json"], capture_output=True, text=True, cwd=self.project_path
                    )

                    # Получаем JSON отчет
                    json_result = subprocess.run(
                        ["coverage", "json"], capture_output=True, text=True, cwd=self.project_path
                    )

                    if json_result.returncode == 0:
                        import json

                        json_report = json.loads(json_result.stdout)

                        coverage_analysis["total_coverage"] = json_report.get("totals", {}).get("percent_covered", 0)
                        coverage_analysis["covered_files"] = len(json_report.get("files", {}))

                        # Анализируем файлы с низким покрытием
                        for file_path, file_data in json_report.get("files", {}).items():
                            covered_percent = file_data.get("summary", {}).get("percent_covered", 0)
                            coverage_analysis["coverage_by_file"][file_path] = covered_percent

                            if covered_percent < 50:  # Если покрытие ниже 50%
                                coverage_analysis["missing_coverage"].append(
                                    {
                                        "file": file_path,
                                        "coverage": covered_percent,
                                        "message": f"Файл имеет низкое покрытие: {covered_percent}%",
                                    }
                                )

        except ImportError:
            logger.warning("Модуль coverage не установлен")
        except subprocess.TimeoutExpired:
            logger.warning("Таймаут при анализе покрытия")
        except Exception as e:
            logger.warning(f"Ошибка при анализе покрытия: {e}")

        return coverage_analysis

    def analyze_test_quality(self) -> list[TestIssue]:
        """Анализировать качество тестов"""
        issues = []

        for test_file in self.test_files:
            try:
                with open(test_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        # Проверяем, есть ли asserts в тесте
                        has_assert = any(
                            isinstance(n, ast.Assert)
                            or (
                                isinstance(n, ast.Expr)
                                and isinstance(n.value, ast.Call)
                                and isinstance(n.value.func, ast.Name)
                                and n.value.func.id == "assert"
                            )
                            for n in ast.walk(node)
                        )

                        if not has_assert:
                            issues.append(
                                TestIssue(
                                    file_path=str(test_file),
                                    issue_type="no_assertions",
                                    severity="high",
                                    message=f"Тест '{node.name}' не содержит утверждений (asserts)",
                                )
                            )

                        # Проверяем, есть ли side effects (изменение глобального состояния)
                        has_side_effects = any(
                            isinstance(n, ast.Assign)
                            and isinstance(n.targets[0], ast.Name)
                            and n.targets[0].id.startswith(("global_", "shared_"))
                            for n in ast.walk(node)
                            if isinstance(n, ast.Assign)
                        )

                        if has_side_effects:
                            issues.append(
                                TestIssue(
                                    file_path=str(test_file),
                                    issue_type="side_effects",
                                    severity="medium",
                                    message=f"Тест '{node.name}' имеет побочные эффекты",
                                )
                            )

                        # Проверяем, использует ли тест внешние ресурсы без моков
                        has_external_calls = any(
                            isinstance(n, ast.Call)
                            and isinstance(n.func, ast.Attribute)
                            and n.func.attr in ["connect", "open", "request", "get", "post", "put", "delete"]
                            for n in ast.walk(node)
                            if isinstance(n, ast.Call)
                        )

                        if has_external_calls:
                            issues.append(
                                TestIssue(
                                    file_path=str(test_file),
                                    issue_type="external_calls",
                                    severity="high",
                                    message=f"Тест '{node.name}' делает внешние вызовы без мокирования",
                                )
                            )

                        # Проверяем длину теста
                        test_lines = (
                            len(ast.get_source_segment(content, node).split("\n"))
                            if hasattr(ast, "get_source_segment")
                            else len(node.body)
                        )
                        if test_lines > 30:
                            issues.append(
                                TestIssue(
                                    file_path=str(test_file),
                                    issue_type="long_test",
                                    severity="medium",
                                    message=f"Тест '{node.name}' слишком длинный ({test_lines} строк)",
                                )
                            )

            except Exception as e:
                logger.warning(f"Ошибка при анализе качества теста {test_file}: {e}")

        return issues

    def run_test_analysis(self) -> dict[str, Any]:
        """Запустить полный анализ тестов"""
        logger.info(f"🧪 Начинаем анализ тестов в проекте: {self.project_path}")

        results = {
            "project_path": str(self.project_path),
            "framework_detected": self.framework.value,
            "total_test_files": len(self.test_files),
            "structure_analysis": self.analyze_test_structure(),
            "coverage_analysis": self.analyze_test_coverage(),
            "quality_issues": self.analyze_test_quality(),
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_severity_issues": 0,
                "medium_severity_issues": 0,
                "low_severity_issues": 0,
            },
        }

        # Подсчитываем проблемы качества
        for issue in results["quality_issues"]:
            results["summary"]["total_issues"] += 1
            if issue.severity == "high":
                results["summary"]["high_severity_issues"] += 1
                results["summary"]["critical_issues"] += 1
            elif issue.severity == "medium":
                results["summary"]["medium_severity_issues"] += 1
            elif issue.severity == "low":
                results["summary"]["low_severity_issues"] += 1

        # Добавляем информацию о покрытии к итоговой статистике
        coverage_info = results["coverage_analysis"]
        if coverage_info["coverage_available"]:
            results["summary"]["test_coverage"] = coverage_info["total_coverage"]

        logger.info(f"✅ Анализ тестов завершен. Найдено проблем: {results['summary']['total_issues']}")

        return results

    def generate_test_improvement_plan(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Сгенерировать план улучшения тестов"""
        improvements = {
            "timestamp": str(self.project_path),
            "project_path": str(self.project_path),
            "framework_detected": analysis_results.get("framework_detected", "unknown"),
            "recommendations": [],
            "priority_actions": [],
            "implementation_guide": {},
        }

        # Получаем информацию из анализа
        structure_analysis = analysis_results.get("structure_analysis", {})
        coverage_analysis = analysis_results.get("coverage_analysis", {})
        quality_issues = analysis_results.get("quality_issues", [])

        # Рекомендации на основе проблем качества
        if len(quality_issues) > 0:
            high_severity_issues = [iq for iq in quality_issues if iq.severity == "high"]
            if high_severity_issues:
                improvements["recommendations"].append(
                    {
                        "category": "test_quality",
                        "priority": "high",
                        "description": f"Устранить {len(high_severity_issues)} критических проблем в тестах",
                        "details": "Фокус на тестах без утверждений, с внешними вызовами и побочными эффектами",
                    }
                )

        # Рекомендации на основе покрытия
        if coverage_analysis.get("coverage_available", False):
            coverage_percent = coverage_analysis.get("total_coverage", 0)
            if coverage_percent < 70:  # Если покрытие меньше 70%
                improvements["recommendations"].append(
                    {
                        "category": "test_coverage",
                        "priority": "high",
                        "description": f"Увеличить покрытие тестами с {coverage_percent}% до 80%",
                        "details": f"Текущее покрытие {coverage_percent}% ниже рекомендуемого уровня",
                    }
                )

                # Добавляем информацию о файлах с низким покрытием
                low_coverage_files = coverage_analysis.get("missing_coverage", [])
                if low_coverage_files:
                    improvements["recommendations"].append(
                        {
                            "category": "targeted_testing",
                            "priority": "medium",
                            "description": f"Добавить тесты для {len(low_coverage_files)} файлов с низким покрытием",
                            "details": f"Файлы с покрытием менее 50%: {[item['file'] for item in low_coverage_files[:5]]}",  # первые 5
                        }
                    )

        # Рекомендации на основе структуры
        if structure_analysis.get("total_test_files", 0) == 0:
            improvements["recommendations"].append(
                {
                    "category": "missing_tests",
                    "priority": "high",
                    "description": "В проекте отсутствуют тесты",
                    "details": "Необходимо добавить базовые юнит-тесты для основных компонентов",
                }
            )
        else:
            # Проверяем соотношение тестов к коду
            total_test_files = structure_analysis.get("total_test_files", 0)
            # Здесь мы бы хотели получить количество production файлов, но для простоты просто добавим общую рекомендацию
            improvements["recommendations"].append(
                {
                    "category": "test_balance",
                    "priority": "medium",
                    "description": f"Оптимизировать соотношение тестов к production коду ({total_test_files} тестовых файлов)",
                    "details": "Проверить, что тесты покрывают основные бизнес-логики",
                }
            )

        # Приоритетные действия
        if len([iq for iq in quality_issues if iq.severity == "high"]) > 0:
            improvements["priority_actions"].append("Исправить критические проблемы в тестах")

        if coverage_analysis.get("total_coverage", 0) < 50:
            improvements["priority_actions"].append("Увеличить покрытие тестами")

        if structure_analysis.get("total_test_files", 0) == 0:
            improvements["priority_actions"].append("Создать базовую тестовую структуру")

        # Руководство по внедрению
        improvements["implementation_guide"] = {
            "step_by_step": [
                "1. Исправить критические проблемы в существующих тестах",
                "2. Добавить базовые юнит-тесты для основных функций",
                "3. Настроить CI/CD для автоматического запуска тестов",
                "4. Внедрить минимальные требования к покрытию тестами",
                "5. Добавить интеграционные тесты для ключевых компонентов",
            ],
            "tools_suggestions": [
                "pytest для запуска тестов",
                "pytest-cov для анализа покрытия",
                "pytest-mock для мокирования зависимостей",
                "factory-boy для генерации тестовых данных",
            ],
            "metrics_to_track": [
                "Процент покрытия кода тестами",
                "Количество пройденных/упавших тестов",
                "Время выполнения тестов",
                "Количество тестов на функцию/класс",
            ],
        }

        return improvements
