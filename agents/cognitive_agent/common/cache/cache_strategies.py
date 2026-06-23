"""
Cache Strategies Module
Стратегии кэширования для Cognitive Agent
"""

import logging
import time

logger = logging.getLogger(__name__)


class CacheStrategy:
    """Базовая стратегия кэширования"""

    def __init__(self, max_size: int = 1000):
        """
        Инициализация стратегии

        Args:
            max_size: Максимальное количество записей
        """
        self.max_size = max_size
        self._access_order: list[str] = []

    def on_access(self, key: str) -> None:
        """Вызывается при доступе к записи"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def on_insert(self, key: str) -> str | None:
        """Вызывается при вставке новой записи"""
        if len(self._access_order) >= self.max_size:
            return self._evict()
        self._access_order.append(key)
        return None

    def on_delete(self, key: str) -> None:
        """Вызывается при удалении записи"""
        if key in self._access_order:
            self._access_order.remove(key)

    def _evict(self) -> str | None:
        """
        Извлечь запись для замены

        Returns:
            Ключ извлекаемой записи или None
        """
        if self._access_order:
            return self._access_order.pop(0)
        return None

    def get_access_order(self) -> list[str]:
        """Получить порядок доступа к записям"""
        return self._access_order.copy()


class LRUStrategy(CacheStrategy):
    """LRU (Least Recently Used) стратегия"""

    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self._access_times: dict[str, float] = {}

    def on_access(self, key: str) -> None:
        """При доступе обновить время последнего использования"""
        self._access_times[key] = time.time()
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def on_insert(self, key: str) -> str | None:
        """При вставке использовать LRU для замены"""
        if len(self._access_order) >= self.max_size:
            return self._evict_lru()
        self._access_order.append(key)
        self._access_times[key] = time.time()
        return None

    def _evict_lru(self) -> str | None:
        """Извлечь наименее недавно используемую запись"""
        if not self._access_order:
            return None

        # Найти наименее недавно используемую запись
        lru_key = self._access_order[0]
        self._access_order.remove(lru_key)
        if lru_key in self._access_times:
            del self._access_times[lru_key]

        logger.debug(f"LRU eviction: {lru_key}")
        return lru_key

    def get_lru_key(self) -> str | None:
        """Получить ключ наименее недавно используемой записи"""
        if self._access_order:
            return self._access_order[0]
        return None


class FIFOStrategy(CacheStrategy):
    """FIFO (First In, First Out) стратегия"""

    def _evict(self) -> str | None:
        """Извлечь первую запись"""
        if self._access_order:
            key = self._access_order.pop(0)
            logger.debug(f"FIFO eviction: {key}")
            return key
        return None


class LFUStrategy(CacheStrategy):
    """LFU (Least Frequently Used) стратегия"""

    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self._access_count: dict[str, int] = {}

    def on_access(self, key: str) -> None:
        """При доступе увеличить счетчик"""
        self._access_count[key] = self._access_count.get(key, 0) + 1
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def on_insert(self, key: str) -> str | None:
        """При вставке использовать LFU для замены"""
        if len(self._access_order) >= self.max_size:
            return self._evict_lfu()
        self._access_order.append(key)
        self._access_count[key] = 0
        return None

    def _evict_lfu(self) -> str | None:
        """Извлечь наименее часто используемую запись"""
        if not self._access_count:
            return None

        # Найти наименее часто используемую запись
        lfu_key = min(self._access_count, key=self._access_count.get)
        self._access_order.remove(lfu_key)
        del self._access_count[lfu_key]

        logger.debug(f"LFU eviction: {lfu_key}")
        return lfu_key


class TTLStrategy:
    """Стратегия с Time-To-Live"""

    def __init__(self, default_ttl: int = 3600):
        """
        Инициализация TTL стратегии

        Args:
            default_ttl: Время жизни по умолчанию в секундах (1 час)
        """
        self.default_ttl = default_ttl
        self._creation_times: dict[str, float] = {}

    def set_ttl(self, key: str, ttl: int | None = None) -> None:
        """Установить TTL для записи"""
        if ttl is None:
            ttl = self.default_ttl
        self._creation_times[key] = (time.time(), ttl)

    def is_expired(self, key: str) -> bool:
        """Проверить, истек ли срок действия"""
        if key not in self._creation_times:
            return False

        created_at, ttl = self._creation_times[key]
        return time.time() - created_at > ttl

    def get_remaining_ttl(self, key: str) -> float | None:
        """Получить оставшееся время жизни"""
        if key not in self._creation_times:
            return None

        created_at, ttl = self._creation_times[key]
        remaining = ttl - (time.time() - created_at)
        return max(0, remaining)

    def cleanup_expired(self, keys: list[str]) -> list[str]:
        """
        Очистить истекшие записи

        Args:
            keys: Список ключей

        Returns:
            Список истекших ключей
        """
        expired = [key for key in keys if self.is_expired(key)]
        for key in expired:
            del self._creation_times[key]
        return expired


# Фабрика стратегий
class CacheStrategyFactory:
    """Фабрика для создания стратегий кэширования"""

    @staticmethod
    def create(strategy_name: str, **kwargs) -> CacheStrategy:
        """
        Создать стратегию по имени

        Args:
            strategy_name: Имя стратегии (lru, fifo, lfu)
            **kwargs: Параметры стратегии

        Returns:
            Экземпляр стратегии
        """
        strategies = {
            "lru": LRUStrategy,
            "fifo": FIFOStrategy,
            "lfu": LFUStrategy,
        }

        strategy_class = strategies.get(strategy_name.lower())
        if strategy_class is None:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return strategy_class(**kwargs)

    @staticmethod
    def get_available_strategies() -> list[str]:
        """Получить список доступных стратегий"""
        return ["lru", "fifo", "lfu"]
