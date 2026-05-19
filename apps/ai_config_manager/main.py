"""
AI Config Manager — Централизованное управление конфигурациями

Единая точка конфигурации для всех 15 микросервисов:
- Загрузка YAML конфигураций
- Hot reload
- Валидация схем
- Environment-specific конфиги (dev/staging/prod)
"""

import logging

from fastapi import FastAPI
from pydantic import BaseModel

from ai_config_manager.config_integration import get_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="AI Config Manager",
    description="Централизованное управление конфигурациями всех сервисов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ConfigSection(BaseModel):
    """Секция конфигурации"""

    name: str
    value: dict | str | int | float | bool
    description: str | None = None


class ServiceConfig(BaseModel):
    """Конфигурация сервиса"""

    service_name: str
    enabled: bool
    settings: dict
    dependencies: list[str] | None = None


class ConfigValidationResult(BaseModel):
    """Результат валидации конфигурации"""

    valid: bool
    errors: list[str]
    warnings: list[str]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Config Manager",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-config-manager"}


@app.get("/api/v1/config", response_model=dict)
async def get_full_config():
    """Получение полной конфигурации"""
    config = get_config()
    return config.get_config()


@app.get("/api/v1/config/sections", response_model=list[ConfigSection])
async def list_config_sections():
    """Список всех секций конфигурации"""
    config = get_config()
    full_config = config.get_config()

    sections = []
    for key, value in full_config.items():
        if isinstance(value, dict):
            sections.append(ConfigSection(name=key, value=value, description=f"Секция {key}"))
        else:
            sections.append(ConfigSection(name=key, value=value, description=f"Параметр {key}"))

    return sections


@app.get("/api/v1/config/{section_name}", response_model=dict)
async def get_section(section_name: str):
    """Получение секции конфигурации"""
    config = get_config()
    full_config = config.get_config()

    if section_name not in full_config:
        return {"error": f"Section '{section_name}' not found"}, 404

    return full_config[section_name]


@app.get("/api/v1/services", response_model=list[ServiceConfig])
async def list_services():
    """Список всех сконфигурированных сервисов"""
    config = get_config()
    services_config = config.get_config().get("services", {})

    services = []
    for name, settings in services_config.items():
        services.append(
            ServiceConfig(
                service_name=name,
                enabled=settings.get("enabled", True),
                settings=settings,
                dependencies=settings.get("dependencies", []),
            )
        )

    return services


@app.get("/api/v1/services/{service_name}", response_model=ServiceConfig)
async def get_service_config(service_name: str):
    """Конфигурация конкретного сервиса"""
    config = get_config()
    services_config = config.get_config().get("services", {})

    if service_name not in services_config:
        return {"error": f"Service '{service_name}' not found"}, 404

    settings = services_config[service_name]
    return ServiceConfig(
        service_name=service_name,
        enabled=settings.get("enabled", True),
        settings=settings,
        dependencies=settings.get("dependencies", []),
    )


@app.post("/api/v1/config/reload")
async def reload_config():
    """Перезагрузка конфигурации (hot reload)"""
    config = get_config()
    config.reload()
    logger.info("Configuration reloaded successfully")
    return {"status": "reloaded", "message": "Configuration reloaded successfully"}


@app.post("/api/v1/config/validate")
async def validate_config():
    """Валидация конфигурации"""
    config = get_config()

    try:
        full_config = config.get_config()
        errors = []
        warnings = []

        # Проверка обязательных секций
        required_sections = ["ai", "services", "logging"]
        for section in required_sections:
            if section not in full_config:
                errors.append(f"Missing required section: {section}")

        # Проверка сервисов
        services = full_config.get("services", {})
        if not services:
            warnings.append("No services configured")

        # Проверка AI конфигурации
        ai_config = full_config.get("ai", {})
        if not ai_config.get("default_model"):
            warnings.append("No default AI model configured")

        return ConfigValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    except Exception as e:
        return ConfigValidationResult(valid=False, errors=[str(e)], warnings=[])


@app.post("/api/v1/config/services/{service_name}/enable")
async def enable_service(service_name: str):
    """Включение сервиса"""
    config = get_config()
    config.update_service(service_name, {"enabled": True})
    logger.info(f"Service '{service_name}' enabled")
    return {"service": service_name, "enabled": True}


@app.post("/api/v1/config/services/{service_name}/disable")
async def disable_service(service_name: str):
    """Отключение сервиса"""
    config = get_config()
    config.update_service(service_name, {"enabled": False})
    logger.info(f"Service '{service_name}' disabled")
    return {"service": service_name, "enabled": False}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8100)
