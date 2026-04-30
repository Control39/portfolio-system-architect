#!/usr/bin/env python3
"""
Система самообучения для Cognitive Automation Agent.

Собирает метрики выполнения задач, анализирует эффективность,
корректирует алгоритмы и непрерывно улучшает работу агента
на основе накопленного опыта.
"""

import hashlib
import json
import logging
import pickle
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TaskMetrics:
    """Метрики выполнения задачи."""

    task_id: str
    task_type: str
    priority: float
    duration: float  # в секундах
    success: bool
    error_message: Optional[str] = None
    resources_used: Dict[str, float] = None  # CPU, память, время
    quality_score: float = 0.0  # оценка качества выполнения (0-1)
    learning_points: List[str] = None  # ключевые выводы для обучения


@dataclass
class AgentMetrics:
    """Агрегированные метрики агента за период."""

    period_start: datetime
    period_end: datetime
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    avg_duration: float
    avg_priority: float
    avg_quality: float
    efficiency_score: float  # общая оценка эффективности (0-1)
    improvement_suggestions: List[str]


class LearningSystem:
    """Система самообучения агента."""

    def __init__(self, config_path: str = ".agents/config/learning.yaml"):
        """Инициализация системы самообучения."""
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Директории для данных
        self.data_dir = Path(".agents/data/learning")
        self.metrics_dir = self.data_dir / "metrics"
        self.models_dir = self.data_dir / "models"
        self.reports_dir = self.data_dir / "reports"

        # Создание директорий
        for directory in [
            self.data_dir,
            self.metrics_dir,
            self.models_dir,
            self.reports_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Загрузка исторических данных
        self.historical_metrics = self._load_historical_metrics()
        self.learning_models = self._load_learning_models()

        logger.info(f"Система самообучения инициализирована. Конфиг: {config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации системы самообучения."""
        default_config = {
            "learning": {
                "enabled": True,
                "metrics_collection_interval": 300,  # секунд
                "analysis_interval": 3600,  # секунд
                "model_retraining_interval": 86400,  # секунд (24 часа)
                "min_samples_for_learning": 100,
                "improvement_threshold": 0.1,  # порог для внесения изменений
                "metrics_to_track": [
                    "task_duration",
                    "task_success_rate",
                    "resource_usage",
                    "quality_score",
                    "priority_accuracy",
                ],
            },
            "models": {
                "priority_predictor": {
                    "enabled": True,
                    "algorithm": "random_forest",
                    "features": ["task_type", "complexity", "urgency", "dependencies"],
                },
                "duration_predictor": {
                    "enabled": True,
                    "algorithm": "linear_regression",
                    "features": ["task_type", "complexity", "resources"],
                },
                "quality_predictor": {
                    "enabled": True,
                    "algorithm": "gradient_boosting",
                    "features": ["task_type", "executor_skill", "resources"],
                },
            },
            "improvements": {
                "auto_apply": False,
                "require_approval": True,
                "backup_before_changes": True,
                "rollback_on_failure": True,
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = yaml.safe_load(f) or {}
                # Объединение с конфигом по умолчанию
                merged_config = self._deep_merge(default_config, loaded_config)
                logger.info(f"Конфигурация загружена из {self.config_path}")
                return merged_config
            except Exception as e:
                logger.error(
                    f"Ошибка загрузки конфигурации: {e}. Используется конфиг по умолчанию."
                )
                return default_config
        else:
            logger.warning(
                f"Конфигурационный файл не найден: {self.config_path}. Используется конфиг по умолчанию."
            )
            return default_config

    def _deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """Рекурсивное объединение словарей."""
        result = dict1.copy()
        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load_historical_metrics(self) -> List[Dict[str, Any]]:
        """Загрузка исторических метрик из файлов."""
        historical_data = []
        metrics_files = list(self.metrics_dir.glob("metrics_*.json"))

        for metrics_file in metrics_files:
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    historical_data.extend(data)
            except Exception as e:
                logger.error(f"Ошибка загрузки метрик из {metrics_file}: {e}")

        logger.info(f"Загружено {len(historical_data)} исторических записей метрик")
        return historical_data

    def _load_learning_models(self) -> Dict[str, Any]:
        """Загрузка обученных моделей машинного обучения."""
        models = {}
        model_files = list(self.models_dir.glob("*.pkl"))

        for model_file in model_files:
            try:
                with open(model_file, "rb") as f:
                    model = pickle.load(f)
                    model_name = model_file.stem
                    models[model_name] = model
                    logger.info(f"Модель загружена: {model_name}")
            except Exception as e:
                logger.error(f"Ошибка загрузки модели из {model_file}: {e}")

        return models

    def collect_metrics(self, task_metrics: TaskMetrics) -> None:
        """Сбор метрик выполнения задачи."""
        try:
            # Сохранение метрик задачи
            metrics_file = self.metrics_dir / f"task_{task_metrics.task_id}.json"
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(asdict(task_metrics), f, indent=2, default=str)

            # Добавление в исторические данные
            self.historical_metrics.append(asdict(task_metrics))

            # Периодическое сохранение агрегированных данных
            if len(self.historical_metrics) % 10 == 0:
                self._save_aggregated_metrics()

            logger.debug(f"Метрики задачи {task_metrics.task_id} сохранены")

        except Exception as e:
            logger.error(f"Ошибка сбора метрик: {e}")

    def _save_aggregated_metrics(self) -> None:
        """Сохранение агрегированных метрик."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            aggregated_file = self.metrics_dir / f"aggregated_{timestamp}.json"

            # Агрегация метрик за последние 24 часа
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_metrics = [
                m
                for m in self.historical_metrics
                if datetime.fromisoformat(
                    m.get("timestamp", datetime.now().isoformat())
                )
                > cutoff_time
            ]

            if recent_metrics:
                with open(aggregated_file, "w", encoding="utf-8") as f:
                    json.dump(recent_metrics, f, indent=2, default=str)

                logger.info(f"Агрегированные метрики сохранены: {aggregated_file}")

        except Exception as e:
            logger.error(f"Ошибка сохранения агрегированных метрик: {e}")

    def analyze_metrics(self, period_hours: int = 24) -> AgentMetrics:
        """Анализ метрик за указанный период."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=period_hours)

            # Фильтрация метрик за период
            period_metrics = [
                m
                for m in self.historical_metrics
                if datetime.fromisoformat(
                    m.get("timestamp", datetime.now().isoformat())
                )
                > cutoff_time
            ]

            if not period_metrics:
                logger.warning(f"Нет метрик за последние {period_hours} часов")
                return self._create_empty_metrics(period_hours)

            # Расчет агрегированных метрик
            total_tasks = len(period_metrics)
            successful_tasks = sum(1 for m in period_metrics if m.get("success", False))
            failed_tasks = total_tasks - successful_tasks

            durations = [m.get("duration", 0) for m in period_metrics]
            priorities = [m.get("priority", 0) for m in period_metrics]
            quality_scores = [m.get("quality_score", 0) for m in period_metrics]

            avg_duration = np.mean(durations) if durations else 0
            avg_priority = np.mean(priorities) if priorities else 0
            avg_quality = np.mean(quality_scores) if quality_scores else 0

            # Расчет эффективности
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
            efficiency_score = (
                success_rate * 0.4
                + avg_quality * 0.3
                + (1 - min(avg_duration / 3600, 1)) * 0.3
            )  # нормализованная оценка

            # Генерация предложений по улучшению
            improvement_suggestions = self._generate_improvement_suggestions(
                period_metrics, success_rate, avg_duration, avg_quality
            )

            metrics = AgentMetrics(
                period_start=cutoff_time,
                period_end=datetime.now(),
                total_tasks=total_tasks,
                successful_tasks=successful_tasks,
                failed_tasks=failed_tasks,
                avg_duration=avg_duration,
                avg_priority=avg_priority,
                avg_quality=avg_quality,
                efficiency_score=efficiency_score,
                improvement_suggestions=improvement_suggestions,
            )

            logger.info(
                f"Анализ метрик завершен. Эффективность: {efficiency_score:.2f}"
            )
            return metrics

        except Exception as e:
            logger.error(f"Ошибка анализа метрик: {e}")
            return self._create_empty_metrics(period_hours)

    def _create_empty_metrics(self, period_hours: int) -> AgentMetrics:
        """Создание пустых метрик при отсутствии данных."""
        return AgentMetrics(
            period_start=datetime.now() - timedelta(hours=period_hours),
            period_end=datetime.now(),
            total_tasks=0,
            successful_tasks=0,
            failed_tasks=0,
            avg_duration=0,
            avg_priority=0,
            avg_quality=0,
            efficiency_score=0,
            improvement_suggestions=["Нет данных для анализа"],
        )

    def _generate_improvement_suggestions(
        self,
        metrics: List[Dict[str, Any]],
        success_rate: float,
        avg_duration: float,
        avg_quality: float,
    ) -> List[str]:
        """Генерация предложений по улучшению на основе метрик."""
        suggestions = []

        # Анализ успешности задач
        if success_rate < 0.8:
            suggestions.append(
                "Увеличить успешность выполнения задач: проанализировать причины неудач"
            )

        # Анализ длительности
        if avg_duration > 3600:  # более 1 часа в среднем
            suggestions.append(
                "Оптимизировать время выполнения задач: выявить и устранить узкие места"
            )

        # Анализ качества
        if avg_quality < 0.7:
            suggestions.append(
                "Повысить качество выполнения: улучшить алгоритмы или добавить проверки"
            )

        # Анализ типов задач с низкой успешностью
        task_types = {}
        for metric in metrics:
            task_type = metric.get("task_type", "unknown")
            success = metric.get("success", False)
            task_types.setdefault(task_type, {"total": 0, "success": 0})
            task_types[task_type]["total"] += 1
            if success:
                task_types[task_type]["success"] += 1

        for task_type, stats in task_types.items():
            if stats["total"] >= 5:  # только для типов с достаточной статистикой
                type_success_rate = stats["success"] / stats["total"]
                if type_success_rate < 0.6:
                    suggestions.append(
                        f"Улучшить выполнение задач типа '{task_type}': текущая успешность {type_success_rate:.1%}"
                    )

        # Добавление общих рекомендаций
        if len(metrics) < 50:
            suggestions.append("Собрать больше данных для более точного анализа")

        if not suggestions:
            suggestions.append("Показатели в норме. Продолжать мониторинг")

        return suggestions

    def train_models(self) -> Dict[str, Any]:
        """Обучение моделей машинного обучения на исторических данных."""
        training_results = {}

        try:
            if (
                len(self.historical_metrics)
                < self.config["learning"]["min_samples_for_learning"]
            ):
                logger.warning(
                    f"Недостаточно данных для обучения. Требуется: {self.config['learning']['min_samples_for_learning']}, есть: {len(self.historical_metrics)}"
                )
                return {"status": "insufficient_data", "models_trained": 0}

            # Преобразование данных в DataFrame
            df = pd.DataFrame(self.historical_metrics)

            # Обучение моделей (заглушки - в реальной реализации здесь будет ML)
            models_to_train = self.config["models"]

            for model_name, model_config in models_to_train.items():
                if model_config.get("enabled", False):
                    try:
                        # Здесь будет реальное обучение модели
                        # Пока создаем заглушку
                        model = {
                            "name": model_name,
                            "algorithm": model_config.get("algorithm", "unknown"),
                            "trained_at": datetime.now().isoformat(),
                            "performance": 0.85,  # заглушка
                            "features_used": model_config.get("features", []),
                        }

                        # Сохранение модели
                        model_file = self.models_dir / f"{model_name}.pkl"
                        with open(model_file, "wb") as f:
                            pickle.dump(model, f)

                        self.learning_models[model_name] = model
                        training_results[model_name] = model

                        logger.info(f"Модель обучена: {model_name}")

                    except Exception as e:
                        logger.error(f"Ошибка обучения модели {model_name}: {e}")
                        training_results[model_name] = {"error": str(e)}

            # Сохранение результатов обучения
            results_file = (
                self.reports_dir
                / f"training_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(training_results, f, indent=2, default=str)

            logger.info(
                f"Обучение моделей завершено. Обучено моделей: {len(training_results)}"
            )
            return {
                "status": "success",
                "models_trained": len(training_results),
                "results": training_results,
            }

        except Exception as e:
            logger.error(f"Ошибка обучения моделей: {e}")
            return {"status": "error", "error": str(e)}

    def generate_improvements(
        self, agent_metrics: AgentMetrics
    ) -> List[Dict[str, Any]]:
        """Генерация конкретных улучшений на основе анализа метрик."""
        improvements = []

        # Анализ эффективности
        if agent_metrics.efficiency_score < 0.7:
            improvements.append(
                {
                    "id": f"improve_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "efficiency",
                    "title": "Повышение общей эффективности агента",
                    "description": f"Текущая эффективность: {agent_metrics.efficiency_score:.2f}. Необходимо проанализировать узкие места.",
                    "priority": "high",
                    "estimated_effort": "medium",
                    "actions": [
                        "Провести детальный анализ неудачных задач",
                        "Оптимизировать алгоритмы планирования",
                        "Улучшить распределение ресурсов",
                    ],
                }
            )

        # Анализ успешности
        if agent_metrics.successful_tasks > 0:
            success_rate = agent_metrics.successful_tasks / agent_metrics.total_tasks
            if success_rate < 0.8:
                improvements.append(
                    {
                        "id": f"success_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                        "type": "success_rate",
                        "title": "Увеличение успешности выполнения задач",
                        "description": f"Текущая успешность: {success_rate:.1%}. Много неудачных выполнений.",
                        "priority": "high",
                        "estimated_effort": "high",
                        "actions": [
                            "Добавить обработку исключений в критические компоненты",
                            "Улучшить валидацию входных данных",
                            "Реализовать механизм повторных попыток",
                        ],
                    }
                )

        # Анализ качества
        if agent_metrics.avg_quality < 0.7:
            improvements.append(
                {
                    "id": f"quality_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
                    "type": "quality",
                    "title": "Повышение качества выполнения задач",
                    "description": f"Среднее качество: {agent_metrics.avg_quality:.2f}. Необходимо улучшить результаты.",
                    "priority": "medium",
                    "estimated_effort": "medium",
                    "actions": [
                        "Добавить дополнительные проверки качества",
                        "Улучшить алгоритмы оценки результатов",
                        "Внедрить систему обратной связи",
                    ],
                }
            )

        # Добавление предложений из анализа метрик
        for suggestion in agent_metrics.improvement_suggestions:
            if (
                "улучшить" in suggestion.lower()
                or "оптимизировать" in suggestion.lower()
            ):
                improvements.append(
                    {
                        "id": f"sugg_{hashlib.md5(suggestion.encode()).hexdigest()[:8]}",
                        "type": "suggestion",
                        "title": suggestion,
                        "description": "Предложение по улучшению на основе анализа метрик",
                        "priority": "low",
                        "estimated_effort": "low",
                        "actions": ["Проанализировать и реализовать предложение"],
                    }
                )

        return improvements

    def apply_improvements(self, improvements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Применение улучшений к системе."""
        results = {"total": len(improvements), "applied": 0, "failed": 0, "details": []}

        for improvement in improvements:
            try:
                # В реальной реализации здесь будет применение конкретных улучшений
                # Пока только логируем
                logger.info(f"Применение улучшения: {improvement['title']}")

                # Сохранение информации об улучшении
                improvement_file = (
                    self.reports_dir / f"improvement_{improvement['id']}.json"
                )
                with open(improvement_file, "w", encoding="utf-8") as f:
                    json.dump(improvement, f, indent=2, default=str)

                results["applied"] += 1
                results["details"].append(
                    {
                        "id": improvement["id"],
                        "status": "applied",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Ошибка применения улучшения {improvement['id']}: {e}")
                results["failed"] += 1
                results["details"].append(
                    {
                        "id": improvement["id"],
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Сохранение отчета о применении улучшений
        report_file = (
            self.reports_dir
            / f"improvements_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(
            f"Улучшения применены: {results['applied']} успешно, {results['failed']} с ошибками"
        )
        return results

    def generate_report(self, period_hours: int = 24) -> Path:
        """Генерация отчета о работе системы самообучения."""
        try:
            # Анализ метрик
            agent_metrics = self.analyze_metrics(period_hours)

            # Генерация улучшений
            improvements = self.generate_improvements(agent_metrics)

            # Статус моделей
            models_status = {
                "total_models": len(self.learning_models),
                "models": list(self.learning_models.keys()),
                "historical_data_points": len(self.historical_metrics),
            }

            # Создание отчета
            report = {
                "generated_at": datetime.now().isoformat(),
                "period_hours": period_hours,
                "agent_metrics": asdict(agent_metrics),
                "improvements": improvements,
                "models_status": models_status,
                "config_summary": {
                    "learning_enabled": self.config["learning"]["enabled"],
                    "metrics_tracked": self.config["learning"]["metrics_to_track"],
                },
            }

            # Сохранение отчета
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"learning_report_{timestamp}.json"

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)

            # Создание читаемой версии
            self._generate_human_readable_report(report, report_file)

            logger.info(f"Отчет сгенерирован: {report_file}")
            return report_file

        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            raise

    def _generate_human_readable_report(
        self, report: Dict[str, Any], json_report_path: Path
    ) -> None:
        """Генерация читаемого отчета в markdown."""
        try:
            md_report_path = json_report_path.with_suffix(".md")

            with open(md_report_path, "w", encoding="utf-8") as f:
                f.write("# Отчет системы самообучения\n\n")
                f.write(f"**Сгенерирован:** {report['generated_at']}\n")
                f.write(f"**Период анализа:** {report['period_hours']} часов\n\n")

                # Метрики агента
                metrics = report["agent_metrics"]
                f.write("## Метрики эффективности агента\n\n")
                f.write(f"- **Всего задач:** {metrics['total_tasks']}\n")
                f.write(
                    f"- **Успешных задач:** {metrics['successful_tasks']} ({metrics['successful_tasks']/metrics['total_tasks']*100:.1f}%)\n"
                )
                f.write(f"- **Неудачных задач:** {metrics['failed_tasks']}\n")
                f.write(
                    f"- **Средняя длительность:** {metrics['avg_duration']:.1f} сек\n"
                )
                f.write(f"- **Средний приоритет:** {metrics['avg_priority']:.2f}\n")
                f.write(f"- **Среднее качество:** {metrics['avg_quality']:.2f}\n")
                f.write(
                    f"- **Оценка эффективности:** {metrics['efficiency_score']:.2f}\n\n"
                )

                # Предложения по улучшению
                f.write("## Предложения по улучшению\n\n")
                for i, suggestion in enumerate(metrics["improvement_suggestions"], 1):
                    f.write(f"{i}. {suggestion}\n")

                # Сгенерированные улучшения
                improvements = report["improvements"]
                if improvements:
                    f.write("\n## Сгенерированные улучшения\n\n")
                    for i, imp in enumerate(improvements, 1):
                        f.write(f"### {i}. {imp['title']}\n")
                        f.write(f"**Тип:** {imp['type']}\n")
                        f.write(f"**Приоритет:** {imp['priority']}\n")
                        f.write(f"**Описание:** {imp['description']}\n")
                        f.write("**Действия:**\n")
                        for action in imp["actions"]:
                            f.write(f"- {action}\n")
                        f.write("\n")

                # Статус моделей
                models = report["models_status"]
                f.write("## Статус моделей машинного обучения\n\n")
                f.write(f"- **Всего моделей:** {models['total_models']}\n")
                f.write(f"- **Загруженные модели:** {', '.join(models['models'])}\n")
                f.write(
                    f"- **Исторических данных:** {models['historical_data_points']} точек\n"
                )

                # Конфигурация
                config = report["config_summary"]
                f.write("\n## Конфигурация системы\n\n")
                f.write(
                    f"- **Самообучение включено:** {'Да' if config['learning_enabled'] else 'Нет'}\n"
                )
                f.write(
                    f"- **Отслеживаемые метрики:** {', '.join(config['metrics_tracked'])}\n"
                )

            logger.info(f"Читаемый отчет сгенерирован: {md_report_path}")

        except Exception as e:
            logger.error(f"Ошибка генерации читаемого отчета: {e}")

    def run_learning_cycle(self) -> Dict[str, Any]:
        """Запуск полного цикла самообучения."""
        cycle_results = {"started_at": datetime.now().isoformat(), "steps": {}}

        try:
            logger.info("Запуск цикла самообучения...")

            # Шаг 1: Анализ метрик
            cycle_results["steps"]["metrics_analysis"] = {
                "started": datetime.now().isoformat(),
                "status": "running",
            }

            agent_metrics = self.analyze_metrics()
            cycle_results["steps"]["metrics_analysis"].update(
                {
                    "completed": datetime.now().isoformat(),
                    "status": "completed",
                    "efficiency_score": agent_metrics.efficiency_score,
                }
            )

            # Шаг 2: Обучение моделей (если достаточно данных)
            if (
                len(self.historical_metrics)
                >= self.config["learning"]["min_samples_for_learning"]
            ):
                cycle_results["steps"]["model_training"] = {
                    "started": datetime.now().isoformat(),
                    "status": "running",
                }

                training_results = self.train_models()
                cycle_results["steps"]["model_training"].update(
                    {
                        "completed": datetime.now().isoformat(),
                        "status": "completed",
                        "models_trained": training_results.get("models_trained", 0),
                    }
                )

            # Шаг 3: Генерация улучшений
            cycle_results["steps"]["improvements_generation"] = {
                "started": datetime.now().isoformat(),
                "status": "running",
            }

            improvements = self.generate_improvements(agent_metrics)
            cycle_results["steps"]["improvements_generation"].update(
                {
                    "completed": datetime.now().isoformat(),
                    "status": "completed",
                    "improvements_generated": len(improvements),
                }
            )

            # Шаг 4: Применение улучшений (если разрешено)
            if improvements and self.config["improvements"]["auto_apply"]:
                cycle_results["steps"]["improvements_application"] = {
                    "started": datetime.now().isoformat(),
                    "status": "running",
                }

                application_results = self.apply_improvements(improvements)
                cycle_results["steps"]["improvements_application"].update(
                    {
                        "completed": datetime.now().isoformat(),
                        "status": "completed",
                        "improvements_applied": application_results["applied"],
                    }
                )

            # Шаг 5: Генерация отчета
            cycle_results["steps"]["report_generation"] = {
                "started": datetime.now().isoformat(),
                "status": "running",
            }

            report_path = self.generate_report()
            cycle_results["steps"]["report_generation"].update(
                {
                    "completed": datetime.now().isoformat(),
                    "status": "completed",
                    "report_path": str(report_path),
                }
            )

            cycle_results["completed_at"] = datetime.now().isoformat()
            cycle_results["status"] = "success"

            logger.info("Цикл самообучения успешно завершен")

        except Exception as e:
            logger.error(f"Ошибка в цикле самообучения: {e}")
            cycle_results["completed_at"] = datetime.now().isoformat()
            cycle_results["status"] = "failed"
            cycle_results["error"] = str(e)

        return cycle_results


def main():
    """Основная функция запуска системы самообучения."""
    try:
        logger.info("Запуск системы самообучения...")

        # Инициализация системы
        learning_system = LearningSystem()

        # Проверка конфигурации
        if not learning_system.config["learning"]["enabled"]:
            logger.warning("Самообучение отключено в конфигурации")
            return

        # Запуск цикла самообучения
        results = learning_system.run_learning_cycle()

        # Сохранение статуса
        status_file = Path(".agents/status/learning_status.json")
        status_file.parent.mkdir(parents=True, exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(
            f"Система самообучения завершила работу. Статус: {results['status']}"
        )

    except Exception as e:
        logger.error(f"Критическая ошибка в системе самообучения: {e}")
        raise


if __name__ == "__main__":
    main()
