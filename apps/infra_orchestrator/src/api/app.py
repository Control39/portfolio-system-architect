"""FastAPI app for infra_orchestrator."""

from fastapi import FastAPI, HTTPException
from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel
from uuid import uuid4

services_db: Dict[str, Dict] = {}
instances_db: Dict[str, Dict] = {}
deployment_history: List[Dict] = []


class Service(BaseModel):
    name: str
    version: str
    port: int
    enabled: bool = True


app = FastAPI(title="Infra Orchestrator", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


@app.post("/services")
async def create_service(service: Service):
    service_id = str(uuid4())[:8]
    service_dict = service.dict()
    service_dict["id"] = service_id
    service_dict["created_at"] = datetime.now().isoformat()
    services_db[service_id] = service_dict
    return service_dict


@app.get("/services")
async def list_services():
    return list(services_db.values())


@app.get("/services/{service_id}")
async def get_service(service_id: str):
    if service_id not in services_db:
        raise HTTPException(status_code=404, detail="Service not found")
    return services_db[service_id]


__all__ = ["app", "services_db", "instances_db", "deployment_history"]
