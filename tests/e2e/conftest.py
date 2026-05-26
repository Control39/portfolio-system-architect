"""
E2E тесты конфигурация

Конфигурация для end-to-end тестов сервисов.
"""

import pytest


def pytest_configure(config):
    """Регистрация маркеров"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test requiring running services"
    )


@pytest.fixture(scope="session")
def service_base_urls():
    """Base URLs для всех сервисов"""
    return {
        "infra_orchestrator": "http://localhost:8200",
        "auth_service": "http://localhost:8100",
        "decision_engine": "http://localhost:8001",
        "career_development": "http://localhost:8301",
        "it_compass": "http://localhost:8501",
        "chat_backend": "http://localhost:8005",
        "ai_config_manager": "http://localhost:8000",
    }


@pytest.fixture
def infra_orchestrator_url(service_base_urls):
    """URL для Infra Orchestrator"""
    return service_base_urls["infra_orchestrator"]


@pytest.fixture
def auth_service_url(service_base_urls):
    """URL для Auth Service"""
    return service_base_urls["auth_service"]


@pytest.fixture
def decision_engine_url(service_base_urls):
    """URL для Decision Engine"""
    return service_base_urls["decision_engine"]


@pytest.fixture
def career_development_url(service_base_urls):
    """URL для Career Development"""
    return service_base_urls["career_development"]
