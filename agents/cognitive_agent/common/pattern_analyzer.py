"""
Модуль анализа паттернов в решениях агента
"""

import statistics
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from .base_logger import BaseLogger


class PatternAnalyzer:
    """
    Анализатор паттернов в решениях агента
    """

    def __init__(self, logger: BaseLogger | None = None):
        """
        Инициализировать анализатор паттернов

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or BaseLogger("PatternAnalyzer")
        self.decision_history = []

        self.logger.info("Анализатор паттернов инициализирован")

    def add_decision(
        self, context: dict[str, Any], decision: str, outcome: str, metadata: dict[str, Any] | None = None
    ):
        """
        Добавить решение в историю для анализа

        Args:
            context: Контекст принятия решения
            decision: Принятое решение
            outcome: Результат (success, failed, cancelled)
            metadata: Дополнительные метаданные
        """
        decision_record = {
            "context": context,
            "decision": decision,
            "outcome": outcome,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        self.decision_history.append(decision_record)

        # Ограничиваем историю 1000 записями
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

        self.logger.debug(f"Добавлено решение для анализа: {decision}, результат: {outcome}")

    def get_success_rate(self) -> float:
        """
        Получить общий success rate

        Returns:
            Success rate в диапазоне [0, 1]
        """
        if not self.decision_history:
            return 0.0

        success_count = sum(1 for d in self.decision_history if d["outcome"] == "success")
        return success_count / len(self.decision_history)

    def analyze_patterns(self) -> dict[str, Any]:
        """
        Проанализировать паттерны в исторических данных

        Returns:
            Словарь с результатами анализа паттернов
        """
        if len(self.decision_history) < 10:  # Минимум 10 записей для анализа
            self.logger.warning("Недостаточно данных для анализа паттернов", history_length=len(self.decision_history))
            return {
                "success_rate": self.get_success_rate(),
                "min_data_for_analysis": 10,
                "available_records": len(self.decision_history),
                "patterns": [],
                "recommendations": ["Накопите больше исторических данных для анализа паттернов"],
            }

        patterns = {
            "by_outcome": self._analyze_by_outcome(),
            "by_context_type": self._analyze_by_context_type(),
            "by_decision_type": self._analyze_by_decision_type(),
            "by_time": self._analyze_by_time(),
            "trends": self._analyze_trends(),
            "success_factors": self._identify_success_factors(),
        }

        recommendations = self._generate_recommendations(patterns)

        result = {
            "success_rate": self.get_success_rate(),
            "patterns": patterns,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        self.logger.info("Анализ паттернов завершен", success_rate=result["success_rate"])
        return result

    def _analyze_by_outcome(self) -> dict[str, Any]:
        """
        Анализ по результатам

        Returns:
            Результаты анализа по исходам
        """
        outcomes = [d["outcome"] for d in self.decision_history]
        outcome_counts = Counter(outcomes)
        total = len(outcomes)

        outcome_stats = {}
        for outcome, count in outcome_counts.items():
            outcome_stats[outcome] = {"count": count, "percentage": count / total * 100}

        return {
            "distribution": outcome_stats,
            "most_common_outcome": outcome_counts.most_common(1)[0][0] if outcome_counts else None,
        }

    def _analyze_by_context_type(self) -> dict[str, Any]:
        """
        Анализ по типам контекста

        Returns:
            Результаты анализа по типам контекста
        """
        context_types = defaultdict(list)

        for decision in self.decision_history:
            ctx = decision["context"]
            # Определяем тип контекста по ключевым признакам
            if "task_type" in ctx:
                ctx_type = ctx["task_type"]
            elif "project_path" in ctx:
                ctx_type = "project_analysis"
            elif "file_path" in ctx:
                ctx_type = "file_operation"
            else:
                ctx_type = "general"

            context_types[ctx_type].append(decision["outcome"])

        context_stats = {}
        for ctx_type, outcomes in context_types.items():
            success_count = sum(1 for outcome in outcomes if outcome == "success")
            context_stats[ctx_type] = {
                "total": len(outcomes),
                "success": success_count,
                "failure": len(outcomes) - success_count,
                "success_rate": success_count / len(outcomes) if outcomes else 0.0,
            }

        return context_stats

    def _analyze_by_decision_type(self) -> dict[str, Any]:
        """
        Анализ по типам решений

        Returns:
            Результаты анализа по типам решений
        """
        decision_types = defaultdict(list)

        for decision in self.decision_history:
            # Определяем тип решения по ключевым словам
            decision_text = decision["decision"].lower()
            if any(keyword in decision_text for keyword in ["refactor", "рефакторинг", "rename", "переименовать"]):
                decision_type = "refactoring"
            elif any(keyword in decision_text for keyword in ["fix", "bug", "баг", "ошибка"]):
                decision_type = "bug_fix"
            elif any(keyword in decision_text for keyword in ["add", "create", "новый", "добавить"]):
                decision_type = "feature_addition"
            elif any(keyword in decision_text for keyword in ["remove", "delete", "удалить"]):
                decision_type = "removal"
            else:
                decision_type = "other"

            decision_types[decision_type].append(decision["outcome"])

        decision_stats = {}
        for dec_type, outcomes in decision_types.items():
            success_count = sum(1 for outcome in outcomes if outcome == "success")
            decision_stats[dec_type] = {
                "total": len(outcomes),
                "success": success_count,
                "failure": len(outcomes) - success_count,
                "success_rate": success_count / len(outcomes) if outcomes else 0.0,
            }

        return decision_stats

    def _analyze_by_time(self) -> dict[str, Any]:
        """
        Анализ по времени

        Returns:
            Результаты анализа по временным характеристикам
        """
        timestamps = [datetime.fromisoformat(d["timestamp"]) for d in self.decision_history]
        outcomes = [d["outcome"] for d in self.decision_history]

        # Группировка по дням
        daily_stats = defaultdict(list)
        for ts, outcome in zip(timestamps, outcomes, strict=False):
            day_key = ts.strftime("%Y-%m-%d")
            daily_stats[day_key].append(outcome)

        daily_rates = {}
        for day, day_outcomes in daily_stats.items():
            success_count = sum(1 for outcome in day_outcomes if outcome == "success")
            daily_rates[day] = {
                "total": len(day_outcomes),
                "success_rate": success_count / len(day_outcomes) if day_outcomes else 0.0,
            }

        return {
            "daily_success_rates": daily_rates,
            "average_daily_decisions": statistics.mean([len(outcomes) for outcomes in daily_stats.values()])
            if daily_stats
            else 0,
        }

    def _analyze_trends(self) -> dict[str, Any]:
        """
        Анализ трендов

        Returns:
            Результаты анализа трендов
        """
        if len(self.decision_history) < 20:  # Минимум 20 записей для анализа трендов
            return {"trend_available": False, "message": "Недостаточно данных для анализа трендов"}

        # Берем последние 20% и первые 20% решений
        split_point = len(self.decision_history) // 5
        recent_decisions = self.decision_history[-split_point:]
        early_decisions = self.decision_history[:split_point]

        recent_success_rate = sum(1 for d in recent_decisions if d["outcome"] == "success") / len(recent_decisions)
        early_success_rate = sum(1 for d in early_decisions if d["outcome"] == "success") / len(early_decisions)

        trend_direction = (
            "improving"
            if recent_success_rate > early_success_rate
            else "declining"
            if recent_success_rate < early_success_rate
            else "stable"
        )

        return {
            "trend_available": True,
            "recent_success_rate": recent_success_rate,
            "early_success_rate": early_success_rate,
            "direction": trend_direction,
            "improvement_percentage": ((recent_success_rate - early_success_rate) / early_success_rate * 100)
            if early_success_rate > 0
            else 0,
        }

    def _identify_success_factors(self) -> list[dict[str, Any]]:
        """
        Идентифицировать факторы успеха

        Returns:
            Список факторов, влияющих на успех
        """
        success_decisions = [d for d in self.decision_history if d["outcome"] == "success"]
        failure_decisions = [d for d in self.decision_history if d["outcome"] != "success"]

        factors = []

        # Анализ по продолжительности задач
        if success_decisions and failure_decisions:
            avg_success_complexity = sum(len(str(d["context"])) for d in success_decisions) / len(success_decisions)
            avg_failure_complexity = sum(len(str(d["context"])) for d in failure_decisions) / len(failure_decisions)

            complexity_factor = {
                "factor": "complexity",
                "success_avg_complexity": avg_success_complexity,
                "failure_avg_complexity": avg_failure_complexity,
                "correlation": "positive" if avg_success_complexity > avg_failure_complexity else "negative",
            }
            factors.append(complexity_factor)

        return factors

    def _generate_recommendations(self, patterns: dict[str, Any]) -> list[str]:
        """
        Генерировать рекомендации на основе паттернов

        Args:
            patterns: Результаты анализа паттернов

        Returns:
            Список рекомендаций
        """
        recommendations = []

        # Рекомендации на основе общего success rate
        overall_success_rate = patterns["by_outcome"]["distribution"].get("success", {}).get("percentage", 0)
        if overall_success_rate < 70:
            recommendations.append("Общий success rate ниже 70%, рекомендуется пересмотреть стратегию принятия решений")
        elif overall_success_rate > 90:
            recommendations.append(
                "Высокий success rate, возможно, стоит расширить область применения успешных стратегий"
            )

        # Рекомендации на основе типов контекста
        for ctx_type, stats in patterns["by_context_type"].items():
            if stats["success_rate"] < 0.6 and stats["total"] > 5:
                recommendations.append(
                    f"Тип контекста '{ctx_type}' имеет низкий success rate ({stats['success_rate']:.2%}), требует улучшения подхода"
                )
            elif stats["success_rate"] > 0.9 and stats["total"] > 5:
                recommendations.append(
                    f"Тип контекста '{ctx_type}' показывает высокий success rate, рекомендуется изучить успешные практики"
                )

        # Рекомендации на основе типов решений
        for dec_type, stats in patterns["by_decision_type"].items():
            if stats["success_rate"] < 0.6 and stats["total"] > 5:
                recommendations.append(
                    f"Тип решений '{dec_type}' имеет низкий success rate ({stats['success_rate']:.2%}), требует пересмотра"
                )
            elif stats["success_rate"] > 0.9 and stats["total"] > 5:
                recommendations.append(
                    f"Тип решений '{dec_type}' показывает высокий success rate, рекомендуется стандартизировать подход"
                )

        # Рекомендации на основе трендов
        if patterns["trends"]["trend_available"]:
            if patterns["trends"]["direction"] == "improving":
                recommendations.append("Success rate улучшается, продолжайте текущую стратегию")
            elif patterns["trends"]["direction"] == "declining":
                recommendations.append("Success rate ухудшается, требуется анализ причин и корректировка стратегии")

        if not recommendations:
            recommendations.append(
                "На основе текущих данных не выявлено критических проблем, продолжайте текущую стратегию"
            )

        return recommendations

    def predict_success_probability(self, context: dict[str, Any], decision: str) -> float:
        """
        Предсказать вероятность успеха для нового решения

        Args:
            context: Контекст принятия решения
            decision: Решение для оценки

        Returns:
            Вероятность успеха (0.0 - 1.0)
        """
        # Если недостаточно данных, возвращаем общий success rate
        if len(self.decision_history) < 10:
            return self.get_success_rate()

        # Определяем типы контекста и решения
        ctx_type = self._classify_context(context)
        decision_type = self._classify_decision(decision)

        # Ищем исторические данные с похожими типами
        similar_decisions = [
            d
            for d in self.decision_history
            if self._classify_context(d["context"]) == ctx_type
            and self._classify_decision(d["decision"]) == decision_type
        ]

        if similar_decisions:
            success_count = sum(1 for d in similar_decisions if d["outcome"] == "success")
            return success_count / len(similar_decisions)
        else:
            # Если нет похожих решений, используем общий success rate для типа контекста
            ctx_stats = self._analyze_by_context_type()
            if ctx_type in ctx_stats:
                return ctx_stats[ctx_type]["success_rate"]
            else:
                return self.get_success_rate()

    def _classify_context(self, context: dict[str, Any]) -> str:
        """
        Классифицировать тип контекста

        Args:
            context: Контекст для классификации

        Returns:
            Тип контекста
        """
        if "task_type" in context:
            return context["task_type"]
        elif "project_path" in context:
            return "project_analysis"
        elif "file_path" in context:
            return "file_operation"
        else:
            return "general"

    def _classify_decision(self, decision: str) -> str:
        """
        Классифицировать тип решения

        Args:
            decision: Решение для классификации

        Returns:
            Тип решения
        """
        decision_lower = decision.lower()
        if any(keyword in decision_lower for keyword in ["refactor", "рефакторинг", "rename", "переименовать"]):
            return "refactoring"
        elif any(keyword in decision_lower for keyword in ["fix", "bug", "баг", "ошибка"]):
            return "bug_fix"
        elif any(keyword in decision_lower for keyword in ["add", "create", "новый", "добавить"]):
            return "feature_addition"
        elif any(keyword in decision_lower for keyword in ["remove", "delete", "удалить"]):
            return "removal"
        else:
            return "other"


class AdaptiveLearningSystem:
    """
    Адаптивная система обучения агента
    """

    def __init__(self, logger: BaseLogger | None = None):
        """
        Инициализировать адаптивную систему обучения

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or BaseLogger("AdaptiveLearningSystem")
        self.pattern_analyzer = PatternAnalyzer(logger=self.logger)
        self.learning_rate = 0.1  # Скорость адаптации (0.0 - 1.0)
        self.success_threshold = 0.7  # Порог успеха для положительной обратной связи

        self.logger.info("Адаптивная система обучения инициализирована")

    def learn_from_decision(
        self, context: dict[str, Any], decision: str, outcome: str, metadata: dict[str, Any] | None = None
    ):
        """
        Обучиться на принятом решении

        Args:
            context: Контекст принятия решения
            decision: Принятое решение
            outcome: Результат (success, failed, cancelled)
            metadata: Дополнательные метаданные
        """
        self.pattern_analyzer.add_decision(context, decision, outcome, metadata)

        self.logger.debug(f"Обучение на решении: {decision}, результат: {outcome}")

        # Если результат успешный, возможно адаптировать стратегию
        if outcome == "success":
            self._adapt_based_on_success(context, decision)

    def _adapt_based_on_success(self, context: dict[str, Any], decision: str):
        """
        Адаптировать стратегию на основе успешного решения

        Args:
            context: Контекст успешного решения
            decision: Успешное решение
        """
        # Здесь может быть реализована логика адаптации стратегии
        # Например, увеличение веса определенных подходов
        pass

    def get_advice_for_decision(self, context: dict[str, Any], decision: str) -> dict[str, Any]:
        """
        Получить совет по принятию решения на основе исторических данных

        Args:
            context: Контекст принятия решения
            decision: Решение для оценки

        Returns:
            Совет по решению
        """
        prediction = self.pattern_analyzer.predict_success_probability(context, decision)
        analysis = self.pattern_analyzer.analyze_patterns()

        advice = {
            "predicted_success_probability": prediction,
            "historical_context_similarity": self._find_similar_historical_contexts(context),
            "recommendations": analysis["recommendations"],
            "confidence_level": "high"
            if len(self.pattern_analyzer.decision_history) > 50
            else "medium"
            if len(self.pattern_analyzer.decision_history) > 20
            else "low",
        }

        self.logger.info(f"Совет для решения: {decision}, вероятность успеха: {prediction:.2%}")
        return advice

    def _find_similar_historical_contexts(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Найти похожие исторические контексты

        Args:
            context: Контекст для сравнения

        Returns:
            Список похожих исторических контекстов
        """
        similar_contexts = []
        current_ctx_type = self.pattern_analyzer._classify_context(context)

        for decision in self.pattern_analyzer.decision_history[-20:]:  # Последние 20 решений
            hist_ctx_type = self.pattern_analyzer._classify_context(decision["context"])
            if hist_ctx_type == current_ctx_type:
                similar_contexts.append(
                    {
                        "context": decision["context"],
                        "decision": decision["decision"],
                        "outcome": decision["outcome"],
                        "timestamp": decision["timestamp"],
                    }
                )

        return similar_contexts[:5]  # Возвращаем только 5 самых похожих

    def get_learning_metrics(self) -> dict[str, Any]:
        """
        Получить метрики обучения

        Returns:
            Метрики обучения системы
        """
        return {
            "total_decisions_learned": len(self.pattern_analyzer.decision_history),
            "current_success_rate": self.pattern_analyzer.get_success_rate(),
            "last_analysis": self.pattern_analyzer.analyze_patterns(),
            "learning_rate": self.learning_rate,
            "adaptation_enabled": True,
        }
