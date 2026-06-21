"""Pytest configuration for cognitive_agent tests."""

import sys
from pathlib import Path

# Add repo root to Python path so that 'cognitive_agent' package can be imported
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
