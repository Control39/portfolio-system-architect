"""
Модуль саморефлексии для когнитивного агента
Развитие агентов через рефлексию и обучение
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class SelfReflector:
    """Саморефлексия агентов"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.project_path = autonomous_agent.project_path
        self.reflection_path = self.project_path / ".agents" / "reflections"

        # Создаем директории
        self.reflection_path.mkdir(parents=True, exist_ok=True)

    def reflect_on_actions(self, agent_name: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Рефлексия на действиях агента
        :param agent_name: Имя агента
        :param actions: Список действий
        :return: Результат рефлексии
        """
        reflection = {
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "actions_analyzed": len(actions),
            "effectiveness": self._calculate_effectiveness(actions),
            "patterns": self._identify_patterns(actions),
            "improvements": self._suggest_improvements(actions),
        }

        # С��храняем рефлексию
        self._save_reflection(reflection)

        return reflection

    def _calculate_effectiveness(self, actions: list[dict[str, Any]]) -> float:
        """Расчет эффективности действий"""
        if not actions:
            return 0.0

        successful = 0
        total = len(actions)

        for action in actions:
            if action.get("success"):
                successful += 1

        return round(successful / total * 100, 2) if total > 0 else 0.0

    def _identify_patterns(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        """Выявление паттернов"""
        patterns = {"success_patterns": [], "failure_patterns": [], "repeated_actions": [], "average_time": 0}

        # Анализируем действия
        success_actions = [a for a in actions if a.get("success")]
        failure_actions = [a for a in actions if not a.get("success")]

        if success_actions:
            patterns["success_patterns"] = self._extract_patterns(success_actions, "success")

        if failure_actions:
            patterns["failure_patterns"] = self._extract_patterns(failure_actions, "failure")

        # Повторяющиеся действия
        action_types = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            action_types[action_type] = action_types.get(action_type, 0) + 1

        patterns["repeated_actions"] = [
            {"type": k, "count": v} for k, v in sorted(action_types.items(), key=lambda x: x[1], reverse=True)
        ]

        # Среднее время выполнения
        times = [a.get("duration", 0) for a in actions]
        patterns["average_time"] = sum(times) / len(times) if times else 0

        return patterns

    def _extract_patterns(self, actions: list[dict[str, Any]], outcome: str) -> list[dict[str, Any]]:
        """Извлечение паттернов"""
        patterns = []

        # Анализируем типы действий
        type_counts = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            type_counts[action_type] = type_counts.get(action_type, 0) + 1

        for action_type, count in type_counts.items():
            patterns.append({"type": action_type, "count": count, "outcome": outcome})

        return patterns

    def _suggest_improvements(self, actions: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Предложение улучшений"""
        improvements = []

        # Анализируем неудачи
        failures = [a for a in actions if not a.get("success")]
        if len(failures) > len(actions) * 0.3:  # Если больше 30% неудач
            improvements.append(
                {
                    "area": "success_rate",
                    "recommendation": "Рассмотреть альтернативные подходы для неудачных действий",
                    "priority": "high",
                }
            )

        # Анализируем повторяющиеся действия
        action_types = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            action_types[action_type] = action_types.get(action_type, 0) + 1

        for action_type, count in action_types.items():
            if count > len(actions) * 0.5:  # Если более 50% действий одного типа
                improvements.append(
                    {
                        "area": f"action_diversity_{action_type}",
                        "recommendation": f"Рассмотреть разнообразие действий вместо повторения {action_type}",
                        "priority": "medium",
                    }
                )

        # Рекомендации по оптимизации времени
        times = [a.get("duration", 0) for a in actions]
        if times:
            avg_time = sum(times) / len(times)
            if avg_time > 60:  # Если среднее время больше 60 секунд
                improvements.append(
                    {
                        "area": "performance",
                        "recommendation": "Оптимизировать длительные действия",
                        "priority": "medium",
                    }
                )

        return improvements

    def update_strategies(self, reflection_results: dict[str, Any]) -> dict[str, Any]:
        """
        Обновление стратегий на основе рефлексии
        :param reflection_results: Результаты рефлексии
        :return: Обновленные стратегии
        """
        strategies = {"updated": [], "retained": [], "removed": []}

        # Обновляем стратегии на основе паттернов
        patterns = reflection_results.get("patterns", {})
        success_patterns = patterns.get("success_patterns", [])
        failure_patterns = patterns.get("failure_patterns", [])

        # Улучшаем успешные паттерны
        for pattern in success_patterns:
            strategy = self._enhance_strategy(pattern, "success")
            if strategy:
                strategies["updated"].append(strategy)

        # Исправляем неудачные паттерны
        for pattern in failure_patterns:
            strategy = self._improve_strategy(pattern, "failure")
            if strategy:
                strategies["updated"].append(strategy)

        # Сохраняем обновленные стратегии
        self._save_strategies(strategies)

        return strategies

    def _enhance_strategy(self, pattern: dict[str, Any], outcome: str) -> dict[str, Any]:
        """Улучшение стратегии"""
        return {
            "type": pattern.get("type"),
            "enhancement": f"Усилить успешный паттерн: {pattern.get('type')}",
            "expected_improvement": "10-20%",
            "priority": "medium",
        }

    def _improve_strategy(self, pattern: dict[str, Any], outcome: str) -> dict[str, Any]:
        """Улучшение стратегии для неудачных паттернов"""
        return {
            "type": pattern.get("type"),
            "improvement": f"Пересмотреть неудачный паттерн: {pattern.get('type')}",
            "alternative": "Попробовать альтернативный подход",
            "priority": "high",
        }

    def _save_strategies(self, strategies: dict[str, Any]) -> None:
        """Сохранение стратегий"""
        strategies_file = self.reflection_path / "strategies.json"

        with open(strategies_file, "w", encoding="utf-8") as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)

    def _save_reflection(self, reflection: dict[str, Any]) -> None:
        """Сохранение рефлексии"""
        reflection_file = self.reflection_path / f"reflection_{reflection['timestamp']}.json"

        with open(reflection_file, "w", encoding="utf-8") as f:
            json.dump(reflection, f, indent=2, ensure_ascii=False)

    def get_reflection_history(self, agent_name: str = None) -> list[dict[str, Any]]:
        """Получение истории рефлексий"""
        reflections = []

        for reflection_file in self.reflection_path.glob("*.json"):
            try:
                with open(reflection_file, encoding="utf-8") as f:
                    reflection = json.load(f)
                    if agent_name is None or reflection.get("agent_name") == agent_name:
                        reflections.append(reflection)
            except Exception:
                continue

        # Сортируем по времени (сначала новые)
        reflections.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return reflections

    def get_latest_reflection(self, agent_name: str) -> dict[str, Any]:
        """Получение последней рефлексии агента"""
        reflections = self.get_reflection_history(agent_name)
        return reflections[0] if reflections else {}

    def calculate_effectiveness(self, actions: list[dict[str, Any]]) -> float:
        """Расчет эффективности действий"""
        return self._calculate_effectiveness(actions)

    def extract_knowledge(self, reflection_results: dict[str, Any]) -> dict[str, Any]:
        """Извлечение знаний из рефлексии"""
        knowledge = {"patterns_discovered": [], "best_practices": [], "improvements_made": []}

        patterns = reflection_results.get("patterns", {})

        # Извлекаем паттерны
        for pattern in patterns.get("success_patterns", []):
            knowledge["patterns_discovered"].append(
                {
                    "type": pattern.get("type"),
                    "effectiveness": pattern.get("count"),
                    "recommendation": f"Продолжать использовать {pattern.get('type')} для успешных действий",
                }
            )

        # Извлекаем лучшие практики
        improvements = reflection_results.get("improvements", [])
        for improvement in improvements:
            knowledge["best_practices"].append(
                {
                    "area": improvement.get("area"),
                    "practice": improvement.get("recommendation"),
                    "priority": improvement.get("priority"),
                }
            )

        # Извлекаем сделанные улучшения
        strategies = reflection_results.get("strategies", {})
        for strategy in strategies.get("updated", []):
            knowledge["improvements_made"].append(
                {
                    "type": strategy.get("type"),
                    "improvement": strategy.get("enhancement") or strategy.get("improvement"),
                    "expected_benefit": strategy.get("expected_improvement"),
                }
            )

        return knowledge
