# Pydantic схемы для Cloud-Reason API
from pydantic import BaseModel
from typing import Optional, List

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "cloud-reason"

class ReasoningRequest(BaseModel):
    context_sources: Optional[List[str]] = None
    query: str
    reasoning_type: Optional[str] = "analysis"

class ReasoningResponse(BaseModel):
    result: str
    trace: Optional[dict] = None
    verified: bool = False

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
