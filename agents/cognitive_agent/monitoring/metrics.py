"""Metrics collection module for cognitive agent."""

import statistics
from collections import deque


class MetricsCollector:
    """Сборщик метрик для enterprise-мониторинга"""

    def __init__(self):
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "ai_calls_made": 0,
            "ai_calls_failed": 0,
            "files_processed": 0,
            "scan_duration_history": deque(maxlen=100),
            "response_times": deque(maxlen=100),
            "error_rates": deque(maxlen=100),
            "cpu_usage_history": deque(maxlen=100),
            "memory_usage_history": deque(maxlen=100),
        }

    def record_task_completion(self, success: bool):
        """Зарегистрировать завершение задачи"""
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

    def record_ai_call(self, success: bool):
        """Зарегистрировать вызов AI"""
        self.metrics["ai_calls_made"] += 1
        if not success:
            self.metrics["ai_calls_failed"] += 1

    def record_file_processed(self, count: int = 1):
        """Зарегистрировать обработку файлов"""
        self.metrics["files_processed"] += count

    def record_scan_duration(self, duration: float):
        """Зарегистрировать длительность сканирования"""
        self.metrics["scan_duration_history"].append(duration)

    def record_response_time(self, response_time: float):
        """Зарегистрировать время ответа"""
        self.metrics["response_times"].append(response_time)

    def record_resource_usage(self, cpu_percent: float, memory_percent: float):
        """Зарегистрировать использование ресурсов"""
        self.metrics["cpu_usage_history"].append(cpu_percent)
        self.metrics["memory_usage_history"].append(memory_percent)

    def calculate_performance_metrics(self) -> dict:
        """Рассчитать показатели производительности"""
        metrics = {}

        # Процент успеха задач
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total_tasks > 0:
            metrics["task_success_rate"] = self.metrics["tasks_completed"] / total_tasks
        else:
            metrics["task_success_rate"] = 1.0

        # Процент успеха AI вызовов
        total_ai_calls = self.metrics["ai_calls_made"]
        if total_ai_calls > 0:
            success_calls = total_ai_calls - self.metrics["ai_calls_failed"]
            metrics["ai_call_success_rate"] = success_calls / total_ai_calls
        else:
            metrics["ai_call_success_rate"] = 1.0

        # Среднее время сканирования
        if self.metrics["scan_duration_history"]:
            metrics["avg_scan_duration"] = statistics.mean(self.metrics["scan_duration_history"])
            metrics["median_scan_duration"] = statistics.median(self.metrics["scan_duration_history"])
            metrics["max_scan_duration"] = max(self.metrics["scan_duration_history"])
            metrics["min_scan_duration"] = min(self.metrics["scan_duration_history"])
        else:
            metrics["avg_scan_duration"] = 0.0

        # Среднее время ответа
        if self.metrics["response_times"]:
            metrics["avg_response_time"] = statistics.mean(self.metrics["response_times"])
            metrics["median_response_time"] = statistics.median(self.metrics["response_times"])
        else:
            metrics["avg_response_time"] = 0.0

        # Скорость обработки файлов
        total_time = sum(self.metrics["scan_duration_history"]) or 1
        metrics["files_per_second"] = self.metrics["files_processed"] / total_time

        # Среднее использование ресурсов
        if self.metrics["cpu_usage_history"]:
            metrics["avg_cpu_usage"] = statistics.mean(self.metrics["cpu_usage_history"])
        else:
            metrics["avg_cpu_usage"] = 0.0

        if self.metrics["memory_usage_history"]:
            metrics["avg_memory_usage"] = statistics.mean(self.metrics["memory_usage_history"])
        else:
            metrics["avg_memory_usage"] = 0.0

        # Общая статистика
        metrics["total_tasks"] = total_tasks
        metrics["total_ai_calls"] = self.metrics["ai_calls_made"]
        metrics["total_files_processed"] = self.metrics["files_processed"]

        return metrics
