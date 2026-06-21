"""
Модуль принятия решений для когнитивного агента
Ведение реестра решений и логики принятия
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class DecisionRegistry:
    """Реестр решений"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.project_path = autonomous_agent.project_path
        self.decisions_path = self.project_path / ".agents" / "decisions"

        # Создаем директории
        self.decisions_path.mkdir(parents=True, exist_ok=True)

        # Загружаем существующие решения
        self.decisions = self._load_decisions()

    def _load_decisions(self) -> list[dict[str, Any]]:
        """Загрузка существующих решений"""
        decisions = []

        for decision_file in self.decisions_path.glob("*.json"):
            try:
                with open(decision_file, encoding="utf-8") as f:
                    decision = json.load(f)
                    decisions.append(decision)
            except Exception:
                continue

        return decisions

    def record_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Запись решения в реестр
        :param decision: Решение
        :return: Результат записи
        """
        # Валидация решения
        validated = self._validate_decision(decision)

        if not validated["valid"]:
            return {"recorded": False, "errors": validated["errors"]}

        # Генерация ID если не указан
        decision_id = decision.get("id", f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        decision["id"] = decision_id
        decision["timestamp"] = datetime.now().isoformat()

        # Сохраняем решение
        decision_path = self.decisions_path / f"{decision_id}.json"

        with open(decision_path, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2, ensure_ascii=False)

        # Добавляем в реестр
        self.decisions.append(decision)

        return {"recorded": True, "decision_id": decision_id, "timestamp": decision["timestamp"]}

    def _validate_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """Валидация решения"""
        errors = []

        required_fields = ["title", "context", "solution"]
        for field in required_fields:
            if field not in decision:
                errors.append(f"Отсутствует обязательное поле: {field}")

        return {"valid": len(errors) == 0, "errors": errors}

    def make_decision(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Принятие решения на основе контекста
        :param context: Контекст
        :return: Решение
        """
        # Анализ контекста
        analysis = self._analyze_context(context)

        # Генерация решения
        decision = self._generate_decision(analysis, context)

        # Регистрация решения
        result = self.record_decision(decision)

        return {
            "decision": decision,
            "rationale": analysis["rationale"],
            "alternatives": analysis["alternatives"],
            "registered": result,
        }

    def _analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Анализ контекста"""
        return {
            "problem": context.get("problem", "Неизвестная проблема"),
            "constraints": context.get("constraints", []),
            "stakeholders": context.get("stakeholders", []),
            "rationale": self._generate_rationale(context),
            "alternatives": self._generate_alternatives(context),
        }

    def _generate_rationale(self, context: dict[str, Any]) -> str:
        """Генерация обоснования"""
        problem = context.get("problem", "Неизвестная проблема")
        constraints = context.get("constraints", [])

        rationale = f"Проблема: {problem}. "
        if constraints:
            rationale += f"Ограничения: {', '.join(constraints)}. "

        rationale += "Решение основано на анализе доступных вариантов и текущих ограничений проекта."

        return rationale

    def _generate_alternatives(self, context: dict[str, Any]) -> list[dict[str, str]]:
        """Генерация альтернатив"""
        return [
            {
                "alternative": "Стандартное решение",
                "pros": ["Простота", "Поддержка"],
                "cons": ["Ограниченная гибкость"],
            },
            {
                "alternative": "Кастомное решение",
                "pros": ["Гибкость", "Оптимизация"],
                "cons": ["Сложность", "Технический долг"],
            },
        ]

    def _generate_decision(self, analysis: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Генерация решения"""
        return {
            "title": context.get("title", "Решение"),
            "id": f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "context": context.get("problem", "Неизвестная проблема"),
            "solution": "Принято автоматическое решение на основе анализа контекста",
            "alternatives": analysis["alternatives"],
            "rationale": analysis["rationale"],
            "status": "approved",
            "timestamp": datetime.now().isoformat(),
        }

    def get_decision_history(self) -> list[dict[str, Any]]:
        """Получение истории решений"""
        return self.decisions

    def get_decision_by_id(self, decision_id: str) -> dict[str, Any]:
        """Получение решения по ID"""
        for decision in self.decisions:
            if decision.get("id") == decision_id:
                return decision
        return {"error": f"Решение {decision_id} не найдено"}

    def validate_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Валидация решения
        :param decision: Решение
        :return: Результат валидации
        """
        validation = self._validate_decision(decision)

        if not validation["valid"]:
            return {"valid": False, "errors": validation["errors"]}

        # Дополнительная валидация на основе истории
        consistency_check = self._check_consistency(decision)

        return {
            "valid": True,
            "consistency": consistency_check["consistent"],
            "conflicts": consistency_check["conflicts"],
            "recommendations": consistency_check["recommendations"],
        }

    def _check_consistency(self, decision: dict[str, Any]) -> dict[str, Any]:
        """Проверка согласованности с историей"""
        conflicts = []
        recommendations = []

        # Проверка на противоречия с существующими решениями
        for existing_decision in self.decisions:
            if existing_decision.get("id") == decision.get("id"):
                continue

            # Проверка на конфликты
            if self._conflicts_with(existing_decision, decision):
                conflicts.append(
                    {
                        "existing_decision": existing_decision.get("id"),
                        "conflict_type": "contradiction",
                        "description": "Новое решение противоречит существующему",
                    }
                )

        return {"consistent": len(conflicts) == 0, "conflicts": conflicts, "recommendations": recommendations}

    def _conflicts_with(self, existing: dict[str, Any], new: dict[str, Any]) -> bool:
        """Проверка конфликта с существующим решением"""
        # Простая проверка на конфликт по заголовкам
        existing_title = existing.get("title", "").lower()
        new_title = new.get("title", "").lower()

        if existing_title and new_title and existing_title != new_title:
            # Проверяем контекст
            existing_context = existing.get("context", "").lower()
            new_context = new.get("context", "").lower()

            if existing_context and new_context:
                # Если контексты похожи, но решения разные - конфликт
                if self._similarity_score(existing_context, new_context) > 0.7:
                    return True

        return False

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Расчет коэффициента схожести текстов"""
        # Упрощенная реализация
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def get_decisions_by_category(self, category: str) -> list[dict[str, Any]]:
        """Получение решений по категории"""
        return [d for d in self.decisions if d.get("category") == category]

    def get_decisions_by_status(self, status: str) -> list[dict[str, Any]]:
        """Получение решений по статусу"""
        return [d for d in self.decisions if d.get("status") == status]
