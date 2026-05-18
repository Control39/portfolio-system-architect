"""Infrastructure Orchestrator Core — Service deployment and management system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ServiceStatus(str, Enum):
    """Статус сервиса."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    SCALING = "scaling"


class ServiceType(str, Enum):
    """Тип сервиса."""
    API = "api"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    DATABASE = "database"
    CACHE = "cache"
    GATEWAY = "gateway"


@dataclass
class ServiceConfig:
    """Конфигурация сервиса."""
    name: str
    service_type: ServiceType
    image: str
    replicas: int = 1
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    environment: dict[str, str] = field(default_factory=dict)
    ports: dict[int, int] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    health_check_path: str = "/health"
    restart_policy: str = "always"


@dataclass
class ServiceInstance:
    """Экземпляр сервиса."""
    config: ServiceConfig
    status: ServiceStatus = ServiceStatus.PENDING
    deployed_at: datetime | None = None
    stopped_at: datetime | None = None
    current_replicas: int = 0
    health_status: str = "unknown"
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def deploy(self) -> None:
        """Задеплоить сервис."""
        self.status = ServiceStatus.DEPLOYING
        self.logs.append(f"[{datetime.now().isoformat()}] Starting deployment...")

    def start(self) -> None:
        """Запустить сервис."""
        if self.status in [ServiceStatus.PENDING, ServiceStatus.STOPPED, ServiceStatus.DEPLOYING]:
            self.status = ServiceStatus.RUNNING
            self.deployed_at = datetime.now()
            self.current_replicas = self.config.replicas
            self.logs.append(f"[{datetime.now().isoformat()}] Service started with {self.current_replicas} replicas")

    def stop(self) -> None:
        """Остановить сервис."""
        if self.status == ServiceStatus.RUNNING:
            self.status = ServiceStatus.STOPPED
            self.stopped_at = datetime.now()
            self.logs.append(f"[{datetime.now().isoformat()}] Service stopped")

    def fail(self, error: str) -> None:
        """Пометить сервис как неудачный."""
        self.status = ServiceStatus.FAILED
        self.logs.append(f"[{datetime.now().isoformat()}] ERROR: {error}")

    def scale(self, replicas: int) -> None:
        """Масштабировать сервис."""
        if self.status == ServiceStatus.RUNNING:
            self.status = ServiceStatus.SCALING
            self.current_replicas = replicas
            self.logs.append(f"[{datetime.now().isoformat()}] Scaling to {replicas} replicas")
            self.status = ServiceStatus.RUNNING

    def check_health(self) -> bool:
        """Проверить здоровье сервиса."""
        if self.status == ServiceStatus.RUNNING:
            self.health_status = "healthy"
            return True
        elif self.status == ServiceStatus.FAILED:
            self.health_status = "unhealthy"
            return False
        else:
            self.health_status = "unknown"
            return False


class InfrastructureOrchestrator:
    """Оркестратор инфраструктуры."""

    def __init__(self, cluster_name: str = "default"):
        self.cluster_name = cluster_name
        self.services: dict[str, ServiceInstance] = {}
        self.deployment_history: list[dict[str, Any]] = []
        self._counter = 0

    def register_service(
        self,
        name: str,
        service_type: ServiceType,
        image: str,
        replicas: int = 1,
        **kwargs: Any,
    ) -> ServiceInstance:
        """Зарегистрировать новый сервис."""
        config = ServiceConfig(
            name=name,
            service_type=service_type,
            image=image,
            replicas=replicas,
            **kwargs,
        )

        instance = ServiceInstance(config=config)
        self.services[name] = instance

        self._log_deployment(name, "registered")

        return instance

    def deploy_service(self, service_name: str) -> bool:
        """Развернуть сервис."""
        service = self.services.get(service_name)
        if not service:
            return False

        service.deploy()
        service.start()

        self._log_deployment(service_name, "deployed")

        return True

    def stop_service(self, service_name: str) -> bool:
        """Остановить сервис."""
        service = self.services.get(service_name)
        if not service:
            return False

        # Если сервис в состоянии DEPLOYING, сначала переведём в RUNNING
        if service.status == ServiceStatus.DEPLOYING:
            service.start()
        
        service.stop()

        self._log_deployment(service_name, "stopped")

        return True

    def scale_service(self, service_name: str, replicas: int) -> bool:
        """Масштабировать сервис."""
        service = self.services.get(service_name)
        if not service:
            return False

        # Если сервис не запущен, сначала запустим его
        if service.status != ServiceStatus.RUNNING:
            service.start()

        service.scale(replicas)

        self._log_deployment(service_name, f"scaled to {replicas}")

        return True

    def get_service(self, service_name: str) -> ServiceInstance | None:
        """Получить сервис по имени."""
        return self.services.get(service_name)

    def list_services(
        self,
        status: ServiceStatus | None = None,
        service_type: ServiceType | None = None,
    ) -> list[ServiceInstance]:
        """Список сервисов с фильтрами."""
        result = list(self.services.values())

        if status:
            result = [s for s in result if s.status == status]
        if service_type:
            result = [s for s in result if s.config.service_type == service_type]

        return result

    def get_running_services(self) -> list[ServiceInstance]:
        """Получить запущенные сервисы."""
        return [s for s in self.services.values() if s.status == ServiceStatus.RUNNING]

    def get_failed_services(self) -> list[ServiceInstance]:
        """Получить неудачные сервисы."""
        return [s for s in self.services.values() if s.status == ServiceStatus.FAILED]

    def check_all_health(self) -> dict[str, bool]:
        """Проверить здоровье всех сервисов."""
        return {name: service.check_health() for name, service in self.services.items()}

    def get_statistics(self) -> dict[str, Any]:
        """Получить статистику оркестратора."""
        stats = {
            "total_services": len(self.services),
            "by_status": {},
            "by_type": {},
            "total_replicas": 0,
            "running_count": 0,
        }

        for service in self.services.values():
            # Статусы
            status_key = service.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            # Типы
            type_key = service.config.service_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

            # Счётчики
            stats["total_replicas"] += service.current_replicas
            if service.status == ServiceStatus.RUNNING:
                stats["running_count"] += 1

        return stats

    def deploy_all(self) -> dict[str, bool]:
        """Развернуть все сервисы."""
        results = {}
        for name in self.services:
            results[name] = self.deploy_service(name)
        return results

    def stop_all(self) -> dict[str, bool]:
        """Остановить все сервисы."""
        results = {}
        for name in self.services:
            results[name] = self.stop_service(name)
        return results

    def _log_deployment(self, service_name: str, action: str) -> None:
        """Записать в историю развёртывания."""
        self.deployment_history.append({
            "service": service_name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "cluster": self.cluster_name,
        })

    def get_deployment_history(self, service_name: str | None = None) -> list[dict[str, Any]]:
        """Получить историю развёртываний."""
        if service_name:
            return [h for h in self.deployment_history if h["service"] == service_name]
        return self.deployment_history
