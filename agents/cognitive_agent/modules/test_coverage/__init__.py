"""
Модуль тестового покрытия для когнитивного агента
Выбор и генерация тестов по типу сервиса
"""

from pathlib import Path
from typing import Any, Dict, List

from agents.cognitive_agent.src.test_analyzer import TestAnalyzer


class TestSelector:
    """Выбор стратегии тестирования по типу сервиса"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.test_analyzer = autonomous_agent.test_analyzer
        self.service_registry = autonomous_agent.service_registry

    def select_test_strategy(self, service_name: str) -> dict[str, Any]:
        """
        Выбор стратегии тестирования для сервиса
        :param service_name: Имя сервиса
        :return: Стратегия тестирования
        """
        service_profile = self.service_registry.get_profile_by_name(service_name)

        if not service_profile:
            return {"strategy": "default", "framework": "pytest"}

        framework = service_profile.framework
        language = service_profile.language

        strategies = {
            ("python", "fastapi"): {
                "strategy": "fastapi",
                "framework": "pytest",
                "additional_deps": ["pytest-asyncio", "httpx"],
                "test_types": ["unit", "integration", "api"],
                "coverage_target": 85.0,
            },
            ("python", "flask"): {
                "strategy": "flask",
                "framework": "pytest",
                "additional_deps": ["flask-test"],
                "test_types": ["unit", "integration", "api"],
                "coverage_target": 80.0,
            },
            ("python", "django"): {
                "strategy": "django",
                "framework": "pytest-django",
                "additional_deps": ["pytest-django"],
                "test_types": ["unit", "integration", "functional"],
                "coverage_target": 85.0,
            },
            ("python", "celery"): {
                "strategy": "celery",
                "framework": "pytest-celery",
                "additional_deps": ["pytest-celery"],
                "test_types": ["unit", "integration"],
                "coverage_target": 75.0,
            },
            ("python", "library"): {
                "strategy": "library",
                "framework": "pytest",
                "additional_deps": [],
                "test_types": ["unit"],
                "coverage_target": 90.0,
            },
            ("typescript", "react"): {
                "strategy": "react",
                "framework": "jest",
                "additional_deps": ["@testing-library/react"],
                "test_types": ["unit", "component", "integration"],
                "coverage_target": 80.0,
            },
            ("javascript", "node"): {
                "strategy": "node",
                "framework": "jest",
                "additional_deps": [],
                "test_types": ["unit", "integration"],
                "coverage_target": 75.0,
            },
        }

        key = (language, framework)
        default_strategy = {
            "strategy": "default",
            "framework": "pytest",
            "additional_deps": [],
            "test_types": ["unit"],
            "coverage_target": 80.0,
        }

        return strategies.get(key, default_strategy)

    def get_test_coverage_requirements(self, service_name: str) -> dict[str, Any]:
        """Получение требований к покрытию тестами"""
        service_profile = self.service_registry.get_profile_by_name(service_name)

        return {
            "minimum_coverage": service_profile.coverage_target if service_profile else 80.0,
            "required_test_types": ["unit"],
            "optional_test_types": ["integration", "e2e"],
            "coverage_tools": ["pytest-cov", "coverage.py"],
        }


class TestCoveragePlanner:
    """Планировщик тестового покрытия"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.test_analyzer = autonomous_agent.test_analyzer
        self.test_selector = TestSelector(autonomous_agent)
        self.test_generator = autonomous_agent.test_generator

    def ensure_coverage(self) -> dict[str, Any]:
        """
        Обеспечение тестового покрытия всех сервисов
        :return: Отчет о тестовом покрытии
        """
        coverage_report = self.test_analyzer.analyze_coverage_all_services()

        gaps = []
        for service_name, coverage in coverage_report.items():
            required = self.test_selector.get_test_coverage_requirements(service_name)
            current = coverage.get("coverage", 0)

            if current < required["minimum_coverage"]:
                gaps.append(
                    {
                        "service": service_name,
                        "current_coverage": current,
                        "required_coverage": required["minimum_coverage"],
                        "gap": required["minimum_coverage"] - current,
                    }
                )

        # Генерация плана для закрытия пробелов
        improvement_plan = self._generate_improvement_plan(gaps)

        return {
            "current_coverage": coverage_report,
            "gaps": gaps,
            "improvement_plan": improvement_plan,
            "estimated_completion": self._estimate_completion(improvement_plan),
        }

    def _generate_improvement_plan(self, gaps: list[dict]) -> dict[str, Any]:
        """Генерация плана улучшения"""
        plan = {"services_to_fix": [], "estimated_tests": 0, "estimated_time": 0}

        for gap in gaps:
            service = gap["service"]
            gap_size = gap["gap"]

            # Оценка количества тестов needed (примерно 10 тестов на 10% покрытия)
            tests_needed = int(gap_size * 10 / 10)
            time_needed = tests_needed * 0.5  # 30 минут на тест

            plan["services_to_fix"].append(
                {"service": service, "tests_needed": tests_needed, "time_needed": time_needed}
            )

            plan["estimated_tests"] += tests_needed
            plan["estimated_time"] += time_needed

        return plan

    def _estimate_completion(self, plan: dict) -> str:
        """Оценка времени завершения"""
        total_hours = plan["estimated_time"] / 60
        days_needed = total_hours / 8  # 8 часов в день

        if days_needed < 1:
            return f"{total_hours:.1f} часов"
        elif days_needed < 7:
            return f"{days_needed:.1f} дней"
        else:
            weeks = days_needed / 5
            return f"{weeks:.1f} недель"

    def generate_tests_for_service(self, service_name: str, strategy: str = None) -> dict[str, Any]:
        """Генерация тестов для сервиса"""
        if not strategy:
            strategy = self.test_selector.select_test_strategy(service_name)

        # Генерация тестов через AI
        tests = self.test_generator.generate_for_service(service_name=service_name, strategy=strategy)

        return {
            "service": service_name,
            "strategy": strategy,
            "tests_generated": tests,
            "coverage_improvement": self._estimate_coverage_improvement(tests),
        }

    def _estimate_coverage_improvement(self, tests: list[dict]) -> float:
        """Оценка улучшения покрытия"""
        if not tests:
            return 0.0

        # Примерная оценка (каждый тест дает ~2-5% покрытия)
        estimated_improvement = len(tests) * 3.0
        return min(estimated_improvement, 50.0)  # Максимум 50% за раз


class TestCoverageAnalyzer:
    """Анализатор тестового покрытия"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.test_analyzer = autonomous_agent.test_analyzer

    def analyze_coverage_all_services(self) -> dict[str, Any]:
        """Анализ покрытия тестами всех сервисов"""
        coverage_report = {}

        for service in self.autonomous_agent.service_registry.services:
            coverage = self.test_analyzer.analyze_coverage(service.path)
            coverage_report[service.name] = coverage

        return coverage_report

    def identify_coverage_gaps(self, service_name: str) -> list[dict]:
        """Выявление пробелов в покрытии тестами"""
        service_path = self.autonomous_agent.service_registry.get_service_path(service_name)

        return self.test_analyzer.identify_coverage_gaps(service_path)
