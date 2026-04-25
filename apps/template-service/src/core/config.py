"""
Модуль конфигурации приложения.

Обеспечивает загрузку настроек из переменных окружения и конфигурационных файлов.
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения.

    Значения загружаются из переменных окружения с префиксом TEMPLATE_.
    """

    # Основные настройки
    app_name: str = Field(default="Template Service", env="TEMPLATE_APP_NAME")
    app_version: str = Field(default="0.1.0", env="TEMPLATE_APP_VERSION")
    environment: str = Field(default="development", env="TEMPLATE_ENVIRONMENT")
    debug: bool = Field(default=True, env="TEMPLATE_DEBUG")
    log_level: str = Field(default="INFO", env="TEMPLATE_LOG_LEVEL")

    # Настройки сервера
    host: str = Field(default="0.0.0.0", env="TEMPLATE_HOST")
    port: int = Field(default=8000, env="TEMPLATE_PORT")

    # Настройки CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="TEMPLATE_CORS_ORIGINS",
    )

    # Настройки базы данных
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/template_db",
        env="TEMPLATE_DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, env="TEMPLATE_DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="TEMPLATE_DATABASE_MAX_OVERFLOW")

    # Настройки Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="TEMPLATE_REDIS_URL",
    )
    redis_pool_size: int = Field(default=10, env="TEMPLATE_REDIS_POOL_SIZE")

    # Настройки безопасности
    secret_key: str = Field(
        default="change-this-in-production",
        env="TEMPLATE_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", env="TEMPLATE_JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, env="TEMPLATE_JWT_EXPIRE_MINUTES")

    # Настройки внешних API
    external_api_base_url: str = Field(
        default="https://api.example.com",
        env="TEMPLATE_EXTERNAL_API_BASE_URL",
    )
    external_api_timeout: int = Field(default=30, env="TEMPLATE_EXTERNAL_API_TIMEOUT")

    # Настройки мониторинга
    sentry_dsn: str = Field(default="", env="TEMPLATE_SENTRY_DSN")
    prometheus_metrics_enabled: bool = Field(
        default=True,
        env="TEMPLATE_PROMETHEUS_METRICS_ENABLED",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()

