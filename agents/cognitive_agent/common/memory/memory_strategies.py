"""
Memory Strategies Module
Стратегии управления памятью для Cognitive Agent
"""

from abc import ABC, abstractmethod
from typing import Any


class MemoryStrategy(ABC):
    """Базовый класс стратегии управления памятью"""

    @abstractmethod
    def name(self) -> str:
        """Название стратегии"""
        pass

    @abstractmethod
    def on_access(self, key: str, entry: Any) -> None:
        """Вызывается при доступе к записи"""
        pass

    @abstractmethod
    def on_add(self, key: str, entry: Any) -> None:
        """Вызывается при добавлении записи"""
        pass

    @abstractmethod
    def on_remove(self, key: str) -> None:
        """Вызывается при удалении записи"""
        pass

    @abstractmethod
    def should_evict(self, memory_size: int, max_size: int) -> str | None:
        """
        Определить, нужно ли извлечь запись

        Args:
            memory_size: Текущий размер памяти
            max_size: Максимальный размер

        Returns:
            Ключ записи для извлечения или None
        """
        pass


class LRUMemoryStrategy(MemoryStrategy):
    """LRU (Least Recently Used) стратегия"""

    def __init__(self, max_size: int = 100):
        """
        Инициализация LRU стратегии

        Args:
            max_size: Максимальное количество записей
        """
        self.max_size = max_size
        self._access_order: list[str] = []

    def name(self) -> str:
        return "lru"

    def on_access(self, key: str, entry: Any) -> None:
        """Обновить порядок доступа"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def on_add(self, key: str, entry: Any) -> None:
        """Добавить в порядок доступа"""
        if key not in self._access_order:
            self._access_order.append(key)

    def on_remove(self, key: str) -> None:
        """Удалить из порядка доступа"""
        if key in self._access_order:
            self._access_order.remove(key)

    def should_evict(self, memory_size: int, max_size: int) -> str | None:
        """Извлечь наименее недавно используемую запись"""
        if memory_size > self.max_size and self._access_order:
            return self._access_order[0]
        return None

    def get_lru_key(self) -> str | None:
        """Получить ключ наименее недавно используемой записи"""
        if self._access_order:
            return self._access_order[0]
        return None


class FIFOMemoryStrategy(MemoryStrategy):
    """FIFO (First In, First Out) стра��егия"""

    def __init__(self, max_size: int = 100):
        """
        Инициализация FIFO стратегии

        Args:
            max_size: Максимальное количество записей
        """
        self.max_size = max_size
        self._add_order: list[str] = []

    def name(self) -> str:
        return "fifo"

    def on_access(self, key: str, entry: Any) -> None:
        """FIFO не меняется при доступе"""
        pass

    def on_add(self, key: str, entry: Any) -> None:
        """Добавить в порядок добавления"""
        if key not in self._add_order:
            self._add_order.append(key)

    def on_remove(self, key: str) -> None:
        """Удалить из порядка добавления"""
        if key in self._add_order:
            self._add_order.remove(key)

    def should_evict(self, memory_size: int, max_size: int) -> str | None:
        """Извлечь самую старую запись"""
        if memory_size > self.max_size and self._add_order:
            return self._add_order[0]
        return None

    def get_fifo_key(self) -> str | None:
        """Получить ключ самой старой записи"""
        if self._add_order:
            return self._add_order[0]
        return None


class LFUMemoryStrategy(MemoryStrategy):
    """LFU (Least Frequently Used) стратегия"""

    def __init__(self, max_size: int = 100):
        """
        Инициализация LFU стратегии

        Args:
            max_size: Максимальное количество записей
        """
        self.max_size = max_size
        self._access_count: dict[str, int] = {}

    def name(self) -> str:
        return "lfu"

    def on_access(self, key: str, entry: Any) -> None:
        """Увеличить счетчик доступа"""
        self._access_count[key] = self._access_count.get(key, 0) + 1

    def on_add(self, key: str, entry: Any) -> None:
        """Инициализировать счетчик доступа"""
        if key not in self._access_count:
            self._access_count[key] = 0

    def on_remove(self, key: str) -> None:
        """Удалить счетчик доступа"""
        if key in self._access_count:
            del self._access_count[key]

    def should_evict(self, memory_size: int, max_size: int) -> str | None:
        """Извлечь наименее часто используемую запись"""
        if memory_size > self.max_size and self._access_count:
            return min(self._access_count, key=self._access_count.get)
        return None

    def get_lfu_key(self) -> str | None:
        """Получить ключ наименее часто используемой записи"""
        if self._access_count:
            return min(self._access_count, key=self._access_count.get)
        return None


class PriorityMemoryStrategy(MemoryStrategy):
    """Стратегия с приоритетами"""

    def __init__(self, max_size: int = 100):
        """
        Инициализация стратегии с приоритетами

        Args:
            max_size: Максимальное количество записей
        """
        self.max_size = max_size
        self._priority: dict[str, int] = {}

    def name(self) -> str:
        return "priority"

    def on_access(self, key: str, entry: Any) -> None:
        """Приоритет не меняется при доступе"""
        pass

    def on_add(self, key: str, entry: Any) -> None:
        """Установить приоритет по умолчанию"""
        if key not in self._priority:
            self._priority[key] = 0

    def on_remove(self, key: str) -> None:
        """Удалить приоритет"""
        if key in self._priority:
            del self._priority[key]

    def set_priority(self, key: str, priority: int) -> None:
        """Установить приоритет для записи"""
        self._priority[key] = priority

    def get_priority(self, key: str) -> int:
        """Получить приоритет записи"""
        return self._priority.get(key, 0)

    def should_evict(self, memory_size: int, max_size: int) -> str | None:
        """Извлечь запись с самым низким приоритетом"""
        if memory_size > self.max_size and self._priority:
            return min(self._priority, key=self._priority.get)
        return None

    def get_lowest_priority_key(self) -> str | None:
        """Получить ключ записи с самым низким приоритетом"""
        if self._priority:
            return min(self._priority, key=self._priority.get)
        return None


class MemoryStrategyFactory:
    """Фабрика стратегий управления памятью"""

    _strategies: dict[str, type] = {
        "lru": LRUMemoryStrategy,
        "fifo": FIFOMemoryStrategy,
        "lfu": LFUMemoryStrategy,
        "priority": PriorityMemoryStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str, **kwargs) -> MemoryStrategy:
        """
        Создать стратегию по имени

        Args:
            strategy_name: Имя стратегии (lru, fifo, lfu, priority)
            **kwargs: Аргументы для конструктора стратегии

        Returns:
            Экземпляр стратегии

        Raises:
            ValueError: Если стратегия не найдена
        """
        strategy_name = strategy_name.lower()

        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown memory strategy: {strategy_name}. " f"Available: {list(cls._strategies.keys())}")

        return cls._strategies[strategy_name](**kwargs)

    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """Получить список доступных стратегий"""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type) -> None:
        """
        Зарегистрировать новую стратегию

        Args:
            name: Имя стратегии
            strategy_class: Класс стратегии
        """
        cls._strategies[name.lower()] = strategy_class


__all__ = [
    "MemoryStrategy",
    "LRUMemoryStrategy",
    "FIFOMemoryStrategy",
    "LFUMemoryStrategy",
    "PriorityMemoryStrategy",
    "MemoryStrategyFactory",
]
