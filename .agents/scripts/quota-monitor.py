#!/usr/bin/env python3
"""
Мониторинг квот SourceCraft в реальном времени.

Отслеживает использование нейрокредитов, времени автоматизаций, хранилища
и других ресурсов для оптимизации использования квот.
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/quota-monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class QuotaMonitor:
    """Монитор квот SourceCraft"""

    def __init__(self, config_path: str = ".agents/config/quota-config.yaml"):
        self.config_path = Path(config_path)
        self.quota_data = {}
        self.alerts = []
        self.thresholds = {
            "neurocredits": 80,  # 80% использование
            "automation_time": 75,  # 75% использование
            "public_storage": 90,  # 90% использование
            "private_storage": 85,  # 85% использование
            "code_prompts": 70,  # 70% использование
        }

        # Загрузка конфигурации
        self._load_config()

    def _load_config(self):
        """Загрузка конфигурации мониторинга"""
        try:
            import yaml

            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config and "thresholds" in config:
                        self.thresholds.update(config["thresholds"])
        except ImportError:
            logger.warning("PyYAML не установлен, используются значения по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")

    def get_current_quotas(self) -> Dict[str, Any]:
        """
        Получение текущих данных о квотах.
        В реальной реализации здесь будет API-запрос к SourceCraft.
        """
        # Заглушка для демонстрации
        # В реальном использовании здесь будет вызов API SourceCraft
        return {
            "neurocredits": {
                "used": 3624,
                "total": 4500,
                "percentage": 80.5,
                "last_updated": datetime.now().isoformat(),
            },
            "code_prompts": {
                "used": 10,
                "total": 4000,
                "percentage": 0.25,
                "last_updated": datetime.now().isoformat(),
            },
            "automation_time": {
                "used": 191,
                "total": 1000,
                "percentage": 19.1,
                "last_updated": datetime.now().isoformat(),
            },
            "public_storage": {
                "used": 0.136,
                "total": 2.0,
                "percentage": 6.8,
                "last_updated": datetime.now().isoformat(),
            },
            "private_storage": {
                "used": 0.012,
                "total": 0.5,
                "percentage": 2.4,
                "last_updated": datetime.now().isoformat(),
            },
        }

    def check_thresholds(self, quota_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Проверка превышения пороговых значений"""
        alerts = []

        for quota_name, data in quota_data.items():
            if quota_name in self.thresholds:
                percentage = data.get("percentage", 0)
                threshold = self.thresholds[quota_name]

                if percentage >= threshold:
                    alert = {
                        "quota": quota_name,
                        "percentage": percentage,
                        "threshold": threshold,
                        "used": data.get("used"),
                        "total": data.get("total"),
                        "timestamp": datetime.now().isoformat(),
                        "severity": "warning" if percentage < 90 else "critical",
                    }
                    alerts.append(alert)

                    logger.warning(
                        f"Превышен порог для {quota_name}: {percentage}% (порог: {threshold}%)"
                    )

        return alerts

    def generate_optimization_recommendations(
        self, quota_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Генерация рекомендаций по оптимизации квот"""
        recommendations = []

        # Нейрокредиты
        if quota_data.get("neurocredits", {}).get("percentage", 0) > 70:
            recommendations.append(
                {
                    "category": "neurocredits",
                    "priority": "high",
                    "action": "Включить локальную обработку для простых задач",
                    "description": "Использовать локальные инструменты (pyright, flake8) вместо облачных проверок",
                    "estimated_savings": "15-30% нейрокредитов",
                }
            )
            recommendations.append(
                {
                    "category": "neurocredits",
                    "priority": "medium",
                    "action": "Кэшировать результаты анализа",
                    "description": "Сохранять результаты сканирования для повторного использования",
                    "estimated_savings": "10-20% нейрокредитов",
                }
            )

        # Время автоматизаций
        if quota_data.get("automation_time", {}).get("percentage", 0) > 60:
            recommendations.append(
                {
                    "category": "automation_time",
                    "priority": "high",
                    "action": "Оптимизировать расписание запусков",
                    "description": "Запускать тяжелые задачи в непиковые часы",
                    "estimated_savings": "20-40% времени",
                }
            )

        # Хранилище
        if quota_data.get("public_storage", {}).get("percentage", 0) > 80:
            recommendations.append(
                {
                    "category": "storage",
                    "priority": "medium",
                    "action": "Очистить старые отчеты и логи",
                    "description": "Удалить отчеты старше 30 дней",
                    "estimated_savings": "0.5-1.0 GB",
                }
            )

        return recommendations

    def save_report(self, report: Dict[str, Any], output_path: str):
        """Сохранение отчета в файл"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Отчет сохранен: {output_file}")

    def run_monitoring(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Запуск мониторинга квот"""
        logger.info("Запуск мониторинга квот SourceCraft...")

        # Получение текущих данных
        quota_data = self.get_current_quotas()

        # Проверка порогов
        alerts = self.check_thresholds(quota_data)

        # Генерация рекомендаций
        recommendations = self.generate_optimization_recommendations(quota_data)

        # Формирование отчета
        report = {
            "timestamp": datetime.now().isoformat(),
            "quotas": quota_data,
            "alerts": alerts,
            "recommendations": recommendations,
            "summary": {
                "total_quotas": len(quota_data),
                "alerts_count": len(alerts),
                "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
                "recommendations_count": len(recommendations),
            },
        }

        # Сохранение отчета
        if output_path:
            self.save_report(report, output_path)

        # Вывод сводки
        self.print_summary(report)

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Вывод сводки мониторинга"""
        print("\n" + "=" * 60)
        print("СВОДКА МОНИТОРИНГА КВОТ SOURCECRAFT")
        print("=" * 60)

        quotas = report.get("quotas", {})
        for name, data in quotas.items():
            percentage = data.get("percentage", 0)
            used = data.get("used", 0)
            total = data.get("total", 0)

            # Цветовое кодирование
            if percentage >= 90:
                color = "\033[91m"  # красный
            elif percentage >= 80:
                color = "\033[93m"  # желтый
            else:
                color = "\033[92m"  # зеленый

            reset = "\033[0m"

            print(f"{name:20} {color}{percentage:6.1f}%{reset} ({used}/{total})")

        print("-" * 60)

        alerts = report.get("alerts", [])
        if alerts:
            print(f"\n\033[93mВНИМАНИЕ: {len(alerts)} предупреждений:\033[0m")
            for alert in alerts:
                print(
                    f"  • {alert['quota']}: {alert['percentage']}% (порог: {alert['threshold']}%)"
                )

        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n\033[92mРЕКОМЕНДАЦИИ ({len(recommendations)}):\033[0m")
            for rec in recommendations:
                print(f"  • [{rec['priority'].upper()}] {rec['action']}")

        print("=" * 60)


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Мониторинг квот SourceCraft")
    parser.add_argument(
        "--output",
        "-o",
        default=".agents/reports/quota-monitor.json",
        help="Путь для сохранения отчета",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=3600,
        help="Интервал мониторинга в секундах (по умолчанию: 3600)",
    )
    parser.add_argument("--continuous", "-c", action="store_true", help="Непрерывный мониторинг")
    parser.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=80,
        help="Порог предупреждения в процентах",
    )

    args = parser.parse_args()

    monitor = QuotaMonitor()
    monitor.thresholds = dict.fromkeys(monitor.thresholds, args.threshold)

    if args.continuous:
        logger.info(f"Запуск непрерывного мониторинга с интервалом {args.interval} секунд")
        try:
            while True:
                monitor.run_monitoring(args.output)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Мониторинг остановлен пользователем")
    else:
        monitor.run_monitoring(args.output)


if __name__ == "__main__":
    main()
