"""Data classes for analysis results.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MicroserviceInfo:
    """Information about a microservice."""

    name: str
    path: str
    is_production_ready: bool = False
    has_tests: bool = False
    has_docker: bool = False
    has_kubernetes: bool = False
    language: str = "unknown"
    dependencies: list[str] = field(default_factory=list)


@dataclass
class SkillMarker:
    """Skill marker from IT-Compass."""

    id: str
    category: str
    level: int
    description: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class GitStats:
    """Git repository statistics."""

    total_commits: int = 0
    recent_activity_days: int = 0
    contributors: list[str] = field(default_factory=list)
    branches: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Overall analysis result."""

    timestamp: str
    microservices: dict[str, Any] = field(default_factory=dict)
    skill_markers: dict[str, Any] = field(default_factory=dict)
    architecture_docs: list[str] = field(default_factory=list)
    git_stats: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, list[str]] = field(default_factory=dict)

    def dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "microservices": self.microservices,
            "skill_markers": self.skill_markers,
            "architecture_docs": self.architecture_docs,
            "git_stats": self.git_stats,
            "dependencies": self.dependencies,
        }

