"""
Shared Pydantic models - generated from src/shared/schemas/career.yaml
"""

import sys
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.shared.pydantic.career import CompetencyMarker, Skill, UserProfile  # noqa: E402


# Local extensions/aliases if needed
__all__ = ["CompetencyMarker", "Skill", "UserProfile"]
