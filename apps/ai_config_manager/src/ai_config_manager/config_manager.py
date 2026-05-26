"""
Менеджер конфигураций AI-агентов с поддержкой hot reload.
"""

import logging
import threading
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .validators import AgentConfig, AIConfig, ResourceConfig

logger = logging.getLogger(__name__)


class ConfigReloadHandler(FileSystemEventHandler):
    """Обработчик событий изменения файла конфигурации."""

    def __init__(self, config_manager: "ConfigManager"):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".yaml", ".yml", ".json")):
            logger.info(f"Изменён файл конфигурации: {event.src_path}")
            self.config_manager.reload()


class ConfigManager:
    """
    Централизованный менеджер конфигураций AI-агентов.

    Поддерживает:
    - Загрузку из YAML/JSON
    - Hot reload (автоматическая перезагрузка при изменении файла)
    - Валидацию через Pydantic
    - Потокобезопасные операции
    """

    def __init__(self, config_path: str, auto_reload: bool = True, watch_dir: str | None = None):
        """
        Инициализация менеджера конфигураций.

        Args:
            config_path: Путь к файлу конфигурации (YAML/JSON)
            auto_reload: Автоматически перезагружать конфиг при изменении
            watch_dir: Директория для наблюдения (по умолчанию - директория config_path)
        """
        self._config_path = Path(config_path)
        self._auto_reload = auto_reload
        self._watch_dir = Path(watch_dir) if watch_dir else self._config_path.parent

        self._config: AIConfig | None = None
        self._lock = threading.RLock()
        self._observer: Observer | None = None

        # Загрузка начальной конфигурации
        self.load()

        # Запуск наблюдателя за изменениями
        if auto_reload:
            self.start_watching()

    def load(self) -> AIConfig:
        """
        Загрузка конфигурации из файла.

        Returns:
            AIConfig: Валидированная конфигурация

        Raises:
            FileNotFoundError: Если файл конфигурации не найден
            ValidationError: Если конфигурация не проходит валидацию
        """
        if not self._config_path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {self._config_path}")

        logger.info(f"Загрузка конфигурации из: {self._config_path}")

        with self._lock:
            with open(self._config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            try:
                self._config = AIConfig(**data)
                logger.info(
                    f"Конфигурация успешно загружена и валидирована: {len(self._config.agents)} агентов, "
                    f"{len(self._config.resources)} ресурсов"
                )
            except ValidationError as e:
                logger.error(f"Ошибка валидации конфигурации: {e}")
                raise

        return self._config

    def reload(self) -> AIConfig:
        """
        Динамическая перезагрузка конфигурации (hot reload).

        Returns:
            AIConfig: Обновлённая конфигурация
        """
        logger.info("Выполняется hot reload конфигурации...")
        return self.load()

    def get_config(self) -> AIConfig:
        """
        Получить текущую конфигурацию.

        Returns:
            AIConfig: Текущая конфигурация
        """
        with self._lock:
            if self._config is None:
                raise RuntimeError("Конфигурация не загружена. Вызовите load() первым.")
            return self._config

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """
        Получить конфигурацию конкретного агента.

        Args:
            agent_name: Имя агента

        Returns:
            AgentConfig: Конфигурация агента

        Raises:
            KeyError: Если агент не найден
        """
        config = self.get_config()
        if agent_name not in config.agents:
            raise KeyError(f"Агент не найден: {agent_name}")
        return config.agents[agent_name]

    def get_resource_config(self, resource_name: str) -> ResourceConfig:
        """
        Получить конфигурацию конкретного ресурса.

        Args:
            resource_name: Имя ресурса

        Returns:
            ResourceConfig: Конфигурация ресурса

        Raises:
            KeyError: Если ресурс не найден
        """
        config = self.get_config()
        if resource_name not in config.resources:
            raise KeyError(f"Ресурс не найден: {resource_name}")
        return config.resources[resource_name]

    def update_agent_config(self, agent_name: str, updates: dict[str, Any]) -> None:
        """
        Обновить конфигурацию агента (в памяти, без сохранения на диск).

        Args:
            agent_name: Имя агента
            updates: Словарь обновлений
        """
        with self._lock:
            if self._config is None:
                raise RuntimeError("Конфигурация не загружена")

            if agent_name not in self._config.agents:
                raise KeyError(f"Агент не найден: {agent_name}")

            # Создание нового объекта с обновлениями
            current = self._config.agents[agent_name].model_dump()
            current.update(updates)
            self._config.agents[agent_name] = AgentConfig(**current)

        logger.info(f"Конфигурация агента {agent_name} обновлена")

    def start_watching(self) -> None:
        """Запуск наблюдения за изменениями файла конфигурации."""
        if self._observer is not None:
            return

        event_handler = ConfigReloadHandler(self)
        self._observer = Observer()
        self._observer.schedule(event_handler, str(self._watch_dir), recursive=False)
        self._observer.start()
        logger.info(f"Наблюдение за изменениями запущено в: {self._watch_dir}")

    def stop_watching(self) -> None:
        """Остановка наблюдения за изменениями."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Наблюдение за изменениями остановлено")

    def validate(self) -> bool:
        """
        Проверка валидности текущей конфигурации.

        Returns:
            bool: True если конфигурация валидна
        """
        try:
            self.get_config()
            return True
        except (ValidationError, RuntimeError):
            return False

    def __enter__(self):
        """Контекстный менеджер."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Остановка наблюдения при выходе из контекста."""
        self.stop_watching()
