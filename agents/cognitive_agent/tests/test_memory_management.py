"""
Тесты для системы управления памятью и кэшированием Cognitive Agent
"""

import time

import pytest

from agents.cognitive_agent.common import (
    CacheManager,
    LazyLoader,
    LRUCache,
    MemoryAwareCache,
    MemoryManager,
    MemoryMonitor,
    get_cache_manager,
    get_memory_manager,
    with_cache,
    with_memory_limit,
)


class TestMemoryManagement:
    """
    Тесты для системы управления памятью и кэшированием
    """

    def test_memory_aware_cache_basic_operations(self):
        """Тест основных операций MemoryAwareCache"""
        cache = MemoryAwareCache(max_size=1024 * 1024, max_items=10)  # 1MB

        # Тест установки значения
        result = cache.set("key1", "value1")
        assert result is True

        # Тест получения значения
        value = cache.get("key1")
        assert value == "value1"

        # Тест удаления значения
        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

    def test_memory_aware_cache_size_limit(self):
        """Тест ограничения размера MemoryAwareCache"""
        cache = MemoryAwareCache(max_size=100, max_items=10)  # Очень маленький лимит

        # Установить небольшое значение - должно пройти
        small_value = "small"
        result = cache.set("small", small_value)
        assert result is True

        # Установить большое значение - должно отклониться
        large_value = "x" * 200  # Больше лимита
        result = cache.set("large", large_value)
        assert result is False

    def test_memory_aware_cache_ttl(self):
        """Тест времени жизни элементов MemoryAwareCache"""
        cache = MemoryAwareCache(max_size=1024 * 1024, max_items=10, ttl=1)  # 1 секунда

        cache.set("expiring_key", "expiring_value")
        assert cache.get("expiring_key") == "expiring_value"

        # Подождать больше времени жизни
        time.sleep(2)
        assert cache.get("expiring_key") is None

    def test_lru_cache_operations(self):
        """Тест операций LRUCache"""
        cache = LRUCache(maxsize=3)

        # Заполнить кэш
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Проверить, что все есть
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Добавить еще один - должен вытеснить самый старый
        cache.set("key4", "value4")

        # Теперь key1 должен быть вытеснен
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"

    def test_cache_manager_functionality(self):
        """Тест функциональности CacheManager"""
        cache_manager = CacheManager()

        # Получить кэши
        project_cache = cache_manager.get_project_cache()
        file_cache = cache_manager.get_file_cache()
        ai_cache = cache_manager.get_ai_response_cache()
        search_cache = cache_manager.get_search_cache()

        # Проверить, что они существуют
        assert project_cache is not None
        assert file_cache is not None
        assert ai_cache is not None
        assert search_cache is not None

        # Тест установки значения в один из кэшей
        result = project_cache.set("test_key", "test_value")
        assert result is True

        # Проверить статистику
        stats = cache_manager.get_stats()
        assert "project_cache" in stats

    def test_memory_monitor_functionality(self):
        """Тест функциональности MemoryMonitor"""
        monitor = MemoryMonitor()

        # Получить информацию о памяти
        memory_info = monitor.get_memory_usage()

        assert "process_memory_mb" in memory_info
        assert "process_percent" in memory_info
        assert "system_percent" in memory_info
        assert memory_info["process_memory_mb"] >= 0
        assert 0 <= memory_info["process_percent"] <= 1

        # Проверить тренд
        trend = monitor.get_memory_trend()
        assert trend in ["increasing", "decreasing", "stable"]

    def test_memory_manager_functionality(self):
        """Тест функциональности MemoryManager"""
        memory_manager = MemoryManager(max_memory_percent=0.9)  # Высокий лимит для тестов

        # Проверить статус памяти
        status = memory_manager.get_memory_status()
        assert "memory_info" in status
        assert "max_allowed_percent" in status

        # Проверить, что очистка памяти работает
        memory_manager.cleanup_memory()

        # Проверить проверку использования памяти
        result = memory_manager.check_memory_usage()
        # Может вернуть True или False в зависимости от текущего состояния

    def test_lazy_loader_functionality(self):
        """Тест функциональности LazyLoader"""
        load_counter = 0

        def loader_func():
            nonlocal load_counter
            load_counter += 1
            return f"loaded_value_{load_counter}"

        lazy_loader = LazyLoader(loader_func)

        # Значение не должно быть загружено сразу
        assert load_counter == 0

        # При первом обращении должно загрузиться
        value1 = lazy_loader.get()
        assert value1 == "loaded_value_1"
        assert load_counter == 1

        # При втором обращении не должно загружаться снова
        value2 = lazy_loader.get()
        assert value2 == "loaded_value_1"
        assert load_counter == 1  # Счетчик не изменился

        # После сброса и повторной загрузки должно быть новое значение
        lazy_loader.reset()
        value3 = lazy_loader.get()
        assert value3 == "loaded_value_2"
        assert load_counter == 2

    def test_global_managers_access(self):
        """Тест доступа к глобальным менеджерам"""
        cache_manager = get_cache_manager()
        memory_manager = get_memory_manager()

        assert cache_manager is not None
        assert memory_manager is not None
        assert isinstance(cache_manager, CacheManager)
        assert isinstance(memory_manager, MemoryManager)

    def test_with_cache_decorator(self):
        """Тест декоратора with_cache"""
        call_count = 0

        @with_cache(ttl=10)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов - функция должна выполниться
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с теми же аргументами - результат должен быть из кэша
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1  # Счетчик не изменился

    def test_with_memory_limit_decorator(self):
        """Тест декоратора with_memory_limit"""

        @with_memory_limit(max_memory_mb=100)
        def test_function():
            return "success"

        # Функция должна выполниться успешно
        result = test_function()
        assert result == "success"

    def test_memory_aware_cache_cleanup(self):
        """Тест очистки устаревших элементов в MemoryAwareCache"""
        cache = MemoryAwareCache(max_size=1024 * 1024, max_items=10, ttl=1)

        cache.set("expiring1", "value1")
        cache.set("expiring2", "value2")

        # Оба значения должны быть доступны
        assert cache.get("expiring1") == "value1"
        assert cache.get("expiring2") == "value2"

        # Подождать, пока они не истекут
        time.sleep(2)

        # Вызвать внутреннюю очистку
        cache._cleanup_expired()

        # Значения должны быть удалены
        assert cache.get("expiring1") is None
        assert cache.get("expiring2") is None

    def test_memory_manager_with_callbacks(self):
        """Тест MemoryManager с коллбэками очистки"""
        cleanup_called = False

        def cleanup_callback():
            nonlocal cleanup_called
            cleanup_called = True

        memory_manager = MemoryManager()
        memory_manager.register_cleanup_callback(cleanup_callback)

        # Выполнить очистку
        memory_manager.cleanup_memory()

        # Проверить, что коллбэк был вызван
        assert cleanup_called is True

        # Отменить регистрацию
        result = memory_manager.unregister_cleanup_callback(cleanup_callback)
        assert result is True

    def test_cache_manager_memory_monitoring(self):
        """Тест мониторинга памяти в CacheManager"""
        cache_manager = CacheManager()

        # Установить значение в кэш
        cache_manager.get_ai_response_cache().set("test", "value")

        # Получить информацию об использовании памяти
        memory_info = cache_manager.monitor_memory_usage()

        assert "total_current_size" in memory_info
        assert "total_max_size" in memory_info
        assert "individual_caches" in memory_info
        assert memory_info["total_utilization"] >= 0


if __name__ == "__main__":
    pytest.main([__file__])
