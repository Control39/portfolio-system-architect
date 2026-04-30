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

from . import cicd, code_quality, documentation, security, structure

__all__ = [
    "documentation",
    "security",
    "structure",
    "cicd",
    "code_quality",
]


# Export check classes for easy importing
