"""
Менеджер пула ресурсов для AI-агентов.
"""

import logging
from threading import RLock
from typing import Any

from .validators import ResourceConfig, ResourceType

logger = logging.getLogger(__name__)


class ResourcePool:
    """
    Пул ресурсов для AI-агентов.

    Управляет жизненным циклом ресурсов (подключение, отключение, проверка состояния).
    Потокобезопасная реализация.
    """

    def __init__(self):
        """Инициализация пула ресурсов."""
        self._resources: dict[str, dict[str, Any]] = {}
        self._configs: dict[str, ResourceConfig] = {}
        self._lock = RLock()

    def register(self, resource_config: ResourceConfig) -> None:
        """
        Регистрация ресурса.

        Args:
            resource_config: Конфигурация ресурса
        """
        with self._lock:
            if resource_config.name in self._resources:
                logger.warning(f"Ресурс уже зарегистрирован: {resource_config.name}")
                return

            self._configs[resource_config.name] = resource_config
            self._resources[resource_config.name] = {
                "config": resource_config,
                "status": "initialized",
                "connected": False,
            }
            logger.info(
                f"Ресурс зарегистрирован: {resource_config.name} (тип: {resource_config.type.value})"
            )

    def unregister(self, resource_name: str) -> None:
        """
        Удаление ресурса.

        Args:
            resource_name: Имя ресурса
        """
        with self._lock:
            if resource_name not in self._resources:
                logger.warning(f"Ресурс не найден: {resource_name}")
                return

            self.disconnect(resource_name)
            del self._resources[resource_name]
            del self._configs[resource_name]
            logger.info(f"Ресурс удалён: {resource_name}")

    def connect(self, resource_name: str) -> bool:
        """
        Подключение ресурса.

        Args:
            resource_name: Имя ресурса

        Returns:
            bool: True если подключение успешно
        """
        with self._lock:
            if resource_name not in self._resources:
                logger.error(f"Ресурс не найден: {resource_name}")
                return False

            resource = self._resources[resource_name]
            if resource["connected"]:
                logger.warning(f"Ресурс уже подключён: {resource_name}")
                return True

            try:
                # Здесь должна быть логика подключения к реальному ресурсу
                # Например, установление соединения с БД, инициализация API-клиента и т.д.
                resource["status"] = "connected"
                resource["connected"] = True
                logger.info(f"Ресурс подключён: {resource_name}")
                return True
            except Exception as e:
                resource["status"] = "error"
                logger.error(f"Ошибка подключения ресурса {resource_name}: {e}")
                return False

    def disconnect(self, resource_name: str) -> None:
        """
        Отключение ресурса.

        Args:
            resource_name: Имя ресурса
        """
        with self._lock:
            if resource_name not in self._resources:
                return

            resource = self._resources[resource_name]
            if not resource["connected"]:
                return

            try:
                # Здесь должна быть логика отключения
                resource["status"] = "disconnected"
                resource["connected"] = False
                logger.info(f"Ресурс отключён: {resource_name}")
            except Exception as e:
                logger.error(f"Ошибка отключения ресурса {resource_name}: {e}")

    def get(self, resource_name: str) -> dict[str, Any] | None:
        """
        Получить ресурс.

        Args:
            resource_name: Имя ресурса

        Returns:
            Dict с ресурсом или None
        """
        with self._lock:
            return self._resources.get(resource_name)

    def get_config(self, resource_name: str) -> ResourceConfig | None:
        """
        Получить конфигурацию ресурса.

        Args:
            resource_name: Имя ресурса

        Returns:
            ResourceConfig или None
        """
        with self._lock:
            return self._configs.get(resource_name)

    def list_resources(
        self, resource_type: ResourceType | None = None, only_enabled: bool = False
    ) -> list[str]:
        """
        Получить список имён ресурсов.

        Args:
            resource_type: Фильтр по типу ресурса
            only_enabled: Только включённые ресурсы

        Returns:
            Список имён ресурсов
        """
        with self._lock:
            result = []
            for name, config in self._configs.items():
                if only_enabled and not config.enabled:
                    continue
                if resource_type and config.type != resource_type:
                    continue
                result.append(name)
            return result

    def get_status(self, resource_name: str) -> str | None:
        """
        Получить статус ресурса.

        Args:
            resource_name: Имя ресурса

        Returns:
            Статус ресурса или None
        """
        with self._lock:
            if resource_name not in self._resources:
                return None
            status: str = self._resources[resource_name]["status"]
            return status

    def health_check(self, resource_name: str) -> bool:
        """
        Проверка здоровья ресурса.

        Args:
            resource_name: Имя ресурса

        Returns:
            bool: True если ресурс здоров
        """
        with self._lock:
            if resource_name not in self._resources:
                return False

            resource = self._resources[resource_name]
            if not resource["connected"]:
                return False

            # Здесь должна быть реальная проверка здоровья
            # Например, ping к БД, запрос к API и т.д.
            is_healthy: bool = resource["status"] == "connected"
            return is_healthy

    def connect_all(self) -> dict[str, bool]:
        """
        Подключить все ресурсы.

        Returns:
            Словарь {имя_ресурса: успех_подключения}
        """
        results: dict[str, bool] = {}
        for name in list(self.list_resources(only_enabled=True)):
            results[name] = self.connect(name)
        return results

    def disconnect_all(self) -> None:
        """Отключить все ресурсы."""
        for name in list(self._resources.keys()):
            self.disconnect(name)

    def __len__(self) -> int:
        """Количество зарегистрированных ресурсов."""
        return len(self._resources)

    def __contains__(self, resource_name: str) -> bool:
        """Проверка наличия ресурса."""
        return resource_name in self._resources
