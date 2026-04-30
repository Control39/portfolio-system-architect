#!/usr/bin/env python3
"""
Планировщик для автоматического запуска системы мониторинга триггеров.
Поддерживает различные интервалы: ежечасно, ежедневно, еженедельно.
"""

import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/scheduled-monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ScheduledMonitor:
    """Планировщик автоматического мониторинга"""

    def __init__(self):
        self.script_path = Path(__file__).parent / "trigger-monitor.py"
        self.logs_dir = Path(".agents/logs/scheduled")
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def run_monitoring(self, report_type: str = "daily"):
        """Запуск мониторинга с указанным типом отчета"""
        try:
            logger.info(f"Запуск мониторинга ({report_type})...")

            # Создаем лог-файл для этого запуска
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.logs_dir / f"monitor_{report_type}_{timestamp}.log"

            # Запускаем скрипт мониторинга
            cmd = [sys.executable, str(self.script_path), f"--{report_type}"]

            with open(log_file, "w") as f:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=Path.cwd()
                )

                # Записываем вывод в лог-файл
                f.write(f"Команда: {' '.join(cmd)}\n")
                f.write(f"Время: {datetime.now().isoformat()}\n")
                f.write(f"Код возврата: {result.returncode}\n")
                f.write("\n=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)

            if result.returncode == 0:
                logger.info(f"Мониторинг ({report_type}) успешно завершен")
                return True
            else:
                logger.error(
                    f"Мониторинг ({report_type}) завершился с ошибкой: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Ошибка при запуске мониторинга: {e}")
            return False

    def run_hourly(self):
        """Ежечасный мониторинг"""
        return self.run_monitoring("hourly")

    def run_daily(self):
        """Ежедневный мониторинг"""
        return self.run_monitoring("daily")

    def run_weekly(self):
        """Еженедельный мониторинг"""
        return self.run_monitoring("weekly")

    def run_monthly(self):
        """Ежемесячный мониторинг"""
        return self.run_monitoring("monthly")

    def setup_schedule(self):
        """Настройка расписания"""
        logger.info("Настройка расписания мониторинга...")

        # Ежечасный мониторинг (в 0 минут каждого часа)
        schedule.every().hour.at(":00").do(self.run_hourly)
        logger.info("  Ежечасный мониторинг: каждый час в :00")

        # Ежедневный мониторинг (в 9:00 утра)
        schedule.every().day.at("09:00").do(self.run_daily)
        logger.info("  Ежедневный мониторинг: каждый день в 09:00")

        # Еженедельный мониторинг (в понедельник в 10:00)
        schedule.every().monday.at("10:00").do(self.run_weekly)
        logger.info("  Еженедельный мониторинг: каждый понедельник в 10:00")

        # Ежемесячный мониторинг (1-го числа в 11:00) - используем 30 дней
        schedule.every(30).days.at("11:00").do(self.run_monthly)
        logger.info("  Ежемесячный мониторинг: каждые 30 дней в 11:00")

        # Тестовый запуск при старте
        schedule.every(1).minutes.do(self.run_test)
        logger.info("  Тестовый запуск: каждую минуту (для отладки)")

    def run_test(self):
        """Тестовый запуск (для отладки)"""
        logger.debug("Тестовый запуск планировщика...")
        return True

    def run_once(self, report_type: str = "daily"):
        """Однократный запуск мониторинга"""
        logger.info(f"Однократный запуск мониторинга ({report_type})...")
        return self.run_monitoring(report_type)

    def start(self, run_once: bool = False, report_type: str = None):
        """Запуск планировщика"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК ПЛАНИРОВЩИКА МОНИТОРИНГА")
        logger.info("=" * 60)

        if run_once and report_type:
            # Однократный запуск
            success = self.run_once(report_type)
            return success
        else:
            # Непрерывный режим
            self.setup_schedule()

            logger.info("\nПланировщик запущен. Ожидание выполнения задач...")
            logger.info("Нажмите Ctrl+C для остановки\n")

            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\nПланировщик остановлен пользователем")
                return True


def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Планировщик автоматического мониторинга триггеров"
    )
    parser.add_argument("--once", action="store_true", help="Однократный запуск")
    parser.add_argument(
        "--type",
        choices=["hourly", "daily", "weekly", "monthly"],
        default="daily",
        help="Тип отчета для однократного запуска",
    )
    parser.add_argument("--daemon", action="store_true", help="Запуск в режиме демона")
    parser.add_argument("--test", action="store_true", help="Тестовый запуск")

    args = parser.parse_args()

    monitor = ScheduledMonitor()

    if args.test:
        # Тестовый запуск
        print("Тестовый запуск планировщика...")
        monitor.setup_schedule()
        print("Расписание настроено:")
        for job in schedule.get_jobs():
            print(f"  {job}")
        return

    if args.once:
        # Однократный запуск
        success = monitor.start(run_once=True, report_type=args.type)
        sys.exit(0 if success else 1)
    else:
        # Непрерывный режим
        monitor.start()


if __name__ == "__main__":
    main()
