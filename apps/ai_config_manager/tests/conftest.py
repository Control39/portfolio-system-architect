"""Local test configuration for ai_config_manager molecule.

This keeps imports scoped to the ai_config_manager molecule (apps/level)
while still allowing the package under apps/ai_config_manager/src to be imported.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _add_paths() -> None:
    tests_dir = Path(__file__).resolve().parent
    app_root = tests_dir.parent  # apps/ai_config_manager
    app_src = app_root / "src"

    # Ensure the molecule package is importable: `import ai_config_manager...`
    sys.path.insert(0, str(app_src))


_add_paths()

