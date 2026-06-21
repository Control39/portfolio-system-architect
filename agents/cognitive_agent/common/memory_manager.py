"""
Адаптер для управления памятью Cognitive Agent

Предоставляет обратно совместимый интерфейс для модуля memory/
Модуль memory/ содержит:
- memory_core.py: Базовые классы памяти (BaseMemory, ShortTermMemory, LongTermMemory, WorkingMemory)
- memory_strategies.py: Стратегии управления памятью (LRU, FIFO, LFU, Priority)
- memory_validators.py: Валидаторы памяти (Size, Type, Pattern, Custom)
"""

import gc
import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Any

import psutil

from .base_logger import BaseLogger
from .exceptions import ResourceExhaustionError

# Импорт модуля memory/


class MemoryMonitor:
    """
    Мониторинг использования памяти
    Адаптер для интеграции с системой мониторинга
    """

    def __init__(self, logger: BaseLogger | None = None):
        """
        Инициализировать монитор памяти

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or BaseLogger("MemoryMonitor")
        self.process = psutil.Process()

        # История использования памяти
        self.memory_history = deque(maxlen=100)  # Хранить последние 100 измерений

        # Пороги для предупреждений
        self.warning_threshold = 0.8  # 80% от лимита
        self.critical_threshold = 0.95  # 95% от лимита

        self.logger.info("Монитор памяти инициализирован")

    def get_memory_usage(self) -> dict[str, float]:
        """
        Получить текущее использование памяти

        Returns:
            Словарь с информацией об использовании памяти
        """
        try:
            # Получить использование памяти процесса
            process_memory = self.process.memory_info().rss  # Resident Set Size

            # Получить общую информацию о памяти системы
            system_memory = psutil.virtual_memory()

            # Вычислить использование в процентах
            process_percent = process_memory / system_memory.total
            system_percent = system_memory.percent

            # Сохранить в историю
            self.memory_history.append(
                {
                    "timestamp": time.time(),
                    "process_memory_mb": process_memory / (1024 * 1024),
                    "process_percent": process_percent,
                    "system_percent": system_percent,
                }
            )

            return {
                "process_memory_mb": process_memory / (1024 * 1024),
                "process_percent": process_percent,
                "system_percent": system_percent,
                "available_memory_mb": system_memory.available / (1024 * 1024),
                "total_memory_mb": system_memory.total / (1024 * 1024),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о памяти: {str(e)}")
            return {
                "process_memory_mb": 0,
                "process_percent": 0,
                "system_percent": 0,
                "available_memory_mb": 0,
                "total_memory_mb": 0,
            }

    def is_memory_low(self, threshold: float = 0.1) -> bool:
        """
        Проверить, мало ли свободной памяти

        Args:
            threshold: Порог в процентах (по умолчанию 10%)

        Returns:
            Мало ли свободной памяти
        """
        try:
            system_memory = psutil.virtual_memory()
            return system_memory.available / system_memory.total < threshold
        except Exception as e:
            self.logger.error(f"Ошибка проверки доступности памяти: {str(e)}")
            return False

    def get_memory_trend(self) -> str:
        """
        Получить тренд использования памяти

        Returns:
            Тренд ('increasing', 'decreasing', 'stable')
        """
        if len(self.memory_history) < 2:
            return "stable"

        recent_samples = list(self.memory_history)[-10:]  # Последние 10 измерений
        if len(recent_samples) < 2:
            return "stable"

        first_sample = recent_samples[0]["process_percent"]
        last_sample = recent_samples[-1]["process_percent"]

        if last_sample > first_sample * 1.1:  # Рост более чем на 10%
            return "increasing"
        elif last_sample < first_sample * 0.9:  # Снижение более чем на 10%
            return "decreasing"
        else:
            return "stable"


class MemoryManager:
    """
    Менеджер управления памятью для агента
    Адаптер для интеграции с системой управления памятью
    """

    def __init__(
        self,
        max_memory_percent: float = 0.8,  # 80% от доступной памяти
        logger: BaseLogger | None = None,
    ):
        """
        Инициализировать менеджер памяти

        Args:
            max_memory_percent: Максимальный процент использования памяти
            logger: Логгер для записи событий
        """
        self.max_memory_percent = max_memory_percent
        self.logger = logger or BaseLogger("MemoryManager")
        self.monitor = MemoryMonitor(logger=self.logger)

        # Коллбэки для очистки памяти
        self.cleanup_callbacks = []

        # Счетчики
        self.cleanup_count = 0
        self.gc_count = 0

        # Блокировка для потокобезопасности
        self._lock = threading.RLock()

        self.logger.info(f"Менеджер памяти инициализирован, макс. использование: {max_memory_percent*100}%")

    def register_cleanup_callback(self, callback: Callable[[], None]):
        """
        Зарегистрировать коллбэк для очистки памяти

        Args:
            callback: Функция для вызова при необходимости очистки памяти
        """
        with self._lock:
            self.cleanup_callbacks.append(callback)
            self.logger.debug(
                f"Зарегистрирован коллбэк очистки памяти: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}"
            )

    def unregister_cleanup_callback(self, callback: Callable[[], None]) -> bool:
        """
        Отменить регистрацию коллбэка для очистки памяти

        Args:
            callback: Функция для отмены регистрации

        Returns:
            Успешно ли отменена регистрация
        """
        with self._lock:
            try:
                self.cleanup_callbacks.remove(callback)
                self.logger.debug(
                    f"Отменена регистрация коллбэка очистки памяти: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}"
                )
                return True
            except ValueError:
                return False

    def cleanup_memory(self):
        """
        Очистить память
        """
        with self._lock:
            self.logger.info("Запуск очистки памяти")

            # Вызвать все коллбэки очистки
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                    self.logger.debug(
                        f"Вызван коллбэк очистки: {callback.__name__ if hasattr(callback, '__name__') else str(callback)}"
                    )
                except Exception as e:
                    self.logger.error(f"Ошибка в коллбэке очистки памяти {callback}: {str(e)}")

            # Выполнить сборку мусора
            collected = gc.collect()
            self.gc_count += 1
            self.cleanup_count += 1

            self.logger.info(f"Очистка памяти завершена, собрано объектов: {collected}, итераций GC: {self.gc_count}")

    def check_memory_usage(self) -> bool:
        """
        Проверить использование памяти и выполнить очистку при необходимости

        Returns:
            Требовалась ли очистка памяти
        """
        memory_info = self.monitor.get_memory_usage()

        # Проверить, превышено ли максимальное использование
        if memory_info["process_percent"] > self.max_memory_percent:
            self.logger.warning(
                f"Превышено максимальное использование памяти: {memory_info['process_percent']*100:.2f}%",
                max_allowed=self.max_memory_percent * 100,
                current_usage=memory_info["process_percent"] * 100,
            )

            self.cleanup_memory()
            return True

        # Проверить тренд использования памяти
        trend = self.monitor.get_memory_trend()
        if trend == "increasing":
            # Если память увеличивается быстро, выполнить профилактическую очистку
            if memory_info["process_percent"] > self.max_memory_percent * 0.7:  # 70% от лимита
                self.logger.info("Обнаружен рост использования памяти, выполнение профилактической очистки")
                self.cleanup_memory()
                return True

        return False

    def get_memory_status(self) -> dict[str, Any]:
        """
        Получить статус использования памяти

        Returns:
            Словарь со статусом памяти
        """
        memory_info = self.monitor.get_memory_usage()

        return {
            "memory_info": memory_info,
            "max_allowed_percent": self.max_memory_percent,
            "cleanup_count": self.cleanup_count,
            "gc_count": self.gc_count,
            "trend": self.monitor.get_memory_trend(),
            "callbacks_registered": len(self.cleanup_callbacks),
            "memory_low": self.monitor.is_memory_low(),
        }

    def ensure_memory_available(self, required_mb: float) -> bool:
        """
        Убедиться, что доступно достаточное количество памяти

        Args:
            required_mb: Требуемое количество памяти в MB

        Returns:
            Доступно ли достаточное количество памяти
        """
        memory_info = self.monitor.get_memory_usage()

        required_bytes = required_mb * 1024 * 1024
        available_bytes = memory_info["available_memory_mb"] * 1024 * 1024

        if available_bytes < required_bytes:
            self.logger.warning(
                f"Недостаточно свободной памяти: требуется {required_mb}MB, доступно {memory_info['available_memory_mb']:.2f}MB"
            )

            # Попробовать очистить память
            self.cleanup_memory()

            # Проверить снова
            memory_info = self.monitor.get_memory_usage()
            available_bytes = memory_info["available_memory_mb"] * 1024 * 1024

            if available_bytes < required_bytes:
                self.logger.error(
                    f"После очистки все равно недостаточно памяти: требуется {required_mb}MB, доступно {memory_info['available_memory_mb']:.2f}MB"
                )
                return False

        return True

    def monitor_continuously(self, interval: int = 30):
        """
        Начать непрерывный мониторинг памяти в отдельном потоке

        Args:
            interval: Интервал проверки в секундах
        """

        def monitoring_loop():
            while True:
                try:
                    self.check_memory_usage()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Ошибка в цикле мониторинга памяти: {str(e)}")
                    time.sleep(interval)  # Продолжить даже при ошибке

        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        self.logger.info(f"Запущен непрерывный мониторинг памяти с интервалом {interval} секунд")


# Глобальный менеджер памяти
global_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """
    Получить глобальный менеджер памяти

    Returns:
        Глобальный менеджер памяти
    """
    return global_memory_manager


class LazyLoader:
    """
    Ленивый загрузчик для экономии памяти
    """

    def __init__(self, loader_func: Callable[[], Any], logger: BaseLogger | None = None):
        """
        Инициализировать ленивый загрузчик

        Args:
            loader_func: Функция для загрузки данных
            logger: Логгер для записи событий
        """
        self.loader_func = loader_func
        self.logger = logger or BaseLogger("LazyLoader")
        self._loaded_value = None
        self._is_loaded = False
        self._lock = threading.Lock()

    def get(self) -> Any:
        """
        Получить значение, загрузив его при необходимости

        Returns:
            Загруженное значение
        """
        if not self._is_loaded:
            with self._lock:
                if not self._is_loaded:
                    self.logger.debug("Ленивая загрузка данных")
                    self._loaded_value = self.loader_func()
                    self._is_loaded = True
                    self.logger.debug("Данные успешно загружены лениво")

        return self._loaded_value

    def reset(self):
        """
        Сбросить загруженное значение
        """
        with self._lock:
            self._loaded_value = None
            self._is_loaded = False
            self.logger.debug("Ленивая загрузка сброшена")


def with_memory_limit(max_memory_mb: float):
    """
    Декоратор для контроля использования памяти функцией

    Args:
        max_memory_mb: Максимальное использование памяти в MB
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            memory_manager = get_memory_manager()

            # Проверить, достаточно ли памяти
            if not memory_manager.ensure_memory_available(max_memory_mb):
                raise ResourceExhaustionError(
                    f"Недостаточно памяти для выполнения функции {func.__name__}",
                    details={"required_mb": max_memory_mb, "function": func.__name__},
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
