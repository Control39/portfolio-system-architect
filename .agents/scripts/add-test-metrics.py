#!/usr/bin/env python3
"""Скрипт для добавления тестовых данных в систему мониторинга триггеров.
Используется для демонстрации работы дашбордов и отчетов.
"""

import logging
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TestMetricsGenerator:
    """Генератор тестовых метрик для системы мониторинга"""

    def __init__(self, db_path: str = ".agents/data/trigger_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Инициализация базы данных (если не существует)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Создание таблицы событий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trigger_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    trigger_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    duration_ms INTEGER,
                    error_message TEXT,
                    metadata TEXT
                )
            """)

            # Создание индексов для быстрого поиска
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON trigger_events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trigger_name ON trigger_events(trigger_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON trigger_events(status)")

            conn.commit()
            logger.info(f"База данных инициализирована: {self.db_path}")

    def add_test_events(self, num_events: int = 50):
        """Добавление тестовых событий в базу данных"""
        trigger_names = [
            "project_open", "file_change", "git_commit",
            "git_push", "error_detected", "schedule_daily",
            "pre_commit", "post_commit", "pre_push", "post_merge",
        ]

        event_types = ["trigger", "action", "validation", "scan", "plan"]
        statuses = ["success", "failed", "partial"]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            added_count = 0
            for i in range(num_events):
                # Генерация случайных данных
                trigger_name = random.choice(trigger_names)
                event_type = random.choice(event_types)
                status = random.choice(statuses)

                # Генерация временной метки (последние 7 дней)
                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)

                timestamp = datetime.now() - timedelta(
                    days=days_ago,
                    hours=hours_ago,
                    minutes=minutes_ago,
                )

                duration_ms = random.randint(50, 5000) if status == "success" else random.randint(100, 10000)

                error_message = None
                if status == "failed":
                    error_messages = [
                        "Timeout exceeded",
                        "Permission denied",
                        "File not found",
                        "Network error",
                        "Validation failed",
                        "Configuration error",
                    ]
                    error_message = random.choice(error_messages)

                metadata = {
                    "test_data": True,
                    "iteration": i,
                    "trigger_config": {
                        "autonomy_level": random.choice(["low", "medium", "high"]),
                        "priority": random.choice(["low", "medium", "high"]),
                    },
                }

                # Вставка события
                cursor.execute("""
                    INSERT INTO trigger_events 
                    (event_id, trigger_name, event_type, status, timestamp, duration_ms, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"test_{i:04d}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                    trigger_name,
                    event_type,
                    status,
                    timestamp.isoformat(),
                    duration_ms,
                    error_message,
                    str(metadata),
                ))

                added_count += 1

            conn.commit()
            logger.info(f"Добавлено {added_count} тестовых событий в базу данных")

    def add_realistic_scenario(self):
        """Добавление реалистичного сценария с последовательностью событий"""
        scenarios = [
            {
                "name": "Успешный рабочий день",
                "events": [
                    ("project_open", "success", 100, None),
                    ("scan_project", "success", 1500, None),
                    ("validate_agent", "success", 800, None),
                    ("file_change", "success", 200, None),
                    ("git_commit", "success", 300, None),
                    ("pre_commit", "success", 400, None),
                    ("post_commit", "success", 150, None),
                    ("git_push", "success", 1200, None),
                    ("pre_push", "success", 350, None),
                ],
            },
            {
                "name": "День с ошибками",
                "events": [
                    ("project_open", "success", 120, None),
                    ("scan_project", "failed", 5000, "Timeout exceeded"),
                    ("validate_agent", "partial", 2500, "Missing configuration"),
                    ("file_change", "success", 180, None),
                    ("error_detected", "success", 100, None),
                    ("git_commit", "failed", 800, "Validation failed"),
                    ("pre_commit", "success", 300, None),
                    ("post_commit", "failed", 200, "Network error"),
                ],
            },
            {
                "name": "Автоматическое планирование",
                "events": [
                    ("schedule_daily", "success", 2000, None),
                    ("generate_plan", "success", 3500, None),
                    ("execute_tasks", "partial", 8000, "Task 3 failed"),
                    ("monitor_progress", "success", 1200, None),
                    ("generate_report", "success", 1500, None),
                ],
            },
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            event_counter = 0
            base_time = datetime.now() - timedelta(days=1)

            for scenario in scenarios:
                logger.info(f"Добавление сценария: {scenario['name']}")

                for i, (trigger_name, status, duration_ms, error_message) in enumerate(scenario["events"]):
                    timestamp = base_time + timedelta(minutes=i * 30)

                    metadata = {
                        "scenario": scenario["name"],
                        "sequence": i,
                        "test_data": True,
                        "realistic": True,
                    }

                    cursor.execute("""
                        INSERT INTO trigger_events 
                        (event_id, trigger_name, event_type, status, timestamp, duration_ms, error_message, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"scenario_{scenario['name'].replace(' ', '_').lower()}_{i:02d}",
                        trigger_name,
                        "trigger" if "schedule" not in trigger_name else "schedule",
                        status,
                        timestamp.isoformat(),
                        duration_ms,
                        error_message,
                        str(metadata),
                    ))

                    event_counter += 1

            conn.commit()
            logger.info(f"Добавлено {event_counter} событий из реалистичных сценариев")

    def show_statistics(self):
        """Показать статистику базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Общее количество событий
            cursor.execute("SELECT COUNT(*) FROM trigger_events")
            total_events = cursor.fetchone()[0]

            # Количество событий по статусам
            cursor.execute("SELECT status, COUNT(*) FROM trigger_events GROUP BY status")
            status_counts = cursor.fetchall()

            # Количество событий по триггерам
            cursor.execute("SELECT trigger_name, COUNT(*) FROM trigger_events GROUP BY trigger_name ORDER BY COUNT(*) DESC LIMIT 10")
            top_triggers = cursor.fetchall()

            # Временной диапазон
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trigger_events")
            time_range = cursor.fetchone()

            print("=" * 60)
            print("СТАТИСТИКА БАЗЫ ДАННЫХ МОНИТОРИНГА")
            print("=" * 60)
            print(f"Всего событий: {total_events}")
            print("\nРаспределение по статусам:")
            for status, count in status_counts:
                percentage = (count / total_events * 100) if total_events > 0 else 0
                print(f"  {status}: {count} ({percentage:.1f}%)")

            print("\nТоп триггеров:")
            for trigger, count in top_triggers:
                print(f"  {trigger}: {count}")

            if time_range[0] and time_range[1]:
                print(f"\nВременной диапазон: {time_range[0]} - {time_range[1]}")

            print("=" * 60)

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Генератор тестовых метрик для системы мониторинга")
    parser.add_argument("--count", type=int, default=50, help="Количество тестовых событий для генерации")
    parser.add_argument("--scenarios", action="store_true", help="Добавить реалистичные сценарии")
    parser.add_argument("--stats", action="store_true", help="Показать статистику базы данных")
    parser.add_argument("--reset", action="store_true", help="Очистить базу данных перед добавлением")

    args = parser.parse_args()

    generator = TestMetricsGenerator()

    if args.reset:
        logger.warning("Очистка базы данных...")
        with sqlite3.connect(generator.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trigger_events")
            conn.commit()
        logger.info("База данных очищена")

    if args.count > 0:
        generator.add_test_events(args.count)

    if args.scenarios:
        generator.add_realistic_scenario()

    if args.stats or args.count > 0 or args.scenarios:
        generator.show_statistics()

    if not any([args.count > 0, args.scenarios, args.stats, args.reset]):
        print("Использование:")
        print("  python add-test-metrics.py --count 100          # Добавить 100 тестовых событий")
        print("  python add-test-metrics.py --scenarios          # Добавить реалистичные сценарии")
        print("  python add-test-metrics.py --stats              # Показать статистику")
        print("  python add-test-metrics.py --reset --count 50   # Очистить и добавить 50 событий")

if __name__ == "__main__":
    main()
