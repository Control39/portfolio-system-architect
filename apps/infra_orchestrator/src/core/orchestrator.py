from typing import Any

from pydantic import BaseModel


class ServiceConfig(BaseModel):
    name: str
    version: str
    enabled: bool = True
    settings: dict[str, Any] = {}


class Orchestrator:
    def __init__(self):
        self.services: dict[str, ServiceConfig] = {}

    def register_service(self, config: ServiceConfig) -> None:
        self.services[config.name] = config

    def get_service(self, name: str) -> ServiceConfig | None:
        return self.services.get(name)


__all__ = ["ServiceConfig", "Orchestrator"]
