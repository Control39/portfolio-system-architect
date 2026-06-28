"""Сервис автоматического обновления GigaChat токенов."""

import logging
import os
import threading
import time
import uuid

import requests

logger = logging.getLogger(__name__)


class TokenRefreshService:
    """
    Сервис для автоматического обновления GigaChat токенов.

    Поддерживает:
    - OAuth OAuth через client_id/client_secret
    - RqUID и Accept заголовки для корректной работы API
    - Кэширование токена с expiry timestamp
    - Автоматическое обновление перед истечением (pre-refresh)
    - Thread-safe операции
    """

    # Время предварительного обновления (за 5 минут до истечения)
    REFRESH_BUFFER_SECONDS = 300

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        scope: str = "GIGACHAT_API_PERS",
    ):
        """
        Инициализация сервиса обновления токенов.

        Args:
            client_id: Client ID для OAuth
            client_secret: Client Secret для OAuth
            auth_url: URL endpoints для получения токена
            scope: Область действия токена
        """
        self.client_id = client_id or os.getenv("GIGACHAT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GIGACHAT_CLIENT_SECRET")
        self.auth_url = auth_url
        self.scope = scope
        self.verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

        self._token_cache: str | None = None
        self._expiry_time: float | None = None
        self._lock = threading.RLock()
        self._refresh_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        logger.info(f"TokenRefreshService инициализирован (verify_ssl={self.verify_ssl})")

    def _generate_rquid(self) -> str:
        """Генерирует уникальный RqUID для запроса."""
        return str(uuid.uuid4())

    def _is_token_expired(self) -> bool:
        """Проверяет, истёк ли токен или nearing expiry."""
        if self._token_cache is None:
            return True

        if self._expiry_time is None:
            # Если expiry не установлен, считаем токен важным и обновляем
            return False

        return time.time() + self.REFRESH_BUFFER_SECONDS >= self._expiry_time

    def _parse_expiry_from_token(self, token: str) -> float:
        """
        Парсит expiry time из JWT токена (кодирует data часть).

        Args:
            token: JWT токен

        Returns:
            float: Время истечения в epoch seconds
        """
        try:
            # JWT состоит из 3 частей: header.payload.signature
            parts = token.split(".")
            if len(parts) != 3:
                logger.warning("Токен не является валидным JWT")
                return time.time() + 1800  # Fallback: 30 минут

            # Декодируем payload (вторая часть)
            import base64

            payload = parts[1]
            # Добавляем padding если нужно
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding

            decoded = base64.urlsafe_b64decode(payload)
            import json

            payload_data = json.loads(decoded.decode("utf-8"))
            exp = payload_data.get("exp")

            if exp:
                return float(exp)
        except Exception as e:
            logger.warning(f"Ошибка парсинга expiry из токена: {e}")

        # Fallback: токен живёт 30 минут
        return time.time() + 1800

    def _fetch_token(self) -> str | None:
        """
        Получает новый токен через OAuth запрос.

        Returns:
            Optional[str]: Новый токен или None
        """
        if not self.client_id or not self.client_secret:
            logger.error("Не настроены учетные данные для GigaChat (GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET)")
            return None

        try:
            import base64

            # Формируем Basic auth header
            auth_string = f"{self.client_id}:{self.client_secret}"
            encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

            # Заголовки ОБЯЗАТЕЛЬНЫ: RqUID и Accept
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": self._generate_rquid(),
            }

            data = {"scope": self.scope, "grant_type": "client_credentials"}

            logger.info(f"Запрос нового токена GigaChat (RqUID={headers['RqUID']})")

            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data,
                timeout=10,
                verify=self.verify_ssl,
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")

                if access_token:
                    self._token_cache = access_token
                    self._expiry_time = self._parse_expiry_from_token(access_token)
                    logger.info(
                        f"Токен GigaChat успешно получен (expires in ~{int((self._expiry_time - time.time()) / 60)} мин)"
                    )
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

    def get_token(self, force_refresh: bool = False) -> str | None:
        """
        Получает текущий токен или обновляет его при необходимости.

        Args:
            force_refresh: Принудительно обновить токен

        Returns:
            Optional[str]: Токен или None
        """
        with self._lock:
            if force_refresh or self._is_token_expired():
                logger.info(f"Обновление токена (force={force_refresh}, expired={self._is_token_expired()})")
                new_token = self._fetch_token()
                if new_token:
                    return new_token
                elif self._token_cache:
                    # Если не удалось обновить, но есть кэш - возвращаем старый
                    logger.warning("Не удалось обновить токен, используется кэшированный")
                    return self._token_cache
                else:
                    return None

            return self._token_cache

    def start_auto_refresh(self, interval: int = 60):
        """
        Запускает фоновый поток для автоматического обновления токенов.

        Args:
            interval: Интервал проверки в секундах
        """
        if self._refresh_thread and self._refresh_thread.is_alive():
            logger.warning("Auto-refresh уже запущен")
            return

        self._stop_event.clear()
        self._refresh_thread = threading.Thread(target=self._refresh_loop, args=(interval,), daemon=True)
        self._refresh_thread.start()
        logger.info(f"Auto-refresh запущен (interval={interval}s)")

    def _refresh_loop(self, interval: int):
        """Цикл автоматического обновления."""
        while not self._stop_event.is_set():
            try:
                self.get_token()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле auto-refresh: {e}")
                time.sleep(interval)  # Не прерываем цикл при ошибке

    def stop_auto_refresh(self):
        """Останавливает фоновый поток auto-refresh."""
        self._stop_event.set()
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
            self._refresh_thread = None
        logger.info("Auto-refresh остановлен")

    def invalidate_token(self):
        """Инвалидирует текущий токен (принудительное обновление при следующем запросе)."""
        with self._lock:
            self._token_cache = None
            self._expiry_time = None
        logger.info("Токен инвалидирован")

    def get_token_info(self) -> dict:
        """
        Получает информацию о текущем токене.

        Returns:
            dict: Информация о токене
        """
        with self._lock:
            return {
                "has_token": self._token_cache is not None,
                "is_expired": self._is_token_expired(),
                "expiry_time": self._expiry_time,
                "time_remaining": (self._expiry_time - time.time() if self._expiry_time else None),
            }


# Глобальный экземпляр для удобства
_global_token_service: TokenRefreshService | None = None


def get_token_refresh_service() -> TokenRefreshService:
    """
    Получает глобальный экземпляр TokenRefreshService.

    Returns:
        TokenRefreshService: Глобальный сервис
    """
    global _global_token_service

    if _global_token_service is None:
        _global_token_service = TokenRefreshService()

    return _global_token_service


def reset_token_refresh_service():
    """Сбрасывает глобальный экземпляр (для тестирования)."""
    global _global_token_service
    _global_token_service = None
