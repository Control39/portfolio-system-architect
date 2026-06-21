"""
Модули наставников для когнитивного агента
Обучение и сопровождение разработчика
"""

from pathlib import Path
from typing import Any, Dict, List


class CareerMentor:
    """Карьерный наставник"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.it_compass = autonomous_agent.it_compass

    def analyze_developer_profile(self) -> dict[str, Any]:
        """Анализ профиля разработчика"""
        return {
            "current_skills": self._extract_skills(),
            "career_stage": self._assess_stage(),
            "growth_areas": self._identify_growth_areas(),
            "market_value": self._calculate_market_value(),
            "it_compass_score": self._calculate_it_compass_score(),
        }

    def _extract_skills(self) -> list[str]:
        """Извлечение навыков"""
        skills = []

        # Анализ стека проекта
        for service in self.autonomous_agent.service_registry.services:
            if service.framework:
                skills.append(service.framework)
            if service.language:
                skills.append(service.language)

        return list(set(skills))

    def _assess_stage(self) -> str:
        """Оценка этапа карьеры"""
        # Анализ опыта на основе истории проекта
        return "mid"  # Упрощенная логика

    def _identify_growth_areas(self) -> list[dict[str, Any]]:
        """Выявление областей для роста"""
        return [
            {"area": "Cloud Native", "priority": "high", "reason": "Миграция на Kubernetes"},
            {"area": "AI/ML", "priority": "medium", "reason": "Интеграция с AI-сервисами"},
            {"area": "Security", "priority": "high", "reason": "Повышение уровня безопасности"},
        ]

    def _calculate_market_value(self) -> dict[str, Any]:
        """Расчет рыночной стоимости"""
        return {"level": "senior", "salary_range": "150-250k", "demand": "high"}

    def _calculate_it_compass_score(self) -> float:
        """Расчет оценки IT Compass"""
        return 75.0  # Упрощенная логика

    def create_development_plan(self, timeframe: str = "6_months") -> dict[str, Any]:
        """Создание плана развития"""
        profile = self.analyze_developer_profile()

        return {
            "timeframe": timeframe,
            "goals": self._set_goals(profile, timeframe),
            "resources": self._select_resources(profile),
            "milestones": self._define_milestones(timeframe),
            "it_compass_path": self._create_it_compass_path(profile),
        }

    def _set_goals(self, profile: dict, timeframe: str) -> list[dict[str, Any]]:
        """Установка целей"""
        return [
            {"goal": "Освоить Kubernetes", "deadline": "3_months", "success_criteria": "Успешный деплой в K8s"},
            {"goal": "Получить сертификат AWS", "deadline": "6_months", "success_criteria": "Сертификат получен"},
        ]

    def _select_resources(self, profile: dict) -> list[dict[str, Any]]:
        """Выбор ресурсов"""
        return [
            {"resource": "Kubernetes documentation", "type": "docs", "priority": "high"},
            {"resource": "AWS Certified Solutions Architect", "type": "course", "priority": "medium"},
        ]

    def _define_milestones(self, timeframe: str) -> list[dict[str, Any]]:
        """Определение вех"""
        return [
            {"milestone": "Начало обучения", "date": "now", "criteria": "План утвержден"},
            {"milestone": "Промежуточный ревью", "date": "3_months", "criteria": "Прогресс 50%"},
            {"milestone": "Финальная оценка", "date": "6_months", "criteria": "Цели достигнуты"},
        ]

    def _create_it_compass_path(self, profile: dict) -> list[dict[str, Any]]:
        """Создание пути развития IT Compass"""
        return [
            {
                "domain": "Архитектура",
                "current_level": 3,
                "target_level": 5,
                "actions": ["Изучить ADR", "Создать архитектурный план"],
            },
            {
                "domain": "Безопасность",
                "current_level": 2,
                "target_level": 4,
                "actions": ["Изучить security best practices", "Провести аудит"],
            },
        ]


class ItTutor:
    """IT-наставник"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent

    def analyze_tech_stack(self) -> dict[str, Any]:
        """Анализ технологического стека"""
        return {
            "languages": self._identify_languages(),
            "frameworks": self._identify_frameworks(),
            "tools": self._identify_tools(),
            "recommendations": self._generate_recommendations(),
        }

    def _identify_languages(self) -> list[str]:
        """Идентификация языков"""
        languages = []

        for service in self.autonomous_agent.service_registry.services:
            if service.language and service.language not in languages:
                languages.append(service.language)

        return languages

    def _identify_frameworks(self) -> list[str]:
        """Идентификация фреймворков"""
        frameworks = []

        for service in self.autonomous_agent.service_registry.services:
            if service.framework and service.framework not in frameworks:
                frameworks.append(service.framework)

        return frameworks

    def _identify_tools(self) -> list[str]:
        """Идентификация инструментов"""
        return ["pytest", "ruff", "mypy", "black", "docker", "git"]

    def _generate_recommendations(self) -> list[dict[str, Any]]:
        """Генерация рекомендаций"""
        return [
            {"recommendation": "Изучить Pydantic v2", "priority": "high", "reason": "Используется во многих сервисах"},
            {
                "recommendation": "Изучить FastAPI async patterns",
                "priority": "medium",
                "reason": "Используется в API сервисах",
            },
        ]

    def create_learning_plan(self, focus_area: str = "all") -> dict[str, Any]:
        """Создание плана обучения"""
        return {
            "focus_area": focus_area,
            "modules": self._create_modules(focus_area),
            "duration": "3_months",
            "assessment": self._create_assessment(),
        }

    def _create_modules(self, focus_area: str) -> list[dict[str, Any]]:
        """Создание модулей обучения"""
        return [
            {
                "module": "Основы Python",
                "duration": "2_weeks",
                "topics": ["синтаксис", "оптимизация", "best practices"],
            },
            {"module": "FastAPI", "duration": "3_weeks", "topics": ["endpoints", "validation", "authentication"]},
        ]

    def _create_assessment(self) -> dict[str, Any]:
        """Создание оценки"""
        return {"pre_assessment": True, "post_assessment": True, "certification": False}


class SkillDeveloper:
    """Разработчик навыков"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent

    def analyze_skill_gaps(self) -> list[dict[str, Any]]:
        """Анализ пробелов в навыках"""
        return [
            {"skill": "Kubernetes", "current_level": 2, "target_level": 4, "gap": 2, "priority": "high"},
            {"skill": "AI/ML", "current_level": 1, "target_level": 3, "gap": 2, "priority": "medium"},
        ]

    def create_skill_plan(self, timeframe: str = "6_months") -> dict[str, Any]:
        """Создание плана развития навыков"""
        gaps = self.analyze_skill_gaps()

        return {
            "timeframe": timeframe,
            "gaps_to_fill": gaps,
            "resources": self._select_resources(gaps),
            "milestones": self._define_milestones(timeframe),
        }

    def _select_resources(self, gaps: list[dict]) -> list[dict[str, Any]]:
        """Выбор ресурсов для заполнения пробелов"""
        return [
            {
                "skill": gap["skill"],
                "resource": f"Курсы по {gap['skill']}",
                "type": "course",
                "duration": f"{gap['gap'] * 2}_weeks",
            }
            for gap in gaps
        ]

    def _define_milestones(self, timeframe: str) -> list[dict[str, Any]]:
        """Определение вех"""
        return [
            {"milestone": "План утвержден", "date": "now", "criteria": "План создан"},
            {"milestone": "Половина плана выполнена", "date": "3_months", "criteria": "50% навыков освоены"},
            {"milestone": "План завершен", "date": "6_months", "criteria": "Все навыки освоены"},
        ]


class LearningPathPlanner:
    """Планировщик пути обучения"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent

    def create_personalized_path(self, developer_profile: dict) -> dict[str, Any]:
        """Создание персонализированного пути обучения"""
        return {
            "profile": developer_profile,
            "path": self._define_path(developer_profile),
            "duration": "12_months",
            "adjustments": self._define_adjustments(),
        }

    def _define_path(self, profile: dict) -> list[dict[str, Any]]:
        """Определение пути обучения"""
        return [
            {"phase": 1, "name": "Базовый уровень", "duration": "3_months", "focus": "Основы проекта"},
            {"phase": 2, "name": "Продвинутый уровень", "duration": "4_months", "focus": "Глубокое погружение"},
            {"phase": 3, "name": "Экспертный уровень", "duration": "5_months", "focus": "Лидерство и инновации"},
        ]

    def _define_adjustments(self) -> list[dict[str, Any]]:
        """Определение корректировок"""
        return [
            {"adjustment": "Гибкий график", "reason": "Учет занятости разработчика"},
            {"adjustment": "Практические проекты", "reason": "Закрепление знаний"},
        ]
