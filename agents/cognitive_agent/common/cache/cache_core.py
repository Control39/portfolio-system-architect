"""
Cache Core Module
Базовая логика кэширования для Cognitive Agent
"""

import hashlib
import json
import logging
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CacheEntry:
    """Запись в кэше"""

    def __init__(self, key: str, value: Any, ttl: int | None = None):
        """
        Инициализация записи в кэше

        Args:
            key: Ключ записи
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.updated_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Проверить, истек ли срок действия записи"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ttl": self.ttl,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheEntry":
        """Создать из словаря"""
        entry = cls(key=data["key"], value=data["value"], ttl=data.get("ttl"))
        entry.created_at = data.get("created_at", entry.created_at)
        entry.updated_at = data.get("updated_at", entry.updated_at)
        return entry


class BaseCache:
    """Базовый класс кэша"""

    def __init__(self, name: str = "base_cache"):
        """
        Инициализация кэша

        Args:
            name: Имя кэша для логирования
        """
        self.name = name
        self._store: dict[str, CacheEntry] = {}

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
            logger.debug(f"Cache entry expired: {key}")
            del self._store[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Установить значение по ключу

        Args:
            key: Ключ
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
        """
        entry = CacheEntry(key=key, value=value, ttl=ttl)
        self._store[key] = entry
        logger.debug(f"Cache entry set: {key}")

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
            logger.debug(f"Cache entry deleted: {key}")
            return True
        return False

    def clear(self) -> None:
        """Очистить весь кэш"""
        self._store.clear()
        logger.debug(f"Cache cleared: {self.name}")

    def size(self) -> int:
        """Получить размер кэша (количество записей)"""
        return len(self._store)

    def keys(self) -> list:
        """Получить все ключи"""
        return list(self._store.keys())

    def __contains__(self, key: str) -> bool:
        """Проверить наличие ключа"""
        return key in self._store and not self._store[key].is_expired()

    def __len__(self) -> int:
        """Получить размер кэша"""
        return self.size()


class FileCache(BaseCache):
    """Файловый кэш"""

    def __init__(self, cache_dir: Path, name: str = "file_cache"):
        """
        Инициализация файлового кэша

        Args:
            cache_dir: Директория для хранения кэша
            name: Имя кэша для логирования
        """
        super().__init__(name)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_files()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Установить значение по ключу и сохранить в файл"""
        super().set(key, value, ttl)
        self._save_to_file(key)

    def get(self, key: str) -> Any | None:
        """Получить значение по ключу (с проверки файла)"""
        # Проверить файл
        file_path = self._get_file_path(key)
        if file_path.exists():
            self._load_from_file(key)

        return super().get(key)

    def delete(self, key: str) -> bool:
        """Удалить запись по ключу и удалить файл"""
        result = super().delete(key)
        if result:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
        return result

    def clear(self) -> None:
        """Очистить кэш и удалить все файлы"""
        super().clear()
        for file_path in self.cache_dir.glob("*.json"):
            file_path.unlink()

    def _get_file_path(self, key: str) -> Path:
        """Получить путь к файлу для ключа"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def _save_to_file(self, key: str) -> None:
        """Сохранить запись в файл"""
        if key not in self._store:
            return

        entry = self._store[key]
        file_path = self._get_file_path(key)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache entry {key}: {e}")

    def _load_from_file(self, key: str) -> CacheEntry | None:
        """Загрузить запись из файла"""
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                entry = CacheEntry.from_dict(data)
                self._store[key] = entry
                return entry
        except Exception as e:
            logger.error(f"Failed to load cache entry {key}: {e}")
            return None

    def _load_from_files(self) -> None:
        """Загрузить все записи из файлов"""
        for file_path in self.cache_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    entry = CacheEntry.from_dict(data)
                    self._store[entry.key] = entry
            except Exception as e:
                logger.error(f"Failed to load cache file {file_path}: {e}")


class TTLCache(BaseCache):
    """Кэш с TTL для всех записей"""

    def __init__(self, default_ttl: int = 3600, name: str = "ttl_cache"):
        """
        Инициализация TTL кэша

        Args:
            default_ttl: Время жизни по умолчанию в секундах (1 час)
            name: Имя кэша для логирования
        """
        super().__init__(name)
        self.default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Установить значение по ключу с использованием TTL"""
        if ttl is None:
            ttl = self.default_ttl
        super().set(key, value, ttl)

    def cleanup(self) -> int:
        """
        Очистить истекшие записи

        Returns:
            Количество удаленных записей
        """
        expired_keys = [key for key, entry in self._store.items() if entry.is_expired()]

        for key in expired_keys:
            del self._store[key]

        logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries")
        return len(expired_keys)


def cached(ttl: int | None = None, cache_name: str = "default_cache"):
    """
    Декоратор для кэширования результатов функций

    Args:
        ttl: Time-to-live в секундах (None = бесконечно)
        cache_name: Имя кэша

    Returns:
        Декоратор
    """
    cache = TTLCache(name=cache_name)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создать ключ из аргументов
            key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Попробовать получить из кэша
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_value

            # Вызвать функцию и сохранить в кэш
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss for {key}, result cached")

            return result

        return wrapper

    return decorator


# Глобальный кэш для приложений
global_cache = TTLCache(default_ttl=3600, name="global_cache")


def with_cache(cache_name: str = "default", ttl: int | None = None):
    """
    Декоратор для кэширования результатов функций

    Args:
        cache_name: Имя кэша для использования
        ttl: Time-to-live в секундах (None = бесконечно)

    Returns:
        Декоратор
    """

    def decorator(func: Callable) -> Callable:
        cache_instance = global_cache  # Используем глобальный кэш по умолчанию

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создать ключ из аргументов
            key = f"{cache_name}:{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Попробовать получить из кэша
            cached_value = cache_instance.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {key}")
                return cached_value

            # Вызвать функцию и сохранить в кэш
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            logger.debug(f"Cache miss for {key}, result cached")

            return result

        return wrapper

    return decorator


class MemoryAwareCache(BaseCache):
    """
    Кэш с учетом использования памяти

    Отслеживает размер данных в памяти и автоматически удаляет старые записи
    при превышении лимитов.
    """

    def __init__(
        self,
        max_size: int = 100 * 1024 * 1024,
        max_items: int = 1000,
        ttl: int | None = None,
        name: str = "memory_aware_cache",
    ):
        """
        Инициализация кэша с учетом памяти

        Args:
            max_size: Максимальный размер кэша в байтах (по умолчанию 100MB)
            max_items: Максимальное количество элементов (по умолчанию 1000)
            ttl: Time-to-live по умолчанию в секундах (None = бесконечно)
            name: Имя кэша для логирования
        """
        super().__init__(name)
        self.max_size = max_size
        self.max_items = max_items
        self.default_ttl = ttl
        self._current_size = 0
        self._access_times: dict[str, float] = {}  # Для LRU eviction

    def _estimate_size(self, value: Any) -> int:
        """
        Оценить размер объекта в памяти

        Args:
            value: Значение для оценки

        Returns:
            Примерный размер в байтах
        """
        try:
            import sys

            return sys.getsizeof(value)
        except Exception:
            # Fallback: базовая оценка
            return 1024  # 1KB по умолчанию

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        Установить значение по ключу с контролем памяти

        Args:
            key: Ключ
            value: Значение
            ttl: Time-to-live в секундах (None = использовать default_ttl)

        Returns:
            True если значение успешно установлено, False если значение слишком большое
        """
        if ttl is None:
            ttl = self.default_ttl

        # Оценить размер нового значения
        value_size = self._estimate_size(value)

        # Если значение больше максимального размера, отклонить
        if value_size > self.max_size:
            logger.warning(f"MemoryAwareCache: value too large ({value_size} bytes > {self.max_size} bytes max)")
            return False

        # Если ключ уже существует, вычесть старый размер
        if key in self._store:
            old_entry = self._store[key]
            old_size = self._estimate_size(old_entry.value)
            self._current_size -= old_size

        # Проверить лимиты и выполнить eviction если нужно
        while (self._current_size + value_size > self.max_size or len(self._store) >= self.max_items) and self._store:
            self._evict_one()

        # Добавить новую запись
        entry = CacheEntry(key=key, value=value, ttl=ttl)
        self._store[key] = entry
        self._current_size += value_size
        self._access_times[key] = time.time()

        logger.debug(f"MemoryAwareCache set: {key} ({value_size} bytes, total: {self._current_size} bytes)")
        return True

    def get(self, key: str) -> Any | None:
        """
        Получить значение по ключу с обновлением времени доступа

        Args:
            key: Ключ

        Returns:
            Значение или None
        """
        value = super().get(key)
        if value is not None:
            self._access_times[key] = time.time()
        return value

    def delete(self, key: str) -> bool:
        """
        Удалить запись по ключу с освобождением памяти

        Args:
            key: Ключ

        Returns:
            True, если запись удалена
        """
        if key in self._store:
            entry = self._store[key]
            size = self._estimate_size(entry.value)
            self._current_size -= size
            del self._store[key]
            if key in self._access_times:
                del self._access_times[key]
            logger.debug(f"MemoryAwareCache delete: {key} (freed {size} bytes)")
            return True
        return False

    def clear(self) -> None:
        """Очистить весь кэш и сбросить счетчик памяти"""
        super().clear()
        self._current_size = 0
        self._access_times.clear()
        logger.debug("MemoryAwareCache cleared (freed all memory)")

    def _evict_one(self) -> None:
        """
        Удалить один элемент из кэша (LRU - Least Recently Used)

        Выбирает наименее недавно использованный элемент для удаления.
        """
        if not self._store:
            return

        # Найти наименее недавно использованный ключ
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])

        # Также проверить на истекшие записи
        expired_keys = [k for k, v in self._store.items() if v.is_expired()]
        if expired_keys:
            # Приоритет: удалить истекшие записи
            lru_key = expired_keys[0]

        self.delete(lru_key)

    def cleanup(self) -> int:
        """
        Очистить истекшие записи

        Returns:
            Количество удаленных записей
        """
        expired_keys = [key for key, entry in self._store.items() if entry.is_expired()]

        for key in expired_keys:
            self.delete(key)

        logger.debug(f"MemoryAwareCache cleanup: removed {len(expired_keys)} expired entries")
        return len(expired_keys)

    def _cleanup_expired(self) -> int:
        """
        Внутренний метод для очистки истекших записей (алиас для cleanup)

        Returns:
            Количество удаленных записей
        """
        return self.cleanup()

    @property
    def current_size(self) -> int:
        """Получить текущий размер кэша в байтах"""
        return self._current_size

    @property
    def utilization(self) -> float:
        """Получить процент использования памяти (0.0 - 1.0)"""
        if self.max_size == 0:
            return 0.0
        return min(1.0, self._current_size / self.max_size)


class LRUCache(BaseCache):
    """
    Простой LRU (Least Recently Used) кэш

    Автоматически удаляет наименее недавно использованные элементы
    при превышении максимального размера.
    """

    def __init__(self, maxsize: int = 128, name: str = "lru_cache"):
        """
        Инициализация LRU кэша

        Args:
            maxsize: Максимальное количество элементов в кэше
            name: Имя кэша для логирования
        """
        super().__init__(name)
        self.maxsize = maxsize
        self._order: list = []  # Порядок доступа для LRU

    def get(self, key: str) -> Any | None:
        """
        Получить значение по ключу с обновлением порядка доступа

        Args:
            key: Ключ

        Returns:
            Значение или None
        """
        value = super().get(key)
        if value is not None:
            # Обновить порядок доступа - переместить в конец
            if key in self._order:
                self._order.remove(key)
            self._order.append(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Установить значение по ключу с контролем размера

        Args:
            key: Ключ
            value: Значение
            ttl: Time-to-live в секундах (None = бесконечно)
        """
        # Если ключ уже есть, обновить его
        if key in self._store:
            super().set(key, value, ttl)
            # Обновить порядок доступа
            if key in self._order:
                self._order.remove(key)
            self._order.append(key)
            return

        # Если достигнут лимит, удалить самый старый
        while len(self._store) >= self.maxsize and self._order:
            oldest_key = self._order.pop(0)
            super().delete(oldest_key)

        # Добавить новый элемент
        super().set(key, value, ttl)
        self._order.append(key)

    def delete(self, key: str) -> bool:
        """
        Удалить запись по ключу

        Args:
            key: Ключ

        Returns:
            True, если запись удалена
        """
        result = super().delete(key)
        if result and key in self._order:
            self._order.remove(key)
        return result

    def clear(self) -> None:
        """Очистить весь кэш"""
        super().clear()
        self._order.clear()
