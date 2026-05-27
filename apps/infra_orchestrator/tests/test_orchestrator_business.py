"""Business logic tests for infra_orchestrator."""
import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Импортируем из локального модуля, а не глобального
from apps.infra_orchestrator.src.core import ServiceConfig, Orchestrator

def test_service_config_creation():
    """Test ServiceConfig model."""
    config = ServiceConfig(
        name="test-service",
        version="1.0.0",
        enabled=True,
        settings={"port": 8080}
    )
    assert config.name == "test-service"
    assert config.version == "1.0.0"
    assert config.enabled is True
    assert config.settings["port"] == 8080

def test_orchestrator_registration():
    """Test orchestrator service registration."""
    orch = Orchestrator()
    config = ServiceConfig(name="api", version="2.0")
    
    orch.register_service(config)
    retrieved = orch.get_service("api")
    
    assert retrieved is not None
    assert retrieved.name == "api"
    assert retrieved.version == "2.0"

def test_orchestrator_get_nonexistent():
    """Test getting non-existent service."""
    orch = Orchestrator()
    result = orch.get_service("nonexistent")
    assert result is None
