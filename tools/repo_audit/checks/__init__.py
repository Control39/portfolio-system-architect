"""Check modules for repository audit.

Each module defines checks for a specific category:
- documentation
- security
- structure
- cicd
- code_quality
- testing
- licensing
- dependencies
- monitoring
- automation
"""

from . import (
    automation,
    cicd,
    code_quality,
    dependencies,
    documentation,
    licensing,
    monitoring,
    security,
    structure,
    testing,
)

__all__ = [
    "documentation",
    "security",
    "structure",
    "cicd",
    "code_quality",
    "testing",
    "licensing",
    "dependencies",
    "monitoring",
    "automation",
]


# Export check classes for easy importing
