"""
proof - Generated Pydantic Models
Source: src\shared\schemas\proof.yaml
"""
from pydantic import BaseModel, Field
from typing import List, Any
from datetime import datetime

class TraceStep(BaseModel):
    input: str = Field(None)
    output: str = Field(None)
    step_type: str = Field(None)
    timestamp: datetime = Field(None)

class ProofMetadata(BaseModel):
    thought_architecture: str = Field(None)
    proof_id: str = Field(None)
    created_at: datetime = Field(None)
    validated: bool = Field(None)

class SystemProof(BaseModel):
    id: str = Field(None)
    metadata: str = Field(None)
    trace_steps: List[Any] = Field(None)
    final_result: dict[str, Any] = Field(None)
    status: str = Field(None)


