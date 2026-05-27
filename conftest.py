"""Global pytest configuration - loads .env.test for testing."""

import os
import pytest
from pathlib import Path

def pytest_configure(config):
    """Load .env.test before any tests run."""
    repo_root = Path(__file__).parent
    env_test_path = repo_root / ".env.test"
    
    if env_test_path.exists():
        with open(env_test_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = value
        print(f"✅ Loaded test environment from {env_test_path}")

MOLECULES_REQUIRING_ENV = {
    "auth_service": {"JWT_SECRET"},
    "chat_backend": {"JWT_SECRET", "DATABASE_URL"},
    "decision_engine": {"GIGACHAT_API_KEY"},
}

ALL_REQUIRED_ENV_VARS = {"JWT_SECRET", "DATABASE_URL", "GIGACHAT_API_KEY"}

def pytest_collection_modifyitems(config, items):
    missing = set()
    for var in ALL_REQUIRED_ENV_VARS:
        if var not in os.environ:
            missing.add(var)
    
    if not missing:
        return
    
    for item in items:
        test_path = str(item.fspath)
        for molecule, required_vars in MOLECULES_REQUIRING_ENV.items():
            if f"apps{os.sep}{molecule}" in test_path:
                missing_for_molecule = required_vars & missing
                if missing_for_molecule:
                    item.add_marker(pytest.mark.skip(reason=f"Missing env: {missing_for_molecule}"))
                break
