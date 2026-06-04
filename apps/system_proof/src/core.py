"""
Core System Proof - verification and metadata management for GigaChain traces.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    """Step in the reasoning chain."""

    input: str
    output: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProofMetadata(BaseModel):
    """Metadata for system proof."""

    thought_architecture: str = Field(..., description="Architecture pattern used")
    system_thinking_level: int = Field(..., ge=1, le=5, description="1=Basic, 5=Advanced")
    source_link: str | None = Field(None, description="Source repo/link")
    timestamp: datetime = Field(default_factory=datetime.now)
    verified: bool = False


class SystemProof(BaseModel):
    """System proof with chain of thought and verification."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chain_id: str
    steps: list[TraceStep] = Field(default_factory=list)
    metadata: ProofMetadata
    verification_accuracy: float = Field(default=0.0, ge=0, le=1)

    def add_step(
        self, input_text: str, output_text: str, step_metadata: dict[str, Any] | None = None
    ) -> None:
        """Add a trace step to the proof."""
        step = TraceStep(
            input=input_text,
            output=output_text,
            metadata=step_metadata or {},
        )
        self.steps.append(step)

    def verify(self, threshold: float = 0.9) -> bool:
        """Verify the proof meets accuracy threshold."""
        self.metadata.verified = self.verification_accuracy >= threshold
        return self.metadata.verified

    def to_dict(self) -> dict[str, Any]:
        """Convert proof to dictionary."""
        return {
            "id": self.id,
            "chain_id": self.chain_id,
            "steps": [
                {"input": s.input, "output": s.output, "metadata": s.metadata} for s in self.steps
            ],
            "metadata": {
                "thought_architecture": self.metadata.thought_architecture,
                "system_thinking_level": self.metadata.system_thinking_level,
                "source_link": self.metadata.source_link,
                "timestamp": self.metadata.timestamp.isoformat(),
                "verified": self.metadata.verified,
            },
            "verification_accuracy": self.verification_accuracy,
        }


class ProofCollection:
    """Collection of system proofs."""

    def __init__(self):
        """Initialize empty collection."""
        self._proofs: dict[str, SystemProof] = {}

    def add_proof(self, proof: SystemProof) -> str:
        """Add proof to collection."""
        self._proofs[proof.id] = proof
        return proof.id

    def get_proof(self, proof_id: str) -> SystemProof | None:
        """Get proof by ID."""
        return self._proofs.get(proof_id)

    def delete_proof(self, proof_id: str) -> bool:
        """Delete proof by ID."""
        if proof_id in self._proofs:
            del self._proofs[proof_id]
            return True
        return False

    def list_proofs(self) -> list[SystemProof]:
        """List all proofs."""
        return list(self._proofs.values())

    def find_by_chain_id(self, chain_id: str) -> list[SystemProof]:
        """Find proofs by chain ID."""
        return [p for p in self._proofs.values() if p.chain_id == chain_id]

    def find_by_architecture(self, architecture: str) -> list[SystemProof]:
        """Find proofs by thought architecture pattern."""
        return [p for p in self._proofs.values() if p.metadata.thought_architecture == architecture]

    def find_verified(self, threshold: float = 0.9) -> list[SystemProof]:
        """Find verified proofs above threshold."""
        return [p for p in self._proofs.values() if p.verification_accuracy >= threshold]

    def clear(self) -> None:
        """Clear all proofs."""
        self._proofs.clear()

    @property
    def count(self) -> int:
        """Number of proofs in collection."""
        return len(self._proofs)
