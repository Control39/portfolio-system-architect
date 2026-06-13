"""
Тесты для ResourcePool.
"""

import pytest
from ai_config_manager.resource_pool import ResourcePool
from ai_config_manager.validators import ResourceConfig, ResourceType


class TestResourcePool:
    """Тесты для ResourcePool."""

    @pytest.fixture
    def resource_pool(self):
        """Создание экземпляра ResourcePool."""
        return ResourcePool()

    @pytest.fixture
    def sample_resource(self):
        """Пример ресурса."""
        return ResourceConfig(
            name="test-resource",
            type=ResourceType.TOOL,
            enabled=True,
            config={"key": "value"},
            metadata={"version": "1.0.0"},
        )

    def test_register_resource(self, resource_pool, sample_resource):
        """Регистрация ресурса."""
        resource_pool.register(sample_resource)

        assert "test-resource" in resource_pool
        assert len(resource_pool) == 1

        status = resource_pool.get_status("test-resource")
        assert status == "initialized"

    def test_unregister_resource(self, resource_pool, sample_resource):
        """Удаление ресурса."""
        resource_pool.register(sample_resource)
        resource_pool.unregister("test-resource")

        assert "test-resource" not in resource_pool
        assert len(resource_pool) == 0

    def test_connect_resource(self, resource_pool, sample_resource):
        """Подключение ресурса."""
        resource_pool.register(sample_resource)
        result = resource_pool.connect("test-resource")

        assert result is True
        assert resource_pool.get_status("test-resource") == "connected"

    def test_disconnect_resource(self, resource_pool, sample_resource):
        """Отключение ресурса."""
        resource_pool.register(sample_resource)
        resource_pool.connect("test-resource")
        resource_pool.disconnect("test-resource")

        assert resource_pool.get_status("test-resource") == "disconnected"

    def test_connect_nonexistent_resource(self, resource_pool):
        """Подключение несуществующего ресурса."""
        result = resource_pool.connect("nonexistent")
        assert result is False

    def test_get_resource(self, resource_pool, sample_resource):
        """Получение ресурса."""
        resource_pool.register(sample_resource)
        resource = resource_pool.get("test-resource")

        assert resource is not None
        assert resource["config"] == sample_resource

    def test_list_resources(self, resource_pool):
        """Получение списка ресурсов."""
        resource1 = ResourceConfig(name="resource1", type=ResourceType.TOOL, enabled=True)
        resource2 = ResourceConfig(name="resource2", type=ResourceType.MODEL, enabled=False)

        resource_pool.register(resource1)
        resource_pool.register(resource2)

        # Все ресурсы
        all_resources = resource_pool.list_resources()
        assert len(all_resources) == 2

        # Только включённые
        enabled_resources = resource_pool.list_resources(only_enabled=True)
        assert len(enabled_resources) == 1
        assert "resource1" in enabled_resources

        # По типу
        tool_resources = resource_pool.list_resources(resource_type=ResourceType.TOOL)
        assert len(tool_resources) == 1
        assert "resource1" in tool_resources

    def test_health_check(self, resource_pool, sample_resource):
        """Проверка здоровья ресурса."""
        resource_pool.register(sample_resource)

        # До подключения
        assert resource_pool.health_check("test-resource") is False

        # После подключения
        resource_pool.connect("test-resource")
        assert resource_pool.health_check("test-resource") is True

    def test_connect_all(self, resource_pool):
        """Подключение всех ресурсов."""
        resource1 = ResourceConfig(name="resource1", type=ResourceType.TOOL, enabled=True)
        resource2 = ResourceConfig(name="resource2", type=ResourceType.MODEL, enabled=True)

        resource_pool.register(resource1)
        resource_pool.register(resource2)

        results = resource_pool.connect_all()

        assert results["resource1"] is True
        assert results["resource2"] is True

    def test_disconnect_all(self, resource_pool):
        """Отключение всех ресурсов."""
        resource1 = ResourceConfig(name="resource1", type=ResourceType.TOOL, enabled=True)
        resource2 = ResourceConfig(name="resource2", type=ResourceType.MODEL, enabled=True)

        resource_pool.register(resource1)
        resource_pool.register(resource2)
        resource_pool.connect("resource1")
        resource_pool.connect("resource2")

        resource_pool.disconnect_all()

        assert resource_pool.get_status("resource1") == "disconnected"
        assert resource_pool.get_status("resource2") == "disconnected"

    def test_duplicate_registration(self, resource_pool, sample_resource):
        """Повторная регистрация ресурса."""
        resource_pool.register(sample_resource)
        resource_pool.register(sample_resource)  # Не должно вызвать ошибку

        assert len(resource_pool) == 1  # Всё ещё один ресурс
