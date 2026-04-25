#!/usr/bin/env python3
"""Система оповещений для мониторинга триггеров.
Проверяет метрики и отправляет уведомления при обнаружении проблем.
"""

import json
import logging
import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/alerts.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

class AlertSystem:
    """Система оповещений для мониторинга триггеров"""

    def __init__(self, db_path: str = ".agents/data/trigger_metrics.db"):
        self.db_path = Path(db_path)
        self.alerts_dir = Path(".agents/alerts")
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

        # Конфигурация оповещений
        self.alert_config = self._load_alert_config()

    def _load_alert_config(self) -> dict[str, Any]:
        """Загрузка конфигурации оповещений"""
        default_config = {
            "thresholds": {
                "success_rate": 80.0,  # Минимальный процент успешных событий
                "failure_rate": 10.0,   # Максимальный процент неудачных событий
                "avg_execution_time": 5.0,  # Максимальное среднее время выполнения (сек)
                "queue_length": 10,     # Максимальная длина очереди
                "memory_usage_mb": 500, # Максимальное использование памяти
                "error_count": 5,       # Максимальное количество ошибок за час
            },
            "notification": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": "",
                    "recipients": [],
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#monitoring",
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": "",
                },
            },
            "alert_cooldown_minutes": 30,  # Время между повторными оповещениями
            "check_interval_hours": 1,     # Интервал проверки
        }

        config_path = Path(".agents/config/alerts.yaml")
        if config_path.exists():
            try:
                import yaml
                with open(config_path, encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    # Объединяем с конфигурацией по умолчанию
                    return self._merge_configs(default_config, user_config)
            except Exception as e:
                logger.warning(f"Не удалось загрузить конфигурацию оповещений: {e}")

        return default_config

    def _merge_configs(self, default: dict, user: dict) -> dict:
        """Рекурсивное объединение конфигураций"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def check_metrics(self, hours: int = 24) -> list[dict[str, Any]]:
        """Проверка метрик и генерация оповещений"""
        alerts = []

        # Получаем статистику за указанный период
        stats = self._get_event_stats(hours)

        # Проверяем пороговые значения
        thresholds = self.alert_config["thresholds"]

        # 1. Проверка успешности
        success_rate = stats.get("success_rate", 0)
        if success_rate < thresholds["success_rate"]:
            alerts.append({
                "type": "success_rate_low",
                "severity": "high",
                "message": f"Низкий процент успешных событий: {success_rate:.1f}% (минимум: {thresholds['success_rate']}%)",
                "metric": success_rate,
                "threshold": thresholds["success_rate"],
                "period_hours": hours,
            })

        # 2. Проверка количества ошибок
        error_count = stats.get("error_count", 0)
        if error_count > thresholds["error_count"]:
            alerts.append({
                "type": "error_count_high",
                "severity": "medium",
                "message": f"Высокое количество ошибок: {error_count} (максимум: {thresholds['error_count']})",
                "metric": error_count,
                "threshold": thresholds["error_count"],
                "period_hours": hours,
            })

        # 3. Проверка среднего времени выполнения
        avg_execution_time = stats.get("avg_execution_time", 0)
        if avg_execution_time > thresholds["avg_execution_time"]:
            alerts.append({
                "type": "execution_time_high",
                "severity": "medium",
                "message": f"Высокое среднее время выполнения: {avg_execution_time:.2f} сек (максимум: {thresholds['avg_execution_time']} сек)",
                "metric": avg_execution_time,
                "threshold": thresholds["avg_execution_time"],
                "period_hours": hours,
            })

        # 4. Проверка самых частых ошибок
        common_errors = self._get_common_errors(hours)
        if common_errors:
            error_messages = [f"{error}: {count}" for error, count in common_errors[:3]]
            alerts.append({
                "type": "common_errors",
                "severity": "low",
                "message": f"Частые ошибки: {', '.join(error_messages)}",
                "errors": common_errors[:5],
                "period_hours": hours,
            })

        # 5. Проверка производительности системы
        performance_issues = self._check_performance_issues(hours)
        alerts.extend(performance_issues)

        return alerts

    def _get_event_stats(self, hours: int) -> dict[str, Any]:
        """Получение статистики событий за указанный период"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Временная граница
            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()

            # Общее количество событий
            cursor.execute("""
                SELECT COUNT(*) FROM trigger_events 
                WHERE timestamp > ?
            """, (time_threshold,))
            total_events = cursor.fetchone()[0]

            # Успешные события
            cursor.execute("""
                SELECT COUNT(*) FROM trigger_events 
                WHERE timestamp > ? AND success = 1
            """, (time_threshold,))
            successful_events = cursor.fetchone()[0]

            # Неудачные события
            cursor.execute("""
                SELECT COUNT(*) FROM trigger_events 
                WHERE timestamp > ? AND success = 0
            """, (time_threshold,))
            failed_events = cursor.fetchone()[0]

            # Среднее время выполнения
            cursor.execute("""
                SELECT AVG(execution_time) FROM trigger_events 
                WHERE timestamp > ? AND execution_time IS NOT NULL
            """, (time_threshold,))
            avg_execution_time = cursor.fetchone()[0] or 0

            # Количество ошибок
            cursor.execute("""
                SELECT COUNT(*) FROM trigger_events 
                WHERE timestamp > ? AND error_message IS NOT NULL
            """, (time_threshold,))
            error_count = cursor.fetchone()[0]

            # Расчет процентов
            success_rate = (successful_events / total_events * 100) if total_events > 0 else 0
            failure_rate = (failed_events / total_events * 100) if total_events > 0 else 0

            return {
                "total_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "avg_execution_time": avg_execution_time,
                "error_count": error_count,
            }

    def _get_common_errors(self, hours: int) -> list[tuple]:
        """Получение самых частых ошибок"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()

            cursor.execute("""
                SELECT error_message, COUNT(*) as count 
                FROM trigger_events 
                WHERE timestamp > ? AND error_message IS NOT NULL 
                GROUP BY error_message 
                ORDER BY count DESC 
                LIMIT 10
            """, (time_threshold,))

            return cursor.fetchall()

    def _check_performance_issues(self, hours: int) -> list[dict[str, Any]]:
        """Проверка проблем с производительностью"""
        alerts = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()

            # Проверка медленных событий
            cursor.execute("""
                SELECT event_name, execution_time 
                FROM trigger_events 
                WHERE timestamp > ? AND execution_time > 10
                ORDER BY execution_time DESC 
                LIMIT 5
            """, (time_threshold,))

            slow_events = cursor.fetchall()
            if slow_events:
                slow_list = [f"{event} ({time:.1f}сек)" for event, time in slow_events]
                alerts.append({
                    "type": "slow_events",
                    "severity": "medium",
                    "message": f"Медленные события: {', '.join(slow_list)}",
                    "events": slow_events,
                    "period_hours": hours,
                })

            # Проверка частых повторных ошибок
            cursor.execute("""
                SELECT event_name, COUNT(*) as error_count 
                FROM trigger_events 
                WHERE timestamp > ? AND success = 0
                GROUP BY event_name 
                HAVING error_count > 3
                ORDER BY error_count DESC
            """, (time_threshold,))

            recurring_errors = cursor.fetchall()
            if recurring_errors:
                error_list = [f"{event} ({count})" for event, count in recurring_errors]
                alerts.append({
                    "type": "recurring_errors",
                    "severity": "high",
                    "message": f"Повторяющиеся ошибки: {', '.join(error_list)}",
                    "errors": recurring_errors,
                    "period_hours": hours,
                })

        return alerts

    def should_send_alert(self, alert_type: str) -> bool:
        """Проверка, нужно ли отправлять оповещение (учет времени охлаждения)"""
        cooldown_file = self.alerts_dir / "cooldown.json"

        if not cooldown_file.exists():
            return True

        try:
            with open(cooldown_file) as f:
                cooldown_data = json.load(f)

            last_alert_time = cooldown_data.get(alert_type)
            if not last_alert_time:
                return True

            last_time = datetime.fromisoformat(last_alert_time)
            cooldown_minutes = self.alert_config["alert_cooldown_minutes"]

            if (datetime.now() - last_time).total_seconds() > cooldown_minutes * 60:
                return True
            logger.debug(f"Оповещение {alert_type} в режиме охлаждения")
            return False

        except Exception as e:
            logger.warning(f"Ошибка при проверке времени охлаждения: {e}")
            return True

    def update_cooldown(self, alert_type: str):
        """Обновление времени последнего оповещения"""
        cooldown_file = self.alerts_dir / "cooldown.json"

        try:
            if cooldown_file.exists():
                with open(cooldown_file) as f:
                    cooldown_data = json.load(f)
            else:
                cooldown_data = {}

            cooldown_data[alert_type] = datetime.now().isoformat()

            with open(cooldown_file, "w") as f:
                json.dump(cooldown_data, f, indent=2)

        except Exception as e:
            logger.error(f"Ошибка при обновлении времени охлаждения: {e}")

    def send_notifications(self, alerts: list[dict[str, Any]]):
        """Отправка уведомлений"""
        if not alerts:
            logger.info("Нет оповещений для отправки")
            return

        # Группируем оповещения по уровню серьезности
        high_alerts = [a for a in alerts if a["severity"] == "high"]
        medium_alerts = [a for a in alerts if a["severity"] == "medium"]
        low_alerts = [a for a in alerts if a["severity"] == "low"]

        # Формируем сообщение
        message = self._format_alert_message(high_alerts, medium_alerts, low_alerts)

        # Отправляем уведомления
        notifications_sent = 0

        # Email уведомления
        if self.alert_config["notification"]["email"]["enabled"]:
            if self._send_email_alert(message):
                notifications_sent += 1

        # Slack уведомления
        if self.alert_config["notification"]["slack"]["enabled"]:
            if self._send_slack_alert(message):
                notifications_sent += 1

        # Telegram уведомления
        if self.alert_config["notification"]["telegram"]["enabled"]:
            if self._send_telegram_alert(message):
                notifications_sent += 1

        # Локальное сохранение оповещений
        self._save_alerts_locally(alerts)

        logger.info(f"Отправлено {notifications_sent} уведомлений о {len(alerts)} оповещениях")

    def _format_alert_message(self, high: list, medium: list, low: list) -> str:
        """Форматирование сообщения об оповещениях"""
        lines = []

        lines.append("🚨 ОПОВЕЩЕНИЯ СИСТЕМЫ МОНИТОРИНГА ТРИГГЕРОВ")
        lines.append("=" * 50)
        lines.append(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if high:
            lines.append("🔴 ВЫСОКИЙ УРОВЕНЬ ОПАСНОСТИ:")
            for alert in high:
                lines.append(f"  • {alert['message']}")
            lines.append("")

        if medium:
            lines.append("🟡 СРЕДНИЙ УРОВЕНЬ ОПАСНОСТИ:")
            for alert in medium:
                lines.append(f"  • {alert['message']}")
            lines.append("")

        if low:
            lines.append("🟢 НИЗКИЙ УРОВЕНЬ ОПАСНОСТИ:")
            for alert in low:
                lines.append(f"  • {alert['message']}")

        lines.append("")
        lines.append("=" * 50)
        lines.append("Для деталей проверьте дашборд мониторинга.")

        return "\n".join(lines)

    def _send_email_alert(self, message: str) -> bool:
        """Отправка оповещения по email"""
        try:
            config = self.alert_config["notification"]["email"]

            msg = MIMEMultipart()
            msg["From"] = config["sender_email"]
            msg["To"] = ", ".join(config["recipients"])
            msg["Subject"] = "🚨 Оповещение системы мониторинга триггеров"

            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)
            server.quit()

            logger.info("Email оповещение отправлено")
            return True

        except Exception as e:
            logger.error(f"Ошибка при отправке email: {e}")
            return False

    def _send_slack_alert(self, message: str) -> bool:
        """Отправка оповещения в Slack"""
        try:
            config = self.alert_config["notification"]["slack"]

            payload = {
                "text": message,
                "channel": config["channel"],
                "username": "Trigger Monitor Bot",
                "icon_emoji": ":warning:",
            }

            response = requests.post(config["webhook_url"], json=payload)

            if response.status_code == 200:
                logger.info("Slack оповещение отправлено")
                return True
            logger.error(f"Ошибка Slack: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            logger.error(f"Ошибка при отправке в Slack: {e}")
            return False

    def _send_telegram_alert(self, message: str) -> bool:
        """Отправка оповещения в Telegram"""
        try:
            config = self.alert_config["notification"]["telegram"]

            url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
            payload = {
                "chat_id": config["chat_id"],
                "text": message,
                "parse_mode": "HTML",
            }

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logger.info("Telegram оповещение отправлено")
                return True
            logger.error(f"Ошибка Telegram: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            logger.error(f"Ошибка при отправке в Telegram: {e}")
            return False

    def _save_alerts_locally(self, alerts: list[dict[str, Any]]):
        """Сохранение оповещений локально"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            alert_file = self.alerts_dir / f"alerts_{timestamp}.json"

            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "total_alerts": len(alerts),
                "alerts": alerts,
            }

            with open(alert_file, "w", encoding="utf-8") as f:
                json.dump(alert_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Оповещения сохранены в {alert_file}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении оповещений: {e}")

    def run_checks(self, hours: int = 24, send_notifications: bool = True):
        """Запуск проверок и обработка оповещений"""
        logger.info(f"Запуск проверки метрик за последние {hours} часов...")

        # Получаем оповещения
        alerts = self.check_metrics(hours)

        if not alerts:
            logger.info("Проблем не обнаружено")
            return

        logger.info(f"Обнаружено {len(alerts)} оповещений")

        # Фильтруем оповещения по времени охлаждения
        filtered_alerts = []
        for alert in alerts:
            if self.should_send_alert(alert["type"]):
                filtered_alerts.append(alert)
                self.update_cooldown(alert["type"])

        if not filtered_alerts:
            logger.info("Все оповещения в режиме охлаждения")
            return

        # Отправляем уведомления
        if send_notifications:
            self.send_notifications(filtered_alerts)

        # Выводим оповещения в консоль
        print("\n" + "=" * 60)
        print("ОПОВЕЩЕНИЯ СИСТЕМЫ МОНИТОРИНГА")
        print("=" * 60)

        for alert in filtered_alerts:
            severity_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢",
            }.get(alert["severity"], "⚪")

            print(f"{severity_icon} [{alert['severity'].upper()}] {alert['message']}")

        print("=" * 60)

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Система оповещений для мониторинга триггеров")
    parser.add_argument("--hours", type=int, default=24, help="Период для анализа (в часах)")
    parser.add_argument("--no-notify", action="store_true", help="Не отправлять уведомления")
    parser.add_argument("--test", action="store_true", help="Тестовый запуск")
    parser.add_argument("--config", help="Путь к файлу конфигурации")

    args = parser.parse_args()

    alert_system = AlertSystem()

    if args.test:
        print("Тестовый запуск системы оповещений...")

        # Создаем тестовые оповещения
        test_alerts = [
            {
                "type": "test_alert",
                "severity": "high",
                "message": "Тестовое оповещение высокого уровня",
                "metric": 95.0,
                "threshold": 90.0,
                "period_hours": 24,
            },
            {
                "type": "test_alert_medium",
                "severity": "medium",
                "message": "Тестовое оповещение среднего уровня",
                "metric": 15,
                "threshold": 10,
                "period_hours": 24,
            },
        ]

        print("\nТестовые оповещения:")
        for alert in test_alerts:
            print(f"  {alert['severity']}: {alert['message']}")

        print("\nФорматированное сообщение:")
        print(alert_system._format_alert_message(
            [test_alerts[0]], [test_alerts[1]], [],
        ))

        return

    # Основной запуск
    alert_system.run_checks(
        hours=args.hours,
        send_notifications=not args.no_notify,
    )

if __name__ == "__main__":
    main()

