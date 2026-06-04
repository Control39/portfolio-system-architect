"""Local test configuration for auth_service molecule.

This follows the Compositional Architecture pattern:
- Molecule sees its own src/
- Molecule sees repo root (for cross-molecule imports like apps.ai_config_manager...)
- No global PYTHONPATH pollution
"""

import sys
from pathlib import Path


def _configure_imports() -> None:
    # Get repo root (4 levels up from tests/conftest.py)
    tests_dir = Path(__file__).resolve().parent
    molecule_root = tests_dir.parent
    repo_root = molecule_root.parent.parent

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    molecule_src = molecule_root / "src"
    if molecule_src.exists() and str(molecule_src) not in sys.path:
        sys.path.insert(0, str(molecule_src))


_configure_imports()
