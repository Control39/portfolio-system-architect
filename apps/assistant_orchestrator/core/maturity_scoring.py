"""
Maturity scoring for architecture assessment.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MaturityLevel(Enum):
    """Maturity levels with thresholds."""

    INITIAL = (0.0, "Начальный")
    BASIC = (2.0, "Базовый")
    INTERMEDIATE = (3.0, "Средний")
    ADVANCED = (4.0, "Продвинутый")
    OPTIMAL = (5.0, "Оптимальный")

    def __init__(self, threshold: float, label: str):
        self.threshold = threshold
        self.label = label

    @classmethod
    def from_score(cls, score: float) -> "MaturityLevel":
        """Get maturity level from score."""
        if score >= cls.OPTIMAL.threshold:
            return cls.OPTIMAL
        elif score >= cls.ADVANCED.threshold:
            return cls.ADVANCED
        elif score >= cls.INTERMEDIATE.threshold:
            return cls.INTERMEDIATE
        elif score >= cls.BASIC.threshold:
            return cls.BASIC
        else:
            return cls.INITIAL


@dataclass
class Recommendation:
    """Recommendation for improving maturity."""

    category: str
    title: str
    description: str
    potential_gain: float
    action: str
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "potential_gain": self.potential_gain,
            "action": self.action,
            "priority": self.priority,
        }


class MaturityScorerError(Exception):
    """Custom exception for maturity scoring errors."""

    pass


class MaturityScorer:
    """Calculate architecture maturity score (0-5)."""

    # Scoring weights (configurable)
    WEIGHTS = {
        "microservices": 1.0,
        "skills": 1.0,
        "documentation": 1.0,
        "git_activity": 1.0,
        "dependencies": 0.5,
        "production_readiness": 0.5,
    }

    def __init__(self, analysis_result: dict[str, Any]):
        """
        Initialize maturity scorer.

        Args:
            analysis_result: Dictionary with analysis results

        Raises:
            MaturityScorerError: If analysis_result is invalid
        """
        if not isinstance(analysis_result, dict):
            raise MaturityScorerError(f"Expected dict, got {type(analysis_result)}")

        self.analysis = analysis_result
        self._scores: dict[str, float] = {}

    def calculate_score(self) -> float:
        """Calculate overall maturity score (0-5)."""
        try:
            self._scores = {
                "microservices": self._score_microservices(),
                "skills": self._score_skills(),
                "documentation": self._score_documentation(),
                "git_activity": self._score_git_activity(),
                "dependencies": self._score_dependencies(),
                "production_readiness": self._score_production_readiness(),
            }

            total_score = sum(self._scores.values())
            max_score = sum(self.WEIGHTS.values())

            # Normalize to 0-5 scale
            normalized_score = (total_score / max_score) * 5.0

            logger.info(f"Maturity score calculated: {normalized_score:.2f}/5.0")
            logger.debug(f"Detailed scores: {self._scores}")

            return round(min(normalized_score, 5.0), 2)

        except Exception as e:
            logger.error(f"Error calculating maturity score: {e}")
            raise MaturityScorerError(f"Failed to calculate score: {e}")

    def get_maturity_level(self) -> MaturityLevel:
        """Get maturity level based on current score."""
        score = self.calculate_score()
        return MaturityLevel.from_score(score)

    def get_recommendations(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recommendations for improving maturity score.

        Args:
            limit: Maximum number of recommendations to return

        Returns:
            List of recommendations sorted by priority
        """
        try:
            recommendations = []

            # Microservices recommendations
            recs = self._get_microservices_recommendations()
            recommendations.extend(recs)

            # Deployment recommendations
            recs = self._get_deployment_recommendations()
            recommendations.extend(recs)

            # Documentation recommendations
            recs = self._get_documentation_recommendations()
            recommendations.extend(recs)

            # Testing recommendations
            recs = self._get_testing_recommendations()
            recommendations.extend(recs)

            # Activity recommendations
            recs = self._get_activity_recommendations()
            recommendations.extend(recs)

            # Skill recommendations
            recs = self._get_skill_recommendations()
            recommendations.extend(recs)

            # Sort by priority (higher gain = higher priority)
            recommendations.sort(key=lambda x: x.get("potential_gain", 0), reverse=True)

            # Assign priorities
            for i, rec in enumerate(recommendations[:limit], 1):
                rec["priority"] = i

            return recommendations[:limit]

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def _safe_get(self, path: str, default: Any = None) -> Any:
        """Safely get nested value using dot notation."""
        try:
            current = self.analysis
            for key in path.split("."):
                if isinstance(current, dict):
                    current = current.get(key, default)
                else:
                    return default
                if current is None:
                    return default
            return current
        except Exception:
            return default

    def _score_microservices(self) -> float:
        """Score based on microservices architecture (max 1.0)."""
        services = self._safe_get("microservices.services", [])

        if not services or not isinstance(services, list):
            return 0.0

        score = 0.0
        total = len(services)

        # Base score for having microservices
        if total >= 1:
            score += 0.5

        # Production ready services
        prod_ready = sum(1 for s in services if isinstance(s, dict) and s.get("is_production_ready", False))
        if prod_ready > 0:
            score += 0.5 * (prod_ready / total)

        # Services with tests
        with_tests = sum(1 for s in services if isinstance(s, dict) and s.get("has_tests", False))
        if with_tests > 0:
            score += 0.3 * (with_tests / total)

        # Docker support
        with_docker = sum(1 for s in services if isinstance(s, dict) and s.get("has_docker", False))
        if with_docker > 0:
            score += 0.2 * (with_docker / total)

        return min(score, self.WEIGHTS["microservices"])

    def _score_skills(self) -> float:
        """Score based on IT-Compass skill markers (max 1.0)."""
        skill_markers = self._safe_get("skill_markers", {})

        if not isinstance(skill_markers, dict):
            return 0.0

        skill_count = skill_markers.get("total_count", 0)
        categories = skill_markers.get("categories", [])
        categories_count = len(categories) if isinstance(categories, list) else 0

        if skill_count == 0:
            return 0.0

        score = 0.0

        # Skills volume scoring
        if skill_count >= 100:
            score += 1.0
        elif skill_count >= 50:
            score += 0.8
        elif skill_count >= 20:
            score += 0.5
        elif skill_count >= 10:
            score += 0.3
        elif skill_count >= 5:
            score += 0.2

        # Categories bonus
        if categories_count >= 20:
            score = min(score + 0.3, 1.0)
        elif categories_count >= 10:
            score = min(score + 0.2, 1.0)
        elif categories_count >= 5:
            score = min(score + 0.1, 1.0)

        return min(score, self.WEIGHTS["skills"])

    def _score_documentation(self) -> float:
        """Score based on architecture documentation (max 1.0)."""
        docs = self._safe_get("architecture_docs", [])

        if not docs or not isinstance(docs, list):
            return 0.0

        score = 0.0

        # Base score for having docs
        score += 0.5

        # Multiple docs
        if len(docs) >= 10:
            score += 0.3
        elif len(docs) >= 5:
            score += 0.2
        elif len(docs) >= 3:
            score += 0.1

        # Check for specific important docs
        doc_names = [str(d).lower() for d in docs]

        if any("architecture" in name for name in doc_names):
            score += 0.2
        if any("design" in name for name in doc_names):
            score += 0.2
        if any("adr" in name or "decision" in name for name in doc_names):
            score += 0.3
        if any("api" in name for name in doc_names):
            score += 0.1
        if any("deployment" in name for name in doc_names):
            score += 0.1

        return min(score, self.WEIGHTS["documentation"])

    def _score_git_activity(self) -> float:
        """Score based on Git repository activity (max 1.0)."""
        git_stats = self._safe_get("git_stats", {})

        if not isinstance(git_stats, dict):
            return 0.0

        total_commits = git_stats.get("total_commits", 0)
        recent_activity = git_stats.get("recent_activity_days", 0)
        contributors = git_stats.get("contributors", [])
        contributors_count = len(contributors) if isinstance(contributors, list) else 0

        score = 0.0

        # Commit volume (max 0.4)
        if total_commits >= 1000:
            score += 0.4
        elif total_commits >= 500:
            score += 0.3
        elif total_commits >= 200:
            score += 0.2
        elif total_commits >= 50:
            score += 0.1

        # Recent activity (max 0.3)
        if recent_activity >= 100:
            score += 0.3
        elif recent_activity >= 50:
            score += 0.25
        elif recent_activity >= 30:
            score += 0.2
        elif recent_activity >= 10:
            score += 0.1

        # Contributors (max 0.3)
        if contributors_count >= 20:
            score += 0.3
        elif contributors_count >= 10:
            score += 0.2
        elif contributors_count >= 5:
            score += 0.15
        elif contributors_count >= 3:
            score += 0.1
        elif contributors_count >= 1:
            score += 0.05

        return min(score, self.WEIGHTS["git_activity"])

    def _score_dependencies(self) -> float:
        """Score based on dependencies management (max 0.5)."""
        deps = self._safe_get("dependencies", [])
        has_docker_compose = self._safe_get("microservices.has_docker_compose", False)
        has_kubernetes = self._safe_get("microservices.has_kubernetes", False)

        score = 0.0

        # Dependencies documentation
        if deps and isinstance(deps, list):
            if len(deps) >= 10:
                score += 0.3
            elif len(deps) >= 5:
                score += 0.2
            elif len(deps) >= 1:
                score += 0.1

        # Orchestration tools
        if has_docker_compose:
            score += 0.3

        if has_kubernetes:
            score += 0.2

        return min(score, self.WEIGHTS["dependencies"])

    def _score_production_readiness(self) -> float:
        """Score based on overall production readiness (max 0.5)."""
        score = 0.0
        services = self._safe_get("microservices.services", [])

        if not services or not isinstance(services, list):
            return 0.0

        has_docker = any(isinstance(s, dict) and s.get("has_docker", False) for s in services)
        has_tests = any(isinstance(s, dict) and s.get("has_tests", False) for s in services)
        has_health_checks = any(isinstance(s, dict) and s.get("has_health_check", False) for s in services)

        # Docker + Tests = CI/CD ready
        if has_docker and has_tests:
            score += 0.3

        # Health checks = production ready
        if has_health_checks:
            score += 0.2

        # All services production ready
        prod_ready_count = sum(1 for s in services if isinstance(s, dict) and s.get("is_production_ready", False))
        if prod_ready_count == len(services) and len(services) > 0:
            score += 0.2

        return min(score, self.WEIGHTS["production_readiness"])

    def _get_microservices_recommendations(self) -> list[Recommendation]:
        """Get microservices-related recommendations."""
        recommendations = []
        services = self._safe_get("microservices.services", [])

        if not services or not isinstance(services, list):
            return recommendations

        prod_ready = sum(1 for s in services if isinstance(s, dict) and s.get("is_production_ready", False))
        prod_ready_percent = (prod_ready / len(services)) * 100 if services else 0

        if prod_ready_percent < 80:
            recommendations.append(
                Recommendation(
                    category="microservices",
                    title="Увеличить количество production-ready сервисов",
                    description=f"Только {prod_ready} из {len(services)} сервисов готовы к продакшену ({prod_ready_percent:.0f}%)",
                    potential_gain=0.5,
                    action="Добавить тесты, Dockerfile, health checks и мониторинг для оставшихся сервисов",
                )
            )

        # Check Docker usage
        with_docker = sum(1 for s in services if isinstance(s, dict) and s.get("has_docker", False))
        docker_percent = (with_docker / len(services)) * 100 if services else 0

        if docker_percent < 100 and with_docker < len(services):
            recommendations.append(
                Recommendation(
                    category="microservices",
                    title="Добавить Dockerfile для всех сервисов",
                    description=f"Только {with_docker} из {len(services)} сервисов имеют Dockerfile",
                    potential_gain=0.3,
                    action="Создать Dockerfile для каждого сервиса и настроить multi-stage сборку",
                )
            )

        return recommendations

    def _get_deployment_recommendations(self) -> list[Recommendation]:
        """Get deployment-related recommendations."""
        recommendations = []
        has_k8s = self._safe_get("microservices.has_kubernetes", False)
        has_compose = self._safe_get("microservices.has_docker_compose", False)

        if not has_k8s:
            recommendations.append(
                Recommendation(
                    category="deployment",
                    title="Внедрить Kubernetes для оркестрации",
                    description="Отсутствуют конфигурации Kubernetes, что усложняет масштабирование",
                    potential_gain=0.4,
                    action="Создать k8s/ директорию с Deployment, Service и ConfigMap манифестами",
                )
            )

        if not has_compose:
            recommendations.append(
                Recommendation(
                    category="deployment",
                    title="Добавить Docker Compose для локальной разработки",
                    description="Отсутствует docker-compose.yml для запуска всех сервисов",
                    potential_gain=0.2,
                    action="Создать docker-compose.yml с настройками всех сервисов и зависимостей",
                )
            )

        return recommendations

    def _get_documentation_recommendations(self) -> list[Recommendation]:
        """Get documentation-related recommendations."""
        recommendations = []
        docs = self._safe_get("architecture_docs", [])

        if not docs or not isinstance(docs, list):
            recommendations.append(
                Recommendation(
                    category="documentation",
                    title="Создать архитектурную документацию",
                    description="Полностью отсутствует архитектурная документация",
                    potential_gain=0.8,
                    action="Создать docs/architecture.md с описанием компонентов и их взаимодействия",
                )
            )
            return recommendations

        doc_names = [str(d).lower() for d in docs]
        has_adr = any("adr" in name or "decision" in name for name in doc_names)

        if not has_adr:
            recommendations.append(
                Recommendation(
                    category="documentation",
                    title="Начать вести Architecture Decision Records (ADR)",
                    description="Отсутствуют документированные архитектурные решения",
                    potential_gain=0.5,
                    action="Создать docs/adr/ директорию и добавить первый ADR с описанием ключевых решений",
                )
            )

        if len(docs) < 3:
            recommendations.append(
                Recommendation(
                    category="documentation",
                    title="Расширить документацию",
                    description=f"Всего {len(docs)} документов, рекомендуется иметь минимум 3",
                    potential_gain=0.3,
                    action="Добавить документацию по API, развертыванию и архитектуре",
                )
            )

        return recommendations

    def _get_testing_recommendations(self) -> list[Recommendation]:
        """Get testing-related recommendations."""
        recommendations = []
        services = self._safe_get("microservices.services", [])

        if not services or not isinstance(services, list):
            return recommendations

        with_tests = sum(1 for s in services if isinstance(s, dict) and s.get("has_tests", False))

        if with_tests == 0:
            recommendations.append(
                Recommendation(
                    category="testing",
                    title="Внедрить тестирование",
                    description="Ни один сервис не имеет тестов",
                    potential_gain=0.6,
                    action="Настроить pytest/unittest и добавить unit-тесты для критической логики",
                )
            )
        elif with_tests < len(services):
            recommendations.append(
                Recommendation(
                    category="testing",
                    title="Улучшить покрытие тестами",
                    description=f"Только {with_tests} из {len(services)} сервисов имеют тесты",
                    potential_gain=0.3,
                    action="Добавить тесты для сервисов без покрытия, настроить CI для запуска тестов",
                )
            )

        return recommendations

    def _get_activity_recommendations(self) -> list[Recommendation]:
        """Get activity-related recommendations."""
        recommendations = []
        git_stats = self._safe_get("git_stats", {})

        if not isinstance(git_stats, dict):
            return recommendations

        recent_commits = git_stats.get("recent_activity_days", 0)
        total_commits = git_stats.get("total_commits", 0)
        contributors = git_stats.get("contributors", [])
        contributors_count = len(contributors) if isinstance(contributors, list) else 0

        if recent_commits < 10:
            recommendations.append(
                Recommendation(
                    category="activity",
                    title="Увеличить активность разработки",
                    description=f"Только {recent_commits} коммитов за последние 30 дней",
                    potential_gain=0.3,
                    action="Планировать регулярные коммиты, настроить CI/CD и практиковать code reviews",
                )
            )

        if total_commits < 100:
            recommendations.append(
                Recommendation(
                    category="activity",
                    title="Нарастить кодобазу",
                    description=f"Всего {total_commits} коммитов в истории",
                    potential_gain=0.2,
                    action="Активнее разрабатывать функциональность и рефакторить существующий код",
                )
            )

        if contributors_count < 3:
            recommendations.append(
                Recommendation(
                    category="activity",
                    title="Расширить команду разработки",
                    description=f"Только {contributors_count} контрибьютора(ов)",
                    potential_gain=0.2,
                    action="Привлечь больше разработчиков к проекту, улучшить документацию для новичков",
                )
            )

        return recommendations

    def _get_skill_recommendations(self) -> list[Recommendation]:
        """Get skill-related recommendations."""
        recommendations = []
        skill_markers = self._safe_get("skill_markers", {})

        if not isinstance(skill_markers, dict):
            return recommendations

        skill_count = skill_markers.get("total_count", 0)
        categories = skill_markers.get("categories", [])
        categories_count = len(categories) if isinstance(categories, list) else 0

        if skill_count < 20:
            recommendations.append(
                Recommendation(
                    category="skills",
                    title="Расширить IT-Compass маркеры",
                    description=f"Найдено только {skill_count} маркеров, рекомендуется минимум 20",
                    potential_gain=0.4,
                    action="Провести аудит проекта и добавить недостающие маркеры по категориям",
                )
            )

        if categories_count < 5:
            recommendations.append(
                Recommendation(
                    category="skills",
                    title="Диверсифицировать категории навыков",
                    description=f"Только {categories_count} категорий, проект нуждается в более широком охвате",
                    potential_gain=0.2,
                    action="Добавить маркеры из разных категорий: бэкенд, фронтенд, DevOps, тестирование",
                )
            )

        return recommendations

    def get_detailed_breakdown(self) -> dict[str, Any]:
        """Get detailed score breakdown."""
        self.calculate_score()  # Ensure scores are calculated

        return {
            "total_score": self.calculate_score(),
            "maturity_level": self.get_maturity_level().label,
            "components": self._scores.copy(),
            "weights": self.WEIGHTS.copy(),
            "max_possible": sum(self.WEIGHTS.values()),
        }


# Convenience function
def calculate_maturity(analysis_result: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    """
    Quick maturity calculation.

    Args:
        analysis_result: Analysis results dictionary

    Returns:
        Tuple of (score, recommendations)
    """
    scorer = MaturityScorer(analysis_result)
    score = scorer.calculate_score()
    recommendations = scorer.get_recommendations()
    return score, recommendations
