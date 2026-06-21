"""
Модуль метакогнитивного контроля для Cognitive Agent
"""

import json
import threading
from datetime import datetime
from typing import Any

from ..common.base_logger import BaseLogger


class MetacognitiveMonitor:
    """
    Монитор метакогнитивных процессов агента
    """

    def __init__(self, logger: BaseLogger | None = None):
        """
        Инициализировать монитор метакогнитивных процессов

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or BaseLogger("MetacognitiveMonitor")
        self.reasoning_trace = []  # След рассуждений
        self.confidence_levels = {}  # Уровни уверенности
        self.uncertainty_markers = {}  # Маркеры неуверенности
        self.quality_metrics = {}  # Метрики качества
        self.self_correction_history = []  # История самокоррекции
        self.lock = threading.RLock()

        self.logger.info("Монитор метакогнитивных процессов инициализирован")

    def start_reasoning_process(self, process_id: str, context: dict[str, Any]):
        """
        Начать отслеживание процесса рассуждения

        Args:
            process_id: ID процесса рассуждения
            context: Контекст процесса
        """
        with self.lock:
            reasoning_entry = {
                "process_id": process_id,
                "start_time": datetime.now().isoformat(),
                "context": context,
                "steps": [],
                "confidence_score": None,
                "quality_assessment": None,
            }

            self.reasoning_trace.append(reasoning_entry)

            self.logger.debug(f"Начат процесс рассуждения: {process_id}", context=context)

    def add_reasoning_step(self, process_id: str, step_data: dict[str, Any]):
        """
        Добавить шаг к процессу рассуждения

        Args:
            process_id: ID процесса рассуждения
            step_data: Данные шага
        """
        with self.lock:
            for entry in self.reasoning_trace:
                if entry["process_id"] == process_id:
                    step_entry = {
                        "step_number": len(entry["steps"]),
                        "timestamp": datetime.now().isoformat(),
                        "data": step_data,
                        "confidence": step_data.get("confidence", 0.5),
                        "uncertainty_markers": step_data.get("uncertainty_markers", []),
                        "quality_indicators": step_data.get("quality_indicators", {}),
                    }

                    entry["steps"].append(step_entry)

                    # Обновить маркеры неуверенности
                    if step_entry["uncertainty_markers"]:
                        self.uncertainty_markers[process_id] = self.uncertainty_markers.get(process_id, []) + [
                            step_entry["step_number"]
                        ]

                    self.logger.debug(
                        f"Добавлен шаг рассуждения: {process_id}:{step_entry['step_number']}", step_data=step_data
                    )
                    return

            self.logger.warning(f"Процесс рассуждения не найден: {process_id}")

    def assess_confidence(
        self, process_id: str, confidence_score: float, confidence_factors: dict[str, Any] | None = None
    ):
        """
        Оценить уровень уверенности в процессе рассуждения

        Args:
            process_id: ID процесса рассуждения
            confidence_score: Уровень уверенности (0.0 - 1.0)
            confidence_factors: Факторы, влияющие на уровень уверенности
        """
        with self.lock:
            for entry in self.reasoning_trace:
                if entry["process_id"] == process_id:
                    entry["confidence_score"] = confidence_score
                    entry["confidence_factors"] = confidence_factors or {}

                    self.confidence_levels[process_id] = {
                        "score": confidence_score,
                        "factors": confidence_factors or {},
                        "timestamp": datetime.now().isoformat(),
                    }

                    self.logger.info(
                        f"Уровень уверенности для {process_id}: {confidence_score:.2f}",
                        confidence_factors=confidence_factors,
                    )
                    return

            self.logger.warning(f"Процесс рассуждения не найден: {process_id}")

    def assess_quality(self, process_id: str, quality_metrics: dict[str, float]):
        """
        Оценить качество процесса рассуждения

        Args:
            process_id: ID процесса рассуждения
            quality_metrics: Метрики качества
        """
        with self.lock:
            for entry in self.reasoning_trace:
                if entry["process_id"] == process_id:
                    entry["quality_assessment"] = {
                        "metrics": quality_metrics,
                        "timestamp": datetime.now().isoformat(),
                        "overall_score": sum(quality_metrics.values()) / len(quality_metrics) if quality_metrics else 0,
                    }

                    self.quality_metrics[process_id] = entry["quality_assessment"]

                    self.logger.info(f"Качество процесса {process_id} оценено", quality_metrics=quality_metrics)
                    return

            self.logger.warning(f"Процесс рассуждения не найден: {process_id}")

    def check_consistency(self, process_id: str) -> tuple[bool, list[str]]:
        """
        Проверить логическую согласованность процесса рассуждения

        Args:
            process_id: ID процесса рассуждения

        Returns:
            Кортеж (согласован ли, список обнаруженных противоречий)
        """
        contradictions = []

        for entry in self.reasoning_trace:
            if entry["process_id"] == process_id:
                steps = entry["steps"]

                # Проверить противоречия между шагами
                for i in range(len(steps)):
                    for j in range(i + 1, len(steps)):
                        step_i = steps[i]["data"]
                        step_j = steps[j]["data"]

                        # Простая проверка на противоречия (в реальной системе будет сложнее)
                        if self._detect_contradiction(step_i, step_j):
                            contradictions.append(f"Противоречие между шагами {i} и {j}")

                break

        is_consistent = len(contradictions) == 0
        self.logger.debug(
            f"Проверка согласованности {process_id}: {'согласован' if is_consistent else 'есть противоречия'}",
            contradiction_count=len(contradictions),
        )

        return is_consistent, contradictions

    def _detect_contradiction(self, step1: dict[str, Any], step2: dict[str, Any]) -> bool:
        """
        Обнаружить противоречие между двумя шагами рассуждения

        Args:
            step1: Данные первого шага
            step2: Данные второго шага

        Returns:
            Есть ли противоречие
        """
        # Простая эвристика для обнаружения противоречий
        # В реальной системе будет использовать более сложные NLP/ML методы

        step1_str = json.dumps(step1, ensure_ascii=False, default=str)
        step2_str = json.dumps(step2, ensure_ascii=False, default=str)

        # Проверить наличие явных противоречий
        contradiction_keywords = ["не", "нет", "отрицание", "противоречит"]

        # Простая проверка на основе ключевых слов
        for keyword in contradiction_keywords:
            if keyword in step1_str.lower() and keyword in step2_str.lower():
                # Дополнительная проверка на контекст
                return True

        return False

    def trigger_self_correction(self, process_id: str, correction_reason: str) -> bool:
        """
        Запустить процесс самокоррекции

        Args:
            process_id: ID процесса рассуждения
            correction_reason: Причина коррекции

        Returns:
            Успешно ли запущена самокоррекция
        """
        with self.lock:
            # Проверить, нуждается ли процесс в коррекции
            confidence = self.confidence_levels.get(process_id, {}).get("score", 1.0)
            is_consistent, contradictions = self.check_consistency(process_id)

            if confidence < 0.6 or not is_consistent or process_id in self.uncertainty_markers:
                correction_entry = {
                    "process_id": process_id,
                    "timestamp": datetime.now().isoformat(),
                    "reason": correction_reason,
                    "original_confidence": confidence,
                    "contradictions_found": len(contradictions),
                    "uncertainty_markers_present": process_id in self.uncertainty_markers,
                }

                self.self_correction_history.append(correction_entry)

                self.logger.warning(f"Запущена самокоррекция для {process_id}", correction_entry=correction_entry)
                return True
            else:
                self.logger.debug(f"Самокоррекция не требуется для {process_id}", confidence=confidence)
                return False

    def get_reasoning_summary(self, process_id: str) -> dict[str, Any] | None:
        """
        Получить сводку по процессу рассуждения

        Args:
            process_id: ID процесса рассуждения

        Returns:
            Сводка по процессу или None, если процесс не найден
        """
        for entry in self.reasoning_trace:
            if entry["process_id"] == process_id:
                summary = {
                    "process_id": entry["process_id"],
                    "start_time": entry["start_time"],
                    "step_count": len(entry["steps"]),
                    "final_confidence": entry["confidence_score"],
                    "quality_assessment": entry["quality_assessment"],
                    "is_consistent": self.check_consistency(process_id)[0],
                    "contradictions_count": len(self.check_consistency(process_id)[1]),
                    "uncertainty_markers_count": len(self.uncertainty_markers.get(process_id, [])),
                }

                return summary

        return None

    def get_overall_assessment(self) -> dict[str, Any]:
        """
        Получить общую оценку метакогнитивных процессов

        Returns:
            Общая оценка
        """
        with self.lock:
            total_processes = len(self.reasoning_trace)
            processes_with_uncertainty = len([pid for pid in self.uncertainty_markers.keys()])
            processes_with_low_confidence = len(
                [pid for pid, data in self.confidence_levels.items() if data.get("score", 1.0) < 0.7]
            )
            self_corrections_performed = len(self.self_correction_history)

            assessment = {
                "total_reasoning_processes": total_processes,
                "processes_with_uncertainty": processes_with_uncertainty,
                "processes_with_low_confidence": processes_with_low_confidence,
                "self_corrections_performed": self_corrections_performed,
                "average_confidence": sum(data.get("score", 1.0) for data in self.confidence_levels.values())
                / max(len(self.confidence_levels), 1),
                "consistency_rate": self._calculate_consistency_rate(),
                "timestamp": datetime.now().isoformat(),
            }

            return assessment

    def _calculate_consistency_rate(self) -> float:
        """
        Рассчитать общий уровень согласованности

        Returns:
            Уровень согласованности (0.0 - 1.0)
        """
        consistent_count = 0
        total_count = 0

        for entry in self.reasoning_trace:
            is_consistent, _ = self.check_consistency(entry["process_id"])
            if is_consistent:
                consistent_count += 1
            total_count += 1

        return consistent_count / max(total_count, 1)


class MetacognitiveController:
    """
    Контроллер метакогнитивных процессов
    """

    def __init__(self, logger: BaseLogger | None = None):
        """
        Инициализировать контроллер метакогнитивных процессов

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or BaseLogger("MetacognitiveController")
        self.monitor = MetacognitiveMonitor(logger=self.logger)
        self.confidence_thresholds = {"low": 0.3, "medium": 0.7, "high": 0.9}
        self.quality_thresholds = {"min_acceptable": 0.5}

        self.logger.info("Контроллер метакогнитивных процессов инициализирован")

    def evaluate_reasoning_quality(self, process_id: str, reasoning_context: dict[str, Any]) -> dict[str, Any]:
        """
        Оценить качество процесса рассуждения

        Args:
            process_id: ID процесса рассуждения
            reasoning_context: Контекст рассуждения

        Returns:
            Оценка качества
        """
        # Начать процесс рассуждения
        self.monitor.start_reasoning_process(process_id, reasoning_context)

        # Рассчитать базовую оценку уверенности
        confidence_score = self._calculate_confidence_score(reasoning_context)

        # Оценить качество
        quality_metrics = self._assess_reasoning_quality(reasoning_context)

        # Записать оценки
        self.monitor.assess_confidence(process_id, confidence_score)
        self.monitor.assess_quality(process_id, quality_metrics)

        # Проверить необходимость самокоррекции
        correction_needed = self._requires_self_correction(process_id)

        result = {
            "process_id": process_id,
            "confidence_score": confidence_score,
            "quality_metrics": quality_metrics,
            "is_consistent": self.monitor.check_consistency(process_id)[0],
            "requires_correction": correction_needed,
            "assessment_timestamp": datetime.now().isoformat(),
        }

        self.logger.info(f"Оценка качества рассуждения {process_id} завершена", result=result)
        return result

    def _calculate_confidence_score(self, reasoning_context: dict[str, Any]) -> float:
        """
        Рассчитать уровень уверенности на основе контекста рассуждения

        Args:
            reasoning_context: Контекст рассуждения

        Returns:
            Уровень уверенности (0.0 - 1.0)
        """
        # Простая эвристика для расчета уверенности
        # В реальной системе будет использовать ML модели

        score = 0.5  # Базовый уровень уверенности

        # Повысить уверенность за счет наличия четких данных
        if "evidence" in reasoning_context:
            score += 0.2

        # Повысить уверенность за счет согласованности данных
        if "consistent_data" in reasoning_context:
            score += 0.15

        # Понизить уверенность при наличии неопределенности
        if "ambiguity" in reasoning_context:
            score -= 0.3

        # Понизить уверенность при наличии конфликта данных
        if "conflicting_info" in reasoning_context:
            score -= 0.4

        # Ограничить диапазон
        score = max(0.0, min(1.0, score))

        return score

    def _assess_reasoning_quality(self, reasoning_context: dict[str, Any]) -> dict[str, float]:
        """
        Оценить качество рассуждения

        Args:
            reasoning_context: Контекст рассуждения

        Returns:
            Метрики качества
        """
        quality_metrics = {
            "logical_coherence": 0.5,
            "evidence_strength": 0.5,
            "completeness": 0.5,
            "relevance": 0.5,
            "consistency": 0.5,
        }

        # Обновить метрики на основе контекста
        if "logical_steps" in reasoning_context:
            quality_metrics["logical_coherence"] = 0.8
        if "strong_evidence" in reasoning_context:
            quality_metrics["evidence_strength"] = 0.9
        if "complete_analysis" in reasoning_context:
            quality_metrics["completeness"] = 0.85
        if "relevant_context" in reasoning_context:
            quality_metrics["relevance"] = 0.9
        if "consistent_info" in reasoning_context:
            quality_metrics["consistency"] = 0.85

        return quality_metrics

    def _requires_self_correction(self, process_id: str) -> bool:
        """
        Определить, требуется ли самокоррекция

        Args:
            process_id: ID процесса рассуждения

        Returns:
            Требуется ли самокоррекция
        """
        # Получить текущую оценку
        summary = self.monitor.get_reasoning_summary(process_id)

        if not summary:
            return False

        # Проверить условия для самокоррекции
        confidence_ok = summary.get("final_confidence", 1.0) >= self.confidence_thresholds["medium"]
        consistent = summary.get("is_consistent", True)
        quality_ok = (
            summary.get("quality_assessment", {}).get("overall_score", 1.0) >= self.quality_thresholds["min_acceptable"]
        )

        requires_correction = not (confidence_ok and consistent and quality_ok)

        if requires_correction:
            reason_parts = []
            if not confidence_ok:
                reason_parts.append("низкая уверенность")
            if not consistent:
                reason_parts.append("найдены противоречия")
            if not quality_ok:
                reason_parts.append("низкое качество")

            reason = ", ".join(reason_parts)
            self.monitor.trigger_self_correction(process_id, reason)

        return requires_correction

    def integrate_with_reasoning_process(self, process_id: str, step_data: dict[str, Any]):
        """
        Интегрироваться с процессом рассуждения

        Args:
            process_id: ID процесса рассуждения
            step_data: Данные шага рассуждения
        """
        # Добавить шаг к процессу рассуждения
        self.monitor.add_reasoning_step(process_id, step_data)

        # Оценить качество текущего шага
        if "confidence" in step_data:
            self.monitor.assess_confidence(process_id, step_data["confidence"])

        # Проверить необходимость коррекции
        if self._requires_self_correction(process_id):
            self.logger.info(f"Обнаружена необходимость коррекции процесса {process_id}")
