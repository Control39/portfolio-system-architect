# apps/decision_engine/src/config/client.py
"""
Клиент для получения конфигурации из AI Config Manager.

Идея: мы хотим получить конфигурацию — но не знать,
как она работает внутри, и не зависеть от того, что там внутри.

Это называется — "не лезть в чужую кухню, а просто заказать еду".
"""

import json
from pathlib import Path
from typing import Any

import httpx  # ✅ Библиотека для HTTP-запросов (Async = не ждём, пока сервер ответит)


class ConfigClientError(Exception):
    """
    Кастомная ошибка.

    Why? Чтобы когда что-то пойдёт не так — мы могли
    поймать именно эту ошибку, а не "всё, что угодно".

    Пример:
        try:
            config = await client.get_config()
        except ConfigClientError as e:
            logger.error(f"Конфиг не загрузился: {e}")
            # Можно сделать fallback — например, читать из файла
    """

    pass


class ConfigClient:
    """
    Клиент для работы с конфигурацией.

    Ключевая идея:
    - Мы не импортируем "ConfigManager из ai_config_manager" —
    - Мы делаем HTTP-запрос к сервису AI Config Manager.

    Это значит:
    - Если AI Config Manager упал — мы НЕ упадём вместе с ним (есть fallback)
    - Если AI Config Manager поменял внутреннюю структуру — мы НЕ пострадаем (интерфейс стабилен)
    """

    def __init__(self, service_name: str, config_url: str | None = None):
        """
        Инициализация клиента.

        Args:
            service_name: Имя этого сервиса (например, "decision_engine").
                          AI Config Manager будет использовать его, чтобы отдать
                          ТОЛЬКО тот конфиг, который для нас.

            config_url: Адрес AI Config Manager.
                        По умолчанию — "http://ai_config_manager:8000".
                        Это имя сервиса из docker-compose.yml.

                        Why? Потому что в Docker Compose имена сервисов — это DNS-имена.
                        Ты не должна знать IP-адрес, только имя.
        """
        self.service_name = service_name
        # Если URL не передали — используем дефолт
        self.config_url = config_url or "http://ai_config_manager:8000"

        # Путь к локальному кэшу.
        # Why? Чтобы, если AI Config Manager упал, у нас был "запасной вариант".
        self.cache_path = Path(f".cache/{service_name}/config.json")

    async def get_config(self) -> dict[str, Any]:
        """
        Получить конфигурацию.

        Алгоритм:
        1. Попытаться получить через HTTP API (быстро, всегда актуально)
        2. Если не удалось — читать из локального кэша (медленно, но работает)
        3. Если нет ни того, ни другого — бросить ошибку

        Why async?
        Потому что HTTP-запросы — это I/O-операции (ждём сетевой ответ).
        Async позволяет другим задачам работать, пока мы ждём.

        Why not sync?
        В современных сервисах (FastAPI, Quart) лучше использовать async.
        """
        try:
            # 1. HTTP-запрос
            # Why AsyncClient?
            # Потому что в асинхронном коде sync-запросы "замораживают" весь процесс.
            async with httpx.AsyncClient(timeout=httpx.Timeout(1.0)) as client:
                # Формируем URL: /api/v1/config/{service_name}
                url = f"{self.config_url}/api/v1/config/{self.service_name}"

                # Делаем GET-запрос
                resp = await client.get(url)

                # Если ответ 4xx/5xx — вызвать исключение (и пойти в except)
                resp.raise_for_status()

                # Получаем JSON из ответа
                config = resp.json()

                # 2. Сохраняем в локальный кэш (на всякий случай)
                self._save_to_cache(config)

                # 3. Возвращаем конфиг
                return config

        except httpx.RequestError as e:
            # 4. Если HTTP-запрос не удался (сервер упал, сеть упала, таймаут)

            # Пытаемся читать из кэша
            config = self._load_from_cache()

            if config:
                # Кэш есть — возвращаем его. Это "режим деградации".
                return config

            # Если и кэша нет — бросаем ошибку с понятным сообщением
            raise ConfigClientError(
                f"Не удалось получить конфиг для '{self.service_name}': "
                f"AI Config Manager недоступен ({e}), локальный кэш отсутствует"
            ) from e

    def _save_to_cache(self, config: dict[str, Any]) -> None:
        """
        Приватный метод: сохранить конфиг в кэш.

        Why "private" (с нижним подчёркиванием)?
        Потому что это внутренняя логика, которую вызывает только get_config().
        Ты не будешь вызывать его напрямую — это не часть публичного API.
        """
        # Создать директорию .cache/decision_engine/, если её нет
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Записать JSON в файл (indent=2 для читаемости)
        self.cache_path.write_text(json.dumps(config, indent=2, default=str))

    def _load_from_cache(self) -> dict[str, Any] | None:
        """
        Приватный метод: загрузить конфиг из кэша.

        Returns:
            dict | None: Конфиг, если есть; None, если нет файла.
        """
        # Если файл существует — загрузить его
        if self.cache_path.exists():
            return json.loads(self.cache_path.read_text())

        # Иначе — None (ошибки не будет, просто "ничего нет")
        return None
