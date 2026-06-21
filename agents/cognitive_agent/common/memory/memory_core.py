"""
Memory Core Module
Базовая логика памяти для Cognitive Agent
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class MemoryEntry:
    """Запись в памяти"""

    def __init__(self, key: str, value: Any, ttl: int | None = None, priority: int = 0, tags: list[str] = None):
        """
        Инициализация записи в памяти

        Args:
            key: Ключ записи
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
            priority: Приоритет записи (0 = низкий, 10 = высокий)
            tags: Теги для фильтрации
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.updated_at = time.time()
        self.ttl = ttl
        self.priority = priority
        self.tags = tags or []

    def is_expired(self) -> bool:
        """Проверить, истек ли срок действия записи"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def matches_tags(self, tags: list[str]) -> bool:
        """Проверить, соответствует ли запись тегам"""
        if not tags:
            return True
        return any(tag in self.tags for tag in tags)

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ttl": self.ttl,
            "priority": self.priority,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        """Создать из словаря"""
        entry = cls(
            key=data["key"],
            value=data["value"],
            ttl=data.get("ttl"),
            priority=data.get("priority", 0),
            tags=data.get("tags", []),
        )
        entry.created_at = data.get("created_at", entry.created_at)
        entry.updated_at = data.get("updated_at", entry.updated_at)
        return entry


class BaseMemory:
    """Базовый класс памяти"""

    def __init__(self, name: str = "base_memory"):
        """
        Инициализация памяти

        Args:
            name: Имя памяти для логирования
        """
        self.name = name
        self._store: dict[str, MemoryEntry] = {}

    def get(self, key: str) -> Any | None:
        """
        Получить значение по ключу

        Args:
            key: Ключ

        Returns:
            Значение или None, если ключ не найден или срок действия истек
        """
        if key not in self._store:
            return None

        entry = self._store[key]
        if entry.is_expired():
            logger.debug(f"Memory entry expired: {key}")
            del self._store[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None, priority: int = 0, tags: list[str] = None) -> None:
        """
        Установить значение по ключу

        Args:
            key: Ключ
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
            priority: Приоритет записи (0 = низкий, 10 = высокий)
            tags: Теги для фильтрации
        """
        entry = MemoryEntry(key=key, value=value, ttl=ttl, priority=priority, tags=tags)
        self._store[key] = entry
        logger.debug(f"Memory entry set: {key}")

    def delete(self, key: str) -> bool:
        """
        Удалить запись по ключу

        Args:
            key: Ключ

        Returns:
            True, если запись удалена, False если ключ не найден
        """
        if key in self._store:
            del self._store[key]
            logger.debug(f"Memory entry deleted: {key}")
            return True
        return False

    def clear(self) -> None:
        """Очистить всю память"""
        self._store.clear()
        logger.debug(f"Memory cleared: {self.name}")

    def size(self) -> int:
        """Получить размер памяти (количество записей)"""
        return len(self._store)

    def keys(self) -> list:
        """Получить все ключи"""
        return list(self._store.keys())

    def get_by_tags(self, tags: list[str]) -> dict[str, Any]:
        """
        Получить записи по тегам

        Args:
            tags: Список тегов

        Returns:
            Словарь ключ-значение для совпадающих записей
        """
        result = {}
        for key, entry in self._store.items():
            if entry.matches_tags(tags) and not entry.is_expired():
                result[key] = entry.value
        return result

    def get_by_priority(self, min_priority: int = 0) -> dict[str, Any]:
        """
        Получить записи по минимальному приоритету

        Args:
            min_priority: Минимальный приоритет

        Returns:
            Словарь ключ-значение для записей с приоритетом >= min_priority
        """
        result = {}
        for key, entry in self._store.items():
            if entry.priority >= min_priority and not entry.is_expired():
                result[key] = entry.value
        return result

    def __contains__(self, key: str) -> bool:
        """Проверить наличие ключа"""
        return key in self._store and not self._store[key].is_expired()

    def __len__(self) -> int:
        """Получить размер памяти"""
        return self.size()


class ShortTermMemory(BaseMemory):
    """Краткосрочная память"""

    def __init__(self, default_ttl: int = 300, name: str = "short_term_memory"):
        """
        Инициализация краткосрочной памяти

        Args:
            default_ttl: Время жизни по умолчанию в секундах (5 минут)
            name: Имя памяти для логирования
        """
        super().__init__(name)
        self.default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: int | None = None, priority: int = 0, tags: list[str] = None) -> None:
        """Установить значение с использованием TTL"""
        if ttl is None:
            ttl = self.default_ttl
        super().set(key, value, ttl, priority, tags)


class LongTermMemory(BaseMemory):
    """Долгосрочная память"""

    def __init__(self, name: str = "long_term_memory"):
        """
        Инициализация долгосрочной памяти

        Args:
            name: Имя памяти для логирования
        """
        super().__init__(name)
        self._priority_store: dict[int, list[str]] = {}

    def set(self, key: str, value: Any, ttl: int | None = None, priority: int = 0, tags: list[str] = None) -> None:
        """Установить значение и обновить priority store"""
        super().set(key, value, ttl, priority, tags)

        # Обновить priority store
        if priority not in self._priority_store:
            self._priority_store[priority] = []
        if key not in self._priority_store[priority]:
            self._priority_store[priority].append(key)

    def get_highest_priority(self) -> Any | None:
        """Получить значение с самым высоким приоритетом"""
        if not self._priority_store:
            return None

        highest_priority = max(self._priority_store.keys())
        keys = self._priority_store[highest_priority]

        for key in keys:
            if key in self._store and not self._store[key].is_expired():
                return self._store[key].value

        return None

    def cleanup_expired(self) -> int:
        """
        Очистить истекшие записи

        Returns:
            Количество удаленных записей
        """
        expired_keys = [key for key, entry in self._store.items() if entry.is_expired()]

        for key in expired_keys:
            del self._store[key]

        # Обновить priority store
        for priority, keys in list(self._priority_store.items()):
            keys = [k for k in keys if k in self._store]
            if keys:
                self._priority_store[priority] = keys
            else:
                del self._priority_store[priority]

        logger.debug(f"Memory cleanup: removed {len(expired_keys)} expired entries")
        return len(expired_keys)


class WorkingMemory(BaseMemory):
    """Рабочая память с ограничением по размеру"""

    def __init__(self, max_size: int = 100, name: str = "working_memory"):
        """
        Инициализация рабочей памяти

        Args:
            max_size: Максимальное количество записей
            name: Имя памяти для логирования
        """
        super().__init__(name)
        self.max_size = max_size
        self._access_order: list[str] = []

    def set(self, key: str, value: Any, ttl: int | None = None, priority: int = 0, tags: list[str] = None) -> None:
        """Установить значение и обновить access order"""
        super().set(key, value, ttl, priority, tags)

        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        # Проверить размер
        if len(self._access_order) > self.max_size:
            self._evict_lru()

    def _evict_lru(self) -> str | None:
        """Извлечь наименее недавно используемую запись"""
        if self._access_order:
            key = self._access_order.pop(0)
            if key in self._store:
                del self._store[key]
            logger.debug(f"Working memory eviction: {key}")
            return key
        return None

    def get_lru_key(self) -> str | None:
        """Получить ключ наименее недавно используемой записи"""
        if self._access_order:
            return self._access_order[0]
        return None


class MemoryManager:
    """Менеджер памяти для всего агента"""

    def __init__(self, logger=None):
        """
        Инициализация менеджера памяти

        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger or logging.getLogger(__name__)

        # Различные типы памяти
        self.short_term = ShortTermMemory(default_ttl=300)
        self.long_term = LongTermMemory()
        self.working = WorkingMemory(max_size=100)

        self.logger.info("Менеджер памяти инициализирован")

    def get(self, key: str) -> Any | None:
        """
        Получить значение из любой памяти

        Args:
            key: Ключ

        Returns:
            Значение или None
        """
        # Проверить рабочую память
        value = self.working.get(key)
        if value is not None:
            return value

        # Проверить краткосрочную память
        value = self.short_term.get(key)
        if value is not None:
            return value

        # Проверить долгосрочную память
        value = self.long_term.get(key)
        return value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        priority: int = 0,
        tags: list[str] = None,
        memory_type: str = "short_term",
    ) -> bool:
        """
        Установить значение в указанную память

        Args:
            key: Ключ
            value: Значение
            ttl: Time-to-live
            priority: Приоритет
            tags: Теги
            memory_type: Тип памяти (short_term, long_term, working)

        Returns:
            True, если успешно
        """
        if memory_type == "short_term":
            self.short_term.set(key, value, ttl, priority, tags)
        elif memory_type == "long_term":
            self.long_term.set(key, value, ttl, priority, tags)
        elif memory_type == "working":
            self.working.set(key, value, ttl, priority, tags)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

        return True

    def cleanup(self) -> dict[str, int]:
        """
        Очистить истекшие записи из всех памятей

        Returns:
            Словарь с количеством удаленных записей
        """
        return {
            "short_term": self.short_term.cleanup_expired(),
            "long_term": self.long_term.cleanup_expired(),
            "working": 0,  # Working memory очищается при добавлении
        }

    def get_stats(self) -> dict[str, Any]:
        """
        Получить статистику по всем памятям

        Returns:
            Словарь со статистикой
        """
        return {
            "short_term": {"size": self.short_term.size(), "type": "short_term"},
            "long_term": {"size": self.long_term.size(), "type": "long_term"},
            "working": {"size": self.working.size(), "max_size": self.working.max_size, "type": "working"},
        }
