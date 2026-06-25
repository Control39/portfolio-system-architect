"""
Менеджер конфигураций AI-агентов с поддержкой hot reload.
"""

import asyncio
import json
import logging
import threading
from pathlib import Path
from typing import Any

import prometheus_client as prom
import toml
import yaml
from pydantic import ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .validators import AgentConfig, AIConfig, ResourceConfig

logger = logging.getLogger(__name__)

# Prometheus метрики
# В монорепозитории один и тот же модуль может импортироваться из разных точек.
# Чтобы избежать падений при повторной регистрации таймсерий в default CollectorRegistry,
# создаём метрики безопасно (при дублировании не падаем).


def _metric_or_existing(name: str) -> bool:
    """Проверяет, зарегистрирована ли метрика с указанным именем."""
    return name in prom.REGISTRY._names_to_collectors  # неофициальный API, но эффективный


def _get_counter(name: str, description: str, labelnames: list[str]):
    # prom.Counter при повторном создании может упасть из-за duplicated timeseries.
    # Поэтому сначала проверяем наличие метрики в REGISTRY.
    if _metric_or_existing(name):
        return prom.REGISTRY._names_to_collectors[name]
    try:
        return prom.Counter(name, description, labelnames)
    except ValueError:
        return prom.REGISTRY._names_to_collectors[name]


def _get_histogram(name: str, description: str, labelnames: list[str], buckets: tuple[float, ...]):
    if _metric_or_existing(name):
        return prom.REGISTRY._names_to_collectors[name]
    try:
        return prom.Histogram(name, description, labelnames, buckets=buckets)
    except ValueError:
        return prom.REGISTRY._names_to_collectors[name]


CONFIG_LOADS_TOTAL = _get_counter(
    "config_loads_total",
    "Total number of config loads",
    ["config_path"],
)
CONFIG_RELOADS_TOTAL = _get_counter(
    "config_reloads_total",
    "Total number of config reloads (hot reload)",
    ["config_path"],
)
CONFIG_LOAD_DURATION = _get_histogram(
    "config_load_duration_seconds",
    "Time spent loading config",
    ["config_path"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)
CONFIG_VALIDATION_ERRORS = _get_counter(
    "config_validation_errors_total",
    "Total number of config validation errors",
    ["config_path"],
)


class ConfigReloadHandler(FileSystemEventHandler):
    """Обработчик событий изменения файла конфигурации."""

    def __init__(self, config_manager: "ConfigManager"):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".yaml", ".yml", ".json", ".toml", ".env")):
            logger.info(f"Изменён файл конфигурации: {event.src_path}")
            self.config_manager.reload()


class ConfigManager:
    """
    Централизованный менеджер конфигураций AI-агентов.

    Поддерживает:
    - Загрузку из YAML/JSON/TOML/ENV
    - Hot reload (автоматическая перезагрузка при изменении файла)
    - Валидацию через Pydantic
    - Потокобезопасные операции
    - Prometheus метрики
    - Асинхронный интерфейс
    """

    # Поддерживаемые форматы файлов
    SUPPORTED_FORMATS = {
        ".yaml": lambda f: yaml.safe_load(f),
        ".yml": lambda f: yaml.safe_load(f),
        ".json": json.load,
        ".toml": lambda f: toml.load(f),
    }

    def __init__(self, config_path: str, auto_reload: bool = True, watch_dir: str | None = None):
        """
        Инициализация менеджера конфигураций.

        Args:
            config_path: Путь к файлу конфигурации (YAML/JSON/TOML)
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

    def _load_from_file(self, path: Path) -> dict[str, Any]:
        """
        Загрузка данных из файла с автоматическим определением формата.

        Args:
            path: Путь к файлу конфигурации

        Returns:
            dict[str, Any]: Распарсенные данные

        Raises:
            ValueError: Если формат файла не поддерживается
        """
        suffix = path.suffix.lower()
        loader = self.SUPPORTED_FORMATS.get(suffix)

        if not loader:
            raise ValueError(
                f"Неподдерживаемый формат файла: {suffix}. Поддерживаются: {list(self.SUPPORTED_FORMATS.keys())}"
            )

        with open(path, encoding="utf-8") as f:
            return loader(f)

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

        config_path_str = str(self._config_path)
        logger.info(f"Загрузка конфигурации из: {self._config_path}")

        # Метрики: начало загрузки
        CONFIG_LOADS_TOTAL.labels(config_path=config_path_str).inc()

        with self._lock, CONFIG_LOAD_DURATION.labels(config_path=config_path_str).time():
            try:
                data = self._load_from_file(self._config_path)

                self._config = AIConfig(**data)
                logger.info(
                    f"Конфигурация успешно загружена и валидирована: {len(self._config.agents)} агентов, "
                    f"{len(self._config.resources)} ресурсов"
                )
            except ValidationError as e:
                CONFIG_VALIDATION_ERRORS.labels(config_path=config_path_str).inc()
                logger.error(f"Ошибка валидации конфигурации: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации: {e}")
                raise

        return self._config

    def reload(self) -> AIConfig:
        """
        Динамическая перезагрузка конфигурации (hot reload).

        Returns:
            AIConfig: Обновлённая конфигурация
        """
        config_path_str = str(self._config_path)
        logger.info("Выполняется hot reload конфигурации...")
        CONFIG_RELOADS_TOTAL.labels(config_path=config_path_str).inc()
        return self.load()

    async def areload(self) -> AIConfig:
        """
        Асинхронная динамическая перезагрузка конфигурации (hot reload).

        Returns:
            AIConfig: Обновлённая конфигурация
        """
        config_path_str = str(self._config_path)
        logger.info("Выполняется async hot reload конфигурации...")
        CONFIG_RELOADS_TOTAL.labels(config_path=config_path_str).inc()
        return await self.aload()

    async def aload(self) -> AIConfig:
        """
        Асинхронная загрузка конфигурации.

        Returns:
            AIConfig: Валидированная конфигурация
        """
        return await asyncio.to_thread(self.load)

    async def aget_config(self) -> AIConfig:
        """
        Асинхронное получение текущей конфигурации.

        Returns:
            AIConfig: Текущая конфигурация
        """
        with self._lock:
            if self._config is None:
                raise RuntimeError("Конфигурация не загружена. Вызовите load() первым.")
            return self._config

    async def aget_agent_config(self, agent_name: str) -> AgentConfig:
        """
        Асинхронное получение конфигурации конкретного агента.

        Args:
            agent_name: Имя агента

        Returns:
            AgentConfig: Конфигурация агента
        """
        config = await self.aget_config()
        if agent_name not in config.agents:
            raise KeyError(f"Агент не найден: {agent_name}")
        return config.agents[agent_name]

    async def aupdate_agent_config(self, agent_name: str, updates: dict[str, Any]) -> None:
        """
        Асинхронное обновление конфигурации агента (в памяти, без сохранения на диск).

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

    def get_gigachat_token(self) -> str | None:
        """
        Получить токен GigaChat из настроек окружения.

        Returns:
            str | None: Токен GigaChat или None, если не настроен
        """
        import base64
        import os

        import requests

        # Получаем настройки из переменных окружения
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
        auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

        # Если есть готовый API ключ, возвращаем его
        api_key = os.getenv("GIGACHAT_API_KEY")
        if api_key:
            return api_key

        # Если настроены client_id и client_secret, получаем токен через OAuth
        if client_id and client_secret:
            try:
                # Подготовка заголовков и данных для запроса
                auth_string = f"{client_id}:{client_secret}"
                encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

                headers = {
                    "Authorization": f"Basic {encoded_auth}",
                    "Content-Type": "application/x-www-form-urlencoded",
                }

                data = {"scope": scope, "grant_type": "client_credentials"}

                # Отправляем запрос для получения токена
                response = requests.post(auth_url, headers=headers, data=data, timeout=10)

                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")

                    if access_token:
                        logger.info("Токен GigaChat успешно получен")
                        return access_token
                    else:
                        logger.error("В ответе отсутствует access_token")
                        return None
                else:
                    logger.error(f"Ошибка получения токена GigaChat: {response.status_code}, {response.text}")
                    return None
            except Exception as e:
                logger.error(f"Исключение при получении токена GigaChat: {e}")
                return None
        else:
            logger.warning("Не настроены учетные данные для GigaChat (GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET)")
            return None

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
