#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в систему мониторинга триггеров.
Адаптирован под существующую структуру базы данных.
"""

import json
import logging
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestMetricsGeneratorV2:
    """Генератор тестовых метрик для системы мониторинга (версия 2)"""

    def __init__(self, db_path: str = ".agents/data/trigger_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def add_test_events(self, num_events: int = 50):
        """Добавление тестовых событий в базу данных"""
        event_names = [
            "project_open",
            "file_change",
            "git_commit",
            "git_push",
            "error_detected",
            "schedule_daily",
            "pre_commit",
            "post_commit",
            "pre_push",
            "post_merge",
            "scan_project",
            "validate_agent",
            "generate_plan",
            "execute_tasks",
            "monitor_progress",
            "generate_report",
        ]

        sources = ["trigger_processor", "git_hook", "vscode", "manual", "schedule"]
        statuses = ["success", "failed", "partial", "pending", "running"]
        priorities = [1, 2, 3, 4, 5]  # 1 - highest, 5 - lowest

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            added_count = 0
            for i in range(num_events):
                # Генерация случайных данных
                event_name = random.choice(event_names)
                source = random.choice(sources)
                status = random.choice(statuses)
                priority = random.choice(priorities)

                # Генерация временной метки (последние 7 дней)
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                seconds_ago = random.randint(0, 59)

                timestamp = datetime.now() - timedelta(
                    days=days_ago,
                    hours=hours_ago,
                    minutes=minutes_ago,
                    seconds=seconds_ago,
                )

                execution_time = random.uniform(0.1, 10.0)  # в секундах
                success = status == "success"

                error_message = None
                if status == "failed":
                    error_messages = [
                        "Timeout exceeded",
                        "Permission denied",
                        "File not found",
                        "Network error",
                        "Validation failed",
                        "Configuration error",
                        "Memory limit exceeded",
                        "Disk space不足",
                    ]
                    error_message = random.choice(error_messages)

                metadata = {
                    "test_data": True,
                    "iteration": i,
                    "autonomy_level": random.choice(["low", "medium", "high"]),
                    "trigger_config": {
                        "enabled": random.choice([True, False]),
                        "priority": random.choice(["low", "medium", "high"]),
                        "retry_count": random.randint(0, 3),
                    },
                    "performance": {
                        "memory_usage_mb": random.randint(10, 500),
                        "cpu_usage_percent": random.uniform(1.0, 80.0),
                    },
                }

                # Вставка события
                cursor.execute(
                    """
                    INSERT INTO trigger_events
                    (event_name, source, timestamp, priority, status, execution_time, success, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event_name,
                        source,
                        timestamp.isoformat(),
                        priority,
                        status,
                        execution_time,
                        success,
                        error_message,
                        json.dumps(metadata),
                    ),
                )

                added_count += 1

            conn.commit()
            logger.info(f"Добавлено {added_count} тестовых событий в базу данных")

    def add_metrics_data(self):
        """Добавление тестовых метрик"""
        metric_names = [
            "events_per_hour",
            "success_rate",
            "average_execution_time",
            "failure_rate",
            "memory_usage",
            "cpu_usage",
            "queue_length",
            "worker_utilization",
            "response_time",
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            base_time = datetime.now() - timedelta(days=7)

            for day in range(7):
                for hour in range(24):
                    timestamp = base_time + timedelta(days=day, hours=hour)

                    for metric_name in metric_names:
                        # Генерация реалистичных значений метрик
                        if metric_name == "events_per_hour":
                            value = random.randint(5, 100)
                        elif metric_name == "success_rate":
                            value = random.uniform(70.0, 99.5)
                        elif metric_name == "average_execution_time":
                            value = random.uniform(0.5, 5.0)
                        elif metric_name == "failure_rate":
                            value = random.uniform(0.1, 5.0)
                        elif metric_name == "memory_usage":
                            value = random.uniform(100.0, 800.0)
                        elif metric_name == "cpu_usage":
                            value = random.uniform(10.0, 60.0)
                        elif metric_name == "queue_length":
                            value = random.randint(0, 20)
                        elif metric_name == "worker_utilization":
                            value = random.uniform(30.0, 95.0)
                        elif metric_name == "response_time":
                            value = random.uniform(0.1, 2.0)
                        else:
                            value = random.uniform(0.0, 100.0)

                        period = "hourly"
                        tags = json.dumps({"test_data": True, "source": "test_generator"})

                        cursor.execute(
                            """
                            INSERT INTO trigger_metrics
                            (metric_name, metric_value, timestamp, period, tags)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (metric_name, value, timestamp.isoformat(), period, tags),
                        )

            conn.commit()
            logger.info("Добавлены тестовые метрики")

    def add_stats_data(self):
        """Добавление статистических данных"""
        stat_data = [
            ("total_events", "1500", "weekly"),
            ("successful_events", "1350", "weekly"),
            ("failed_events", "120", "weekly"),
            ("partial_events", "30", "weekly"),
            ("avg_execution_time_seconds", "2.5", "weekly"),
            ("peak_memory_usage_mb", "750", "weekly"),
            ("avg_cpu_usage_percent", "45.2", "weekly"),
            ("busiest_trigger", "project_open", "weekly"),
            ("most_reliable_trigger", "post_commit", "weekly"),
            ("total_execution_time_hours", "12.8", "weekly"),
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for stat_name, stat_value, period in stat_data:
                timestamp = datetime.now() - timedelta(days=random.randint(0, 6))

                cursor.execute(
                    """
                    INSERT INTO trigger_stats
                    (stat_name, stat_value, timestamp, period)
                    VALUES (?, ?, ?, ?)
                """,
                    (stat_name, stat_value, timestamp.isoformat(), period),
                )

            conn.commit()
            logger.info("Добавлены статистические данные")

    def show_statistics(self):
        """Показать статистику базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            print("=" * 60)
            print("СТАТИСТИКА БАЗЫ ДАННЫХ МОНИТОРИНГА")
            print("=" * 60)

            # Статистика по таблицам
            tables = ["trigger_events", "trigger_metrics", "trigger_stats"]
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} записей")

            print("\n📊 Статистика событий:")

            # Распределение по статусам
            cursor.execute("SELECT status, COUNT(*) FROM trigger_events GROUP BY status")
            status_counts = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM trigger_events")
            total_events = cursor.fetchone()[0]

            if total_events > 0:
                print("  По статусам:")
                for status, count in status_counts:
                    percentage = count / total_events * 100
                    print(f"    {status}: {count} ({percentage:.1f}%)")

            # Топ событий
            cursor.execute(
                "SELECT event_name, COUNT(*) FROM trigger_events GROUP BY event_name ORDER BY COUNT(*) DESC LIMIT 5"
            )
            top_events = cursor.fetchall()

            if top_events:
                print("\n  Топ событий:")
                for event_name, count in top_events:
                    print(f"    {event_name}: {count}")

            # Успешность
            cursor.execute("SELECT COUNT(*) FROM trigger_events WHERE success = 1")
            successful = cursor.fetchone()[0]

            if total_events > 0:
                success_rate = successful / total_events * 100
                print(f"\n  Успешность: {success_rate:.1f}% ({successful}/{total_events})")

            # Временной диапазон
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trigger_events")
            time_range = cursor.fetchone()

            if time_range[0] and time_range[1]:
                print(f"\n  Временной диапазон: {time_range[0]} - {time_range[1]}")

            print("=" * 60)


def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Генератор тестовых метрик для системы мониторинга (v2)"
    )
    parser.add_argument(
        "--events",
        type=int,
        default=50,
        help="Количество тестовых событий для генерации",
    )
    parser.add_argument("--metrics", action="store_true", help="Добавить тестовые метрики")
    parser.add_argument("--stats", action="store_true", help="Добавить статистические данные")
    parser.add_argument("--all", action="store_true", help="Добавить все типы данных")
    parser.add_argument("--show", action="store_true", help="Показать статистику базы данных")
    parser.add_argument(
        "--reset", action="store_true", help="Очистить базу данных перед добавлением"
    )

    args = parser.parse_args()

    generator = TestMetricsGeneratorV2()

    if args.reset:
        logger.warning("Очистка базы данных...")
        with sqlite3.connect(generator.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trigger_events")
            cursor.execute("DELETE FROM trigger_metrics")
            cursor.execute("DELETE FROM trigger_stats")
            conn.commit()
        logger.info("База данных очищена")

    if args.events > 0 or args.all:
        generator.add_test_events(args.events)

    if args.metrics or args.all:
        generator.add_metrics_data()

    if args.stats or args.all:
        generator.add_stats_data()

    if args.show or args.events > 0 or args.metrics or args.stats or args.all:
        generator.show_statistics()

    if not any([args.events > 0, args.metrics, args.stats, args.all, args.show, args.reset]):
        print("Использование:")
        print(
            "  python add-test-metrics-v2.py --events 100          # Добавить 100 тестовых событий"
        )
        print("  python add-test-metrics-v2.py --metrics             # Добавить тестовые метрики")
        print(
            "  python add-test-metrics-v2.py --stats               # Добавить статистические данные"
        )
        print("  python add-test-metrics-v2.py --all                 # Добавить все типы данных")
        print("  python add-test-metrics-v2.py --show                # Показать статистику")
        print(
            "  python add-test-metrics-v2.py --reset --events 50   # Очистить и добавить 50 событий"
        )


if __name__ == "__main__":
    main()
