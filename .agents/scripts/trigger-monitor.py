#!/usr/bin/env python3
"""Система мониторинга для работы триггеров Cognitive Automation Agent.
Собирает метрики, генерирует отчеты и предоставляет дашборд.
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

class TriggerMetricsCollector:
    """Сборщик метрик работы триггеров"""

    def __init__(self, db_path: str = ".agents/data/trigger_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица событий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                execution_time REAL,
                success BOOLEAN,
                error_message TEXT,
                metadata TEXT
            )
        """)

        # Таблица метрик
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                period TEXT NOT NULL,
                tags TEXT
            )
        """)

        # Таблица статистики
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name TEXT NOT NULL,
                stat_value TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                period TEXT NOT NULL
            )
        """)

        # Индексы для производительности
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON trigger_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_name ON trigger_events(event_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON trigger_events(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON trigger_metrics(timestamp)")

        conn.commit()
        conn.close()

        logger.info(f"База данных инициализирована: {self.db_path}")

    def record_event(self, event_name: str, source: str, priority: int,
                    status: str, execution_time: float | None = None,
                    success: bool | None = None, error_message: str | None = None,
                    metadata: dict | None = None):
        """Запись события триггера"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trigger_events 
            (event_name, source, timestamp, priority, status, execution_time, success, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_name,
            source,
            datetime.now().isoformat(),
            priority,
            status,
            execution_time,
            success,
            error_message,
            json.dumps(metadata) if metadata else None,
        ))

        conn.commit()
        conn.close()

        logger.debug(f"Записано событие: {event_name} ({status})")

    def record_metric(self, metric_name: str, metric_value: float,
                     period: str = "instant", tags: dict | None = None):
        """Запись метрики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trigger_metrics 
            (metric_name, metric_value, timestamp, period, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (
            metric_name,
            metric_value,
            datetime.now().isoformat(),
            period,
            json.dumps(tags) if tags else None,
        ))

        conn.commit()
        conn.close()

        logger.debug(f"Записана метрика: {metric_name} = {metric_value}")

    def record_stat(self, stat_name: str, stat_value: Any, period: str = "daily"):
        """Запись статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trigger_stats 
            (stat_name, stat_value, timestamp, period)
            VALUES (?, ?, ?, ?)
        """, (
            stat_name,
            json.dumps(stat_value),
            datetime.now().isoformat(),
            period,
        ))

        conn.commit()
        conn.close()

        logger.debug(f"Записана статистика: {stat_name}")

    def get_event_stats(self, hours: int = 24) -> dict[str, Any]:
        """Получение статистики событий за указанный период"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        # Общая статистика
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_events,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_events,
                AVG(execution_time) as avg_execution_time
            FROM trigger_events
            WHERE timestamp >= ?
        """, (cutoff_time,))

        row = cursor.fetchone()
        stats = {
            "total_events": row[0] or 0,
            "successful_events": row[1] or 0,
            "failed_events": row[2] or 0,
            "avg_execution_time": row[3] or 0,
            "success_rate": (row[1] / row[0] * 100) if row[0] > 0 else 0,
        }

        # Статистика по типам событий
        cursor.execute("""
            SELECT 
                event_name,
                COUNT(*) as count,
                AVG(execution_time) as avg_time,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
            FROM trigger_events
            WHERE timestamp >= ?
            GROUP BY event_name
            ORDER BY count DESC
        """, (cutoff_time,))

        events_by_type = []
        for row in cursor.fetchall():
            events_by_type.append({
                "event_name": row[0],
                "count": row[1],
                "avg_time": row[2] or 0,
                "success_count": row[3] or 0,
                "success_rate": (row[3] / row[1] * 100) if row[1] > 0 else 0,
            })

        stats["events_by_type"] = events_by_type

        # Статистика по источникам
        cursor.execute("""
            SELECT 
                source,
                COUNT(*) as count
            FROM trigger_events
            WHERE timestamp >= ?
            GROUP BY source
            ORDER BY count DESC
        """, (cutoff_time,))

        events_by_source = []
        for row in cursor.fetchall():
            events_by_source.append({
                "source": row[0],
                "count": row[1],
            })

        stats["events_by_source"] = events_by_source

        conn.close()
        return stats

    def get_metrics_summary(self, hours: int = 24) -> dict[str, Any]:
        """Получение сводки метрик"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        cursor.execute("""
            SELECT 
                metric_name,
                AVG(metric_value) as avg_value,
                MIN(metric_value) as min_value,
                MAX(metric_value) as max_value,
                COUNT(*) as count
            FROM trigger_metrics
            WHERE timestamp >= ?
            GROUP BY metric_name
        """, (cutoff_time,))

        metrics = {}
        for row in cursor.fetchall():
            metrics[row[0]] = {
                "avg": row[1] or 0,
                "min": row[2] or 0,
                "max": row[3] or 0,
                "count": row[4] or 0,
            }

        conn.close()
        return metrics

    def generate_report(self, report_type: str = "daily") -> dict[str, Any]:
        """Генерация отчета"""
        if report_type == "daily":
            hours = 24
        elif report_type == "weekly":
            hours = 168
        elif report_type == "monthly":
            hours = 720
        else:
            hours = 24

        event_stats = self.get_event_stats(hours)
        metrics_summary = self.get_metrics_summary(hours)

        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "period_hours": hours,
            "event_statistics": event_stats,
            "metrics_summary": metrics_summary,
            "recommendations": self._generate_recommendations(event_stats, metrics_summary),
        }

        # Сохраняем отчет
        report_dir = Path(".agents/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"trigger_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Генерируем читаемый отчет
        self._generate_human_readable_report(report, report_file)

        logger.info(f"Сгенерирован отчет: {report_file}")
        return report

    def _generate_recommendations(self, event_stats: dict, metrics_summary: dict) -> list[str]:
        """Генерация рекомендаций на основе статистики"""
        recommendations = []

        # Проверяем успешность событий
        success_rate = event_stats.get("success_rate", 0)
        if success_rate < 80:
            recommendations.append(
                f"Низкий процент успешных событий: {success_rate:.1f}%. "
                "Рекомендуется проверить логи ошибок и настроить обработку исключений.",
            )

        # Проверяем среднее время выполнения
        avg_execution_time = event_stats.get("avg_execution_time", 0)
        if avg_execution_time > 10:  # больше 10 секунд
            recommendations.append(
                f"Высокое среднее время выполнения: {avg_execution_time:.1f} секунд. "
                "Рекомендуется оптимизировать обработку событий.",
            )

        # Проверяем распределение по типам событий
        events_by_type = event_stats.get("events_by_type", [])
        if len(events_by_type) > 0:
            most_common = events_by_type[0]
            if most_common["count"] > 100:  # слишком много событий одного типа
                recommendations.append(
                    f"Слишком много событий типа '{most_common['event_name']}': {most_common['count']}. "
                    "Рассмотрите возможность агрегации или уменьшения частоты.",
                )

        # Проверяем наличие ошибок
        failed_events = event_stats.get("failed_events", 0)
        if failed_events > 10:
            recommendations.append(
                f"Обнаружено много неудачных событий: {failed_events}. "
                "Рекомендуется провести анализ причин сбоев.",
            )

        if not recommendations:
            recommendations.append("Система работает стабильно. Рекомендации не требуются.")

        return recommendations

    def _generate_human_readable_report(self, report: dict, json_report_path: Path):
        """Генерация читаемого отчета в markdown"""
        md_report_path = json_report_path.with_suffix(".md")

        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("# Отчет мониторинга триггеров\n\n")
            f.write(f"**Тип отчета:** {report['report_type']}\n")
            f.write(f"**Сгенерирован:** {report['generated_at']}\n")
            f.write(f"**Период:** {report['period_hours']} часов\n\n")

            # Статистика событий
            event_stats = report["event_statistics"]
            f.write("## Статистика событий\n\n")
            f.write(f"- Всего событий: **{event_stats['total_events']}**\n")
            f.write(f"- Успешных событий: **{event_stats['successful_events']}**\n")
            f.write(f"- Неудачных событий: **{event_stats['failed_events']}**\n")
            f.write(f"- Процент успеха: **{event_stats['success_rate']:.1f}%**\n")
            f.write(f"- Среднее время выполнения: **{event_stats['avg_execution_time']:.2f} секунд**\n\n")

            # События по типам
            f.write("### События по типам\n\n")
            f.write("| Тип события | Количество | Среднее время | Успешность |\n")
            f.write("|-------------|------------|---------------|------------|\n")

            f.writelines(f"| {event['event_name']} | {event['count']} | {event['avg_time']:.2f}с | {event['success_rate']:.1f}% |\n" for event in event_stats.get("events_by_type", []))

            f.write("\n")

            # Рекомендации
            f.write("## Рекомендации\n\n")
            f.writelines(f"{i}. {recommendation}\n" for i, recommendation in enumerate(report["recommendations"], 1))

            f.write("\n---\n")
            f.write(f"*Полный отчет в JSON: `{json_report_path}`*\n")

        logger.info(f"Сгенерирован читаемый отчет: {md_report_path}")

class TriggerDashboard:
    """Дашборд для мониторинга триггеров"""

    def __init__(self, collector: TriggerMetricsCollector):
        self.collector = collector

    def generate_html_dashboard(self) -> str:
        """Генерация HTML дашборда"""
        # Получаем статистику
        stats = self.collector.get_event_stats(24)
        metrics = self.collector.get_metrics_summary(24)

        # Генерируем HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Дашборд мониторинга триггеров</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header .subtitle {{
                    margin-top: 10px;
                    opacity: 0.9;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }}
                .stat-card h3 {{
                    margin-top: 0;
                    color: #555;
                    font-size: 1em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .stat-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .stat-success {{ color: #10b981; }}
                .stat-warning {{ color: #f59e0b; }}
                .stat-danger {{ color: #ef4444; }}
                .stat-info {{ color: #3b82f6; }}
                .charts {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .chart-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .chart-container h3 {{
                    margin-top: 0;
                    color: #555;
                }}
                .recommendations {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .recommendations h3 {{
                    margin-top: 0;
                    color: #555;
                }}
                .recommendation-item {{
                    padding: 10px;
                    margin: 10px 0;
                    background: #f8fafc;
                    border-left: 4px solid #3b82f6;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 0.9em;
                }}
                @media (max-width: 768px) {{
                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .charts {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Дашборд мониторинга триггеров</h1>
                    <div class="subtitle">
                        Cognitive Automation Agent • {datetime.now().strftime('%d.%m.%Y %H:%M')}
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Всего событий</h3>
                        <div class="stat-value stat-info">{stats['total_events']}</div>
                        <p>За последние 24 часа</p>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Успешность</h3>
                        <div class="stat-value stat-success">{stats['success_rate']:.1f}%</div>
                        <p>{stats['successful_events']} успешных из {stats['total_events']}</p>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Среднее время</h3>
                        <div class="stat-value">{stats['avg_execution_time']:.2f}с</div>
                        <p>Среднее время выполнения события</p>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Неудачных событий</h3>
                        <div class="stat-value stat-danger">{stats['failed_events']}</div>
                        <p>Требуют внимания</p>
                    </div>
                </div>
                
                <div class="charts">
                    <div class="chart-container">
                        <h3>Распределение по типам событий</h3>
                        <canvas id="eventsChart" width="400" height="300"></canvas>
                    </div>
                    
                    <div class="chart-container">
                        <h3>Успешность по типам событий</h3>
                        <canvas id="successChart" width="400" height="300"></canvas>
                    </div>
                </div>
                
                <div class="recommendations">
                    <h3>💡 Рекомендации</h3>
        """

        # Генерируем рекомендации
        report = self.collector.generate_report("daily")
        for i, recommendation in enumerate(report["recommendations"], 1):
            html += f"""
                    <div class="recommendation-item">
                        <strong>{i}.</strong> {recommendation}
                    </div>
            """

        html += f"""
                </div>
                
                <div class="footer">
                    <p>Дашборд обновлен: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                    <p>Cognitive Automation Agent • Система автоматического мониторинга</p>
                </div>
            </div>
            
            <script>
                // Данные для графиков
                const eventsData = {json.dumps([e['event_name'] for e in stats['events_by_type']])};
                const eventsCount = {json.dumps([e['count'] for e in stats['events_by_type']])};
                const successRates = {json.dumps([e['success_rate'] for e in stats['events_by_type']])};
                
                // График распределения событий
                const eventsCtx = document.getElementById('eventsChart').getContext('2d');
                new Chart(eventsCtx, {{
                    type: 'bar',
                    data: {{
                        labels: eventsData,
                        datasets: [{{
                            label: 'Количество событий',
                            data: eventsCount,
                            backgroundColor: [
                                '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                                '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
                            ],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Количество событий'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Тип события'
                                }}
                            }}
                        }}
                    }}
                }});
                
                // График успешности
                const successCtx = document.getElementById('successChart').getContext('2d');
                new Chart(successCtx, {{
                    type: 'line',
                    data: {{
                        labels: eventsData,
                        datasets: [{{
                            label: 'Процент успеха',
                            data: successRates,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: 'Процент успеха (%)'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Тип события'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """

        # Сохраняем дашборд
        dashboard_dir = Path(".agents/dashboards")
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        dashboard_file = dashboard_dir / f"trigger_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Сгенерирован дашборд: {dashboard_file}")
        return str(dashboard_file)

def main():
    """Основная функция мониторинга"""
    print("=" * 60)
    print("СИСТЕМА МОНИТОРИНГА ТРИГГЕРОВ")
    print("=" * 60)

    try:
        # Инициализируем сборщик метрик
        collector = TriggerMetricsCollector()

        # Генерируем отчет
        print("📊 Генерация отчета...")
        report = collector.generate_report("daily")

        print("✓ Отчет сгенерирован:")
        print(f"  - Всего событий: {report['event_statistics']['total_events']}")
        print(f"  - Успешных: {report['event_statistics']['successful_events']}")
        print(f"  - Неудачных: {report['event_statistics']['failed_events']}")
        print(f"  - Успешность: {report['event_statistics']['success_rate']:.1f}%")

        # Генерируем дашборд
        print("\n📈 Генерация дашборда...")
        dashboard = TriggerDashboard(collector)
        dashboard_file = dashboard.generate_html_dashboard()

        print(f"✓ Дашборд сгенерирован: {dashboard_file}")

        # Выводим рекомендации
        print("\n💡 Рекомендации:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")

        print("\n" + "=" * 60)
        print("✅ Мониторинг завершен успешно!")
        print("\n📋 Доступные команды:")
        print("  - Просмотр отчета: cat .agents/reports/trigger_report_*.json")
        print("  - Открыть дашборд: start .agents/dashboards/trigger_dashboard_*.html")
        print("  - Запуск в режиме демона: python trigger-monitor.py --daemon")

        return True

    except Exception as e:
        logger.error(f"Ошибка мониторинга: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
