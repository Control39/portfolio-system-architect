#!/usr/bin/env python3
"""
Explanation Engine module for cognitive agent

Движок объяснимости решений агента.

Ключевые принципы:
- Структурированные объяснения для каждого действия
- Обоснование, доказательства, оценка рисков, альтернативы
- Интеграция с TransparencyLogger для прозрачности
- История объяснений для аудита
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class ExplanationEngine:
    """
    Движок объяснимости решений агента

    Каждое объяснение содержит:
    - why: причина действия/решения
    - evidence: список доказательств (файлы, метрики, логи)
    - risk_assessment: оценка риска (low/medium/high/critical)
    - alternatives_considered: список рассмотренных альтернатив с причинами отказа
    - timestamp: время создания

    Использование:
        engine = ExplanationEngine(transparency_logger=logger)
        explanation = engine.explain_action({
            'name': 'modify_config',
            'file': 'config.yaml',
            'risk_level': 'high'
        })
    """

    def __init__(self, transparency_logger: Any = None, save_to_file: bool = False):
        """
        Инициализация ExplanationEngine.

        Args:
            transparency_logger: Экземпляр TransparencyLogger для логирования (опционально)
            save_to_file: Сохранять ли объяснения в файлы (по умолчанию False)
        """
        self.explanations: list[dict[str, Any]] = []
        self.transparency_logger = transparency_logger
        self.save_to_file = save_to_file
        self.explanations_dir = Path(".agent_data/explanations")
        if self.save_to_file:
            self.explanations_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "ExplanationEngine initialized",
            save_to_file=save_to_file,
            explanations_dir=str(self.explanations_dir) if save_to_file else "in-memory",
        )

    def explain_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        Объяснить действие агента.

        Args:
            action: Словарь с данными действия
                - name: Название действия
                - file: Путь к файлу (опционально)
                - risk_level: Уровень риска (опционально)
                - description: Описание (опционально)

        Returns:
            Структура объяснения с why, evidence, risk_assessment, alternatives_considered
        """
        explanation = {
            "id": str(uuid.uuid4()),
            "type": "action",
            "action": action,
            "why": self._generate_reason(action),
            "evidence": self._collect_evidence(action),
            "risk_assessment": self._assess_risk(action),
            "alternatives_considered": self._list_alternatives(action),
            "timestamp": datetime.now().isoformat(),
        }

        self.explanations.append(explanation)

        if self.save_to_file:
            self._save_explanation(explanation)

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": action.get("description", action.get("name", "Unknown action")),
                    "executed": f"Explanation generated: {explanation['id']}",
                    "status": "executed",
                    "confidence": 1.0,
                    "user_approval": False,
                }
            )

        logger.info(
            "Explanation generated for action",
            explanation_id=explanation["id"],
            action_name=action.get("name", "unknown"),
            risk_assessment=explanation["risk_assessment"],
        )

        return explanation

    def explain_decision(self, decision: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Объяснить решение агента.

        Args:
            decision: Принятое решение
            context: Контекст принятия решения

        Returns:
            Структура объяснения с why, evidence, risk_assessment, alternatives_considered
        """
        explanation = {
            "id": str(uuid.uuid4()),
            "type": "decision",
            "decision": decision,
            "context": context,
            "why": self._generate_decision_reason(decision, context),
            "evidence": self._collect_decision_evidence(context),
            "risk_assessment": self._assess_decision_risk(decision, context),
            "alternatives_considered": self._list_decision_alternatives(decision, context),
            "timestamp": datetime.now().isoformat(),
        }

        self.explanations.append(explanation)

        if self.save_to_file:
            self._save_explanation(explanation)

        logger.info(
            "Explanation generated for decision",
            explanation_id=explanation["id"],
            decision=decision,
            risk_assessment=explanation["risk_assessment"],
        )

        return explanation

    def get_explanation_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Получить историю объяснений.

        Args:
            limit: Максимальное количество объяснений

        Returns:
            Список последних объяснений
        """
        return self.explanations[-limit:]

    def clear_history(self) -> None:
        """Очистить историю объяснений."""
        self.explanations.clear()
        logger.info("Explanation history cleared")

    def get_stats(self) -> dict[str, Any]:
        """
        Получить статистику объяснений.

        Returns:
            Словарь со статистикой
        """
        total = len(self.explanations)
        actions = sum(1 for e in self.explanations if e["type"] == "action")
        decisions = sum(1 for e in self.explanations if e["type"] == "decision")
        high_risk = sum(1 for e in self.explanations if e.get("risk_assessment") in ["high", "critical"])

        return {
            "total_explanations": total,
            "actions": actions,
            "decisions": decisions,
            "high_risk": high_risk,
        }

    # Вспомогательные методы (заглушки для реализации)

    def _generate_reason(self, action: dict[str, Any]) -> str:
        """
        Сгенерировать причину действия.

        Args:
            action: Данные действия

        Returns:
            Описание причины
        """
        name = action.get("name", "unknown")
        description = action.get("description", "")
        file = action.get("file", "")

        if description:
            return description

        if file:
            return f"Action {name} was executed on file {file}"

        return f"Action {name} was executed based on current context"

    def _collect_evidence(self, action: dict[str, Any]) -> list[str]:
        """
        Собрать доказательства для действия.

        Args:
            action: Данные действия

        Returns:
            Список доказательств
        """
        evidence = ["Context analysis", "Historical data"]

        file = action.get("file")
        if file:
            evidence.append(f"File: {file}")

        risk = action.get("risk_level")
        if risk:
            evidence.append(f"Risk level: {risk}")

        return evidence

    def _assess_risk(self, action: dict[str, Any]) -> str:
        """
        Оценить риск действия.

        Args:
            action: Данные действия

        Returns:
            Уровень риска (low/medium/high/critical)
        """
        return action.get("risk_level", "medium")

    def _list_alternatives(self, action: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Список рассмотренных альтернатив.

        Args:
            action: Данные действия

        Returns:
            Список альтернатив с причинами отказа
        """
        alternatives = []

        # Альтернатива 1: Не делать ничего
        alternatives.append(
            {
                "alternative": "Do nothing",
                "reason_rejected": "Action required to complete task",
            }
        )

        # Альтернатива 2: Другой подход
        if action.get("file"):
            alternatives.append(
                {
                    "alternative": f"Manual modification of {action['file']}",
                    "reason_rejected": "AI automation more efficient",
                }
            )

        return alternatives

    def _generate_decision_reason(self, decision: str, context: dict[str, Any]) -> str:
        """
        Сгенерировать причину решения.

        Args:
            decision: Решение
            context: Контекст

        Returns:
            Описание причины
        """
        return f"Decision '{decision}' was made based on context analysis"

    def _collect_decision_evidence(self, context: dict[str, Any]) -> list[str]:
        """
        Собрать доказательства для решения.

        Args:
            context: Контекст

        Returns:
            Список доказательств
        """
        evidence = ["Context analysis", "Historical decisions", "Risk assessment"]

        if context.get("files_analyzed"):
            evidence.append(f"Files analyzed: {context['files_analyzed']}")

        if context.get("issues_found"):
            evidence.append(f"Issues found: {context['issues_found']}")

        return evidence

    def _assess_decision_risk(self, decision: str, context: dict[str, Any]) -> str:
        """
        Оценить риск решения.

        Args:
            decision: Решение
            context: Контекст

        Returns:
            Уровень риска
        """
        return context.get("risk_level", "medium")

    def _list_decision_alternatives(self, decision: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Список рассмотренных альтернатив для решения.

        Args:
            decision: Решение
            context: Контекст

        Returns:
            Список альтернатив
        """
        alternatives = []

        alternatives.append(
            {
                "alternative": "Alternative decision based on different criteria",
                "reason_rejected": "Less optimal for current context",
            }
        )

        alternatives.append(
            {
                "alternative": "Defer decision to human operator",
                "reason_rejected": "Risk level allows autonomous decision",
            }
        )

        return alternatives

    def _save_explanation(self, explanation: dict[str, Any]) -> None:
        """
        Сохранить объяснение в файл.

        Args:
            explanation: Данные объяснения
        """
        if not self.save_to_file:
            return

        file_path = self.explanations_dir / f"explanation_{explanation['id']}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(explanation, f, indent=2, ensure_ascii=False)

        logger.debug(
            "Explanation saved to file",
            explanation_id=explanation["id"],
            file_path=str(file_path),
        )

    def get_explanation_by_id(self, explanation_id: str) -> Optional[dict[str, Any]]:
        """
        Получить объяснение по ID.

        Args:
            explanation_id: ID объяснения

        Returns:
            Данные объяснения или None если не найдено
        """
        for explanation in self.explanations:
            if explanation["id"] == explanation_id:
                return explanation
        return None
