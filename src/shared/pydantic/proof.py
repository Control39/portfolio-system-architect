r"""
proof - Generated Pydantic Models
Source: src\shared\schemas\proof.yaml
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    input: str | None = Field(None)
    output: str | None = Field(None)
    step_type: str | None = Field(None)
    timestamp: datetime | None = Field(None)


class ProofMetadata(BaseModel):
    thought_architecture: str | None = Field(None)
    proof_id: str | None = Field(None)
    created_at: datetime | None = Field(None)
    validated: bool | None = Field(None)


class SystemProof(BaseModel):
    id: str | None = Field(None)
    metadata: str | None = Field(None)
    trace_steps: list[Any] | None = Field(None)
    final_result: dict[str, Any] | None = Field(None)
    status: str | None = Field(None)
