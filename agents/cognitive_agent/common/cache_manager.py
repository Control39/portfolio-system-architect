"""
Cache Manager Module (Adapter)
Адаптер для старого кода, использующего cache_manager.py

Этот файл предоставляет обратную совместимость для кода,
который импортирует cache_manager напрямую.
"""

from .cache import (
    BaseCache,
    CacheEntry,
    CacheStrategy,
    CacheStrategyFactory,
    CacheValidator,
    CacheValidatorFactory,
    CustomValidator,
    FIFOStrategy,
    FileCache,
    FileValidator,
    HashValidator,
    LFUStrategy,
    LRUCache,
    LRUStrategy,
    MemoryAwareCache,
    PatternValidator,
    SizeValidator,
    TTLCache,
    TTLStrategy,
    TypeValidator,
    cached,
    default_validator,
    global_cache,
    with_cache,
)


class CacheManager:
    """
    Менеджер кэша для Cognitive Agent

    Предоставляет централизованный доступ к различным типам кэшей.
    """

    _instance = None

    def __init__(self):
        """Инициализация менеджера кэша"""
        # Кэш проекта - хранит результаты сканирования проекта
        self._project_cache = MemoryAwareCache(
            max_size=50 * 1024 * 1024,  # 50MB
            max_items=50,
            ttl=3600,  # 1 час
            name="project_cache",
        )

        # Кэш файлов - хранит содержимое файлов
        self._file_cache = MemoryAwareCache(
            max_size=10 * 1024 * 1024,  # 10MB
            max_items=100,
            ttl=300,  # 5 минут
            name="file_cache",
        )

        # Кэш AI ответов - хранит ответы от AI провайдеров
        self._ai_response_cache = MemoryAwareCache(
            max_size=20 * 1024 * 1024,  # 20MB
            max_items=200,
            ttl=7200,  # 2 часа
            name="ai_response_cache",
        )

        # Кэш поиска - хранит результаты поиска
        self._search_cache = MemoryAwareCache(
            max_size=15 * 1024 * 1024,  # 15MB
            max_items=150,
            ttl=1800,  # 30 минут
            name="search_cache",
        )

    @classmethod
    def get_instance(cls) -> "CacheManager":
        """Получить singleton экземпляр CacheManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_project_cache(self) -> MemoryAwareCache:
        """Получить кэш проекта"""
        return self._project_cache

    def get_file_cache(self) -> MemoryAwareCache:
        """Получить кэш файлов"""
        return self._file_cache

    def get_ai_response_cache(self) -> MemoryAwareCache:
        """Получить кэш AI ответов"""
        return self._ai_response_cache

    def get_search_cache(self) -> MemoryAwareCache:
        """Получить кэш поиска"""
        return self._search_cache

    def clear_all(self) -> None:
        """Очистить все кэши"""
        self._project_cache.clear()
        self._file_cache.clear()
        self._ai_response_cache.clear()
        self._search_cache.clear()

    def get_stats(self) -> dict:
        """Получить статистику использования кэшей"""
        return {
            "project_cache": {
                "size_bytes": self._project_cache.current_size,
                "items": len(self._project_cache),
                "utilization": self._project_cache.utilization,
            },
            "file_cache": {
                "size_bytes": self._file_cache.current_size,
                "items": len(self._file_cache),
                "utilization": self._file_cache.utilization,
            },
            "ai_response_cache": {
                "size_bytes": self._ai_response_cache.current_size,
                "items": len(self._ai_response_cache),
                "utilization": self._ai_response_cache.utilization,
            },
            "search_cache": {
                "size_bytes": self._search_cache.current_size,
                "items": len(self._search_cache),
                "utilization": self._search_cache.utilization,
            },
        }

    def monitor_memory_usage(self) -> dict:
        """
        Мониторить использование памяти всеми кэшами

        Returns:
            Словарь с информацией об использовании памяти
        """
        total_size = sum(
            [
                self._project_cache.current_size,
                self._file_cache.current_size,
                self._ai_response_cache.current_size,
                self._search_cache.current_size,
            ]
        )

        total_max_size = sum(
            [
                self._project_cache.max_size,
                self._file_cache.max_size,
                self._ai_response_cache.max_size,
                self._search_cache.max_size,
            ]
        )

        total_items = sum(
            [len(self._project_cache), len(self._file_cache), len(self._ai_response_cache), len(self._search_cache)]
        )

        # Вычислить общую утилизацию
        total_utilization = (total_size / total_max_size * 100) if total_max_size > 0 else 0.0

        return {
            "total_current_size": total_size,
            "total_max_size": total_max_size,
            "total_utilization": total_utilization,
            "total_items": total_items,
            "individual_caches": self.get_stats(),
        }


# Singleton instance
_cache_manager_instance = None


def get_cache_manager() -> CacheManager:
    """
    Получить глобальный экземпляр CacheManager (singleton)

    Returns:
        Экземпляр CacheManager
    """
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager.get_instance()
    return _cache_manager_instance


__all__ = [
    "CacheEntry",
    "BaseCache",
    "FileCache",
    "TTLCache",
    "MemoryAwareCache",
    "LRUCache",
    "CacheManager",
    "get_cache_manager",
    "cached",
    "global_cache",
    "with_cache",
    "CacheStrategy",
    "LRUStrategy",
    "FIFOStrategy",
    "LFUStrategy",
    "TTLStrategy",
    "CacheStrategyFactory",
    "CacheValidator",
    "SizeValidator",
    "TypeValidator",
    "HashValidator",
    "PatternValidator",
    "FileValidator",
    "CustomValidator",
    "CacheValidatorFactory",
    "default_validator",
]
