# components/cloud-reason/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..config.loader import COMPONENT_CONFIG
from ..config.utils import get_module_path, find_endpoint_by_path

app = FastAPI(
    title=COMPONENT_CONFIG["component"]["name"],
    version=COMPONENT_CONFIG["component"]["version"],
    description=COMPONENT_CONFIG["component"]["description"],
    docs_url="/docs",
    redoc_url="/redoc"
)

class ReasoningRequest(BaseModel):
    context_sources: list
    query: str
    reasoning_type: str

@app.post(COMPONENT_CONFIG["endpoints"][0]["path"])
async def reason(request: ReasoningRequest):
    endpoint_info = find_endpoint_by_path("/api/v1/reason")
    module_path = get_module_path("reasoning_engine")

    return {
        "status": "processing",
        "module_used": module_path,
        "endpoint": endpoint_info["path"],
        "description": endpoint_info["description"]
    }

@app.get("/api/v1/status")
async def get_status():
    return {
        "component": COMPONENT_CONFIG["component"]["name"],
        "version": COMPONENT_CONFIG["component"]["version"],
        "status": "healthy",
        "coverage_target": COMPONENT_CONFIG["tests"]["coverage_target"],
        "total_modules": len(COMPONENT_CONFIG["modules"])
    }

# Динамическое создание всех эндпоинтов из конфигурации
for endpoint_data in COMPONENT_CONFIG["endpoints"]:
    path = endpoint_data["path"]
    method = endpoint_data["method"].lower()

    if method == "get" and path != "/api/v1/status":
        @app.get(path)
        async def generic_get():
            return {"endpoint": path, "status": "active"}

    elif method == "post" and path != "/api/v1/reason":
        @app.post(path)
        async def generic_post():
            return {"endpoint": path, "status": "processed"}
