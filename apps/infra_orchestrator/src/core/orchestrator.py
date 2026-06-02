from typing import Dict, Any, Optional
from pydantic import BaseModel

class ServiceConfig(BaseModel):
    name: str
    version: str
    enabled: bool = True
    settings: Dict[str, Any] = {}

class Orchestrator:
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
    
    def register_service(self, config: ServiceConfig) -> None:
        self.services[config.name] = config
    
    def get_service(self, name: str) -> Optional[ServiceConfig]:
        return self.services.get(name)

__all__ = ["ServiceConfig", "Orchestrator"]
