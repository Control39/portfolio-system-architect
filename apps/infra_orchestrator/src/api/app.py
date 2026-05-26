"""
Infrastructure Orchestrator API — управление развёртыванием сервисов
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.infra_orchestrator.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    io_config = config_manager.get_config()
    print("✅ Infra Orchestrator: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Infra Orchestrator: AI Config Manager недоступен ({e}), используется локальный конфиг")
    io_config = {}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Инициализация приложения
app = FastAPI(
    title="Infrastructure Orchestrator API",
    version="1.0.0",
    description="API для управления развёртыванием и масштабированием микросервисов"
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "infra-orchestrator",
        "version": "1.0.0",
        "ai_config_available": AI_CONFIG_AVAILABLE
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe"""
    return {"status": "ready"}

@app.get("/live")
async def liveness_check():
    """Liveness probe"""
    return {"status": "alive"}

# Enums
class ServiceStatus(str, Enum):
    pending = "pending"
    deploying = "deploying"
    running = "running"
    stopped = "stopped"
    failed = "failed"
    scaling = "scaling"

class ServiceType(str, Enum):
    api = "api"
    worker = "worker"
    scheduler = "scheduler"
    database = "database"
    cache = "cache"
    gateway = "gateway"

# Модели данных
class ServiceConfig(BaseModel):
    """Конфигурация сервиса"""
    service_id: str
    name: str
    service_type: ServiceType
    image: str
    replicas: int = 1
    ports: Dict[str, int] = {}
    environment: Dict[str, str] = {}
    depends_on: List[str] = []
    health_check_path: Optional[str] = "/health"

class ServiceInstance(BaseModel):
    """Экземпляр сервиса"""
    instance_id: str
    service_id: str
    status: ServiceStatus = ServiceStatus.pending
    config: ServiceConfig
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    cluster: str = "default"
    health_status: str = "unknown"

# Временное хранилище
services_db: dict[str, ServiceConfig] = {}
instances_db: dict[str, ServiceInstance] = {}
deployment_history: List[Dict[str, Any]] = []

# CRUD для конфигураций сервисов
@app.get("/services", response_model=List[ServiceConfig])
async def list_services():
    """Получить список всех конфигураций сервисов"""
    return list(services_db.values())

@app.post("/services", response_model=ServiceConfig)
async def register_service(config: ServiceConfig):
    """Зарегистрировать новый сервис"""
    if config.service_id in services_db:
        raise HTTPException(status_code=400, detail="Service already registered")
    
    services_db[config.service_id] = config
    return config

@app.get("/services/{service_id}", response_model=ServiceConfig)
async def get_service(service_id: str):
    """Получить конфигурацию сервиса"""
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    return services_db[service_id]

@app.put("/services/{service_id}", response_model=ServiceConfig)
async def update_service(service_id: str, config: ServiceConfig):
    """Обновить конфигурацию сервиса"""
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    
    services_db[service_id] = config
    return config

@app.delete("/services/{service_id}")
async def delete_service(service_id: str):
    """Удалить конфигурацию сервиса"""
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    
    del services_db[service_id]
    return {"message": "Service configuration deleted"}

# CRUD для экземпляров сервисов
@app.get("/instances", response_model=List[ServiceInstance])
async def list_instances(
    status: Optional[ServiceStatus] = None,
    cluster: Optional[str] = None
):
    """Получить список экземпляров"""
    instances = list(instances_db.values())
    
    if status:
        instances = [i for i in instances if i.status == status]
    if cluster:
        instances = [i for i in instances if i.cluster == cluster]
    
    return instances

@app.post("/instances/{service_id}/deploy")
async def deploy_service(service_id: str, cluster: str = "default"):
    """Развернуть сервис"""
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    
    config = services_db[service_id]
    instance_id = f"{service_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    instance = ServiceInstance(
        instance_id=instance_id,
        service_id=service_id,
        status=ServiceStatus.deploying,
        config=config,
        cluster=cluster
    )
    
    instances_db[instance_id] = instance
    
    # Имитация развёртывания
    instance.status = ServiceStatus.running
    instance.started_at = datetime.now()
    instance.updated_at = datetime.now()
    instance.health_status = "healthy"
    
    # Запись в историю
    deployment_history.append({
        "instance_id": instance_id,
        "service_id": service_id,
        "action": "deploy",
        "timestamp": datetime.now().isoformat(),
        "cluster": cluster,
        "status": "success"
    })
    
    return instance

@app.post("/instances/{instance_id}/start")
async def start_instance(instance_id: str):
    """Запустить экземпляр"""
    if instance_id not in instances_db:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance = instances_db[instance_id]
    if instance.status == ServiceStatus.stopped:
        instance.status = ServiceStatus.running
        instance.started_at = datetime.now()
        instance.health_status = "healthy"
    
    instance.updated_at = datetime.now()
    return instance

@app.post("/instances/{instance_id}/stop")
async def stop_instance(instance_id: str):
    """Остановить экземпляр"""
    if instance_id not in instances_db:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance = instances_db[instance_id]
    if instance.status == ServiceStatus.running:
        instance.status = ServiceStatus.stopped
        instance.stopped_at = datetime.now()
    
    instance.updated_at = datetime.now()
    return instance

@app.delete("/instances/{instance_id}")
async def delete_instance(instance_id: str):
    """Удалить экземпляр"""
    if instance_id not in instances_db:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    del instances_db[instance_id]
    return {"message": "Instance deleted"}

# Масштабирование
@app.post("/instances/{instance_id}/scale")
async def scale_instance(instance_id: str, replicas: int):
    """Масштабировать экземпляр"""
    if instance_id not in instances_db:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    if replicas < 1:
        raise HTTPException(status_code=400, detail="Replicas must be >= 1")
    
    instance = instances_db[instance_id]
    instance.status = ServiceStatus.scaling
    instance.config.replicas = replicas
    instance.updated_at = datetime.now()
    
    # Имитация масштабирования
    instance.status = ServiceStatus.running
    instance.updated_at = datetime.now()
    
    # Запись в историю
    deployment_history.append({
        "instance_id": instance_id,
        "service_id": instance.service_id,
        "action": "scale",
        "replicas": replicas,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    })
    
    return instance

# Health checks
@app.get("/instances/{instance_id}/health")
async def check_instance_health(instance_id: str):
    """Проверить здоровье экземпляра"""
    if instance_id not in instances_db:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance = instances_db[instance_id]
    return {
        "instance_id": instance_id,
        "health_status": instance.health_status,
        "status": instance.status.value
    }

@app.get("/health/all")
async def check_all_health():
    """Проверить здоровье всех экземпляров"""
    results = {}
    for instance_id, instance in instances_db.items():
        results[instance_id] = {
            "health_status": instance.health_status,
            "status": instance.status.value
        }
    return results

# Статистика
@app.get("/statistics")
async def get_statistics():
    """Получить статистику"""
    status_counts = {}
    type_counts = {}
    cluster_counts = {}
    
    for instance in instances_db.values():
        # Status
        status = instance.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Type
        service_type = instance.config.service_type.value
        type_counts[service_type] = type_counts.get(service_type, 0) + 1
        
        # Cluster
        cluster = instance.cluster
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
    
    return {
        "total_instances": len(instances_db),
        "total_services": len(services_db),
        "by_status": status_counts,
        "by_type": type_counts,
        "by_cluster": cluster_counts
    }

# История развёртываний
@app.get("/history")
async def get_history(limit: int = 100):
    """Получить историю развёртываний"""
    return deployment_history[-limit:]

# Фильтрация экземпляров
@app.get("/instances/by-type")
async def get_by_type(service_type: ServiceType):
    """Получить экземпляры по типу"""
    results = []
    for instance in instances_db.values():
        if instance.config.service_type == service_type:
            results.append(instance)
    return results
