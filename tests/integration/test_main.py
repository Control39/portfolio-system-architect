import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK

from src.main import (
    COMPONENT_CONFIG,
    create_stub_app,
    extract_port_from_config,
    main,
    main_dev,
    main_prod,
    run_server,
)


@pytest.fixture(scope="session")
def client():
    """Fixture providing a test client to interact with the application."""
    app = create_stub_app()
    with TestClient(app) as c:
        yield c


def test_extract_port_from_config_no_script():
    """
    Test that extract_port_from_config returns default port when no valid config found.
    """
    original_config = COMPONENT_CONFIG.copy()
    try:
        import src.main

        src.main.COMPONENT_CONFIG = {"automation": {"scripts": []}}
        assert extract_port_from_config() == 8000
    finally:
        src.main.COMPONENT_CONFIG = original_config


def test_extract_port_from_config_valid_script():
    """
    Test that extract_port_from_config correctly extracts port from valid configuration.
    """
    original_config = COMPONENT_CONFIG.copy()
    try:
        import src.main

        src.main.COMPONENT_CONFIG = {"automation": {"scripts": [{"name": "run_api", "command": ["--port", "9000"]}]}}
        assert extract_port_from_config() == 9000
    finally:
        src.main.COMPONENT_CONFIG = original_config


@patch("src.main.uvicorn.run")
def test_run_server_default_port(mock_run, caplog):
    """
    Test that run_server configures correct parameters for default port.
    """
    run_server("localhost", 8000, False, None)
    mock_run.assert_called_once()
    # Check that uvicorn was called with correct config
    call_args = mock_run.call_args[1]
    assert call_args["host"] == "localhost"
    assert call_args["port"] == 8000


@patch("src.main.uvicorn.run")
def test_run_server_custom_port(mock_run):
    """
    Test that run_server uses custom port when provided.
    """
    run_server("localhost", 8080, False, None)
    mock_run.assert_called_once()
    call_args = mock_run.call_args[1]
    assert call_args["port"] == 8080


@patch("src.main.uvicorn.run")
def test_run_server_reload_mode(mock_run):
    """
    Test that run_server configures reload mode correctly.
    """
    run_server("localhost", 8000, True, None)
    mock_run.assert_called_once()
    call_args = mock_run.call_args[1]
    assert call_args["reload"] is True


@patch("src.main.uvicorn.run")
def test_main_dev(mock_run):
    """
    Test that main_dev calls run_server in development mode.
    """
    main_dev("localhost", 8000)
    mock_run.assert_called_once()


@patch("src.main.uvicorn.run")
def test_main_prod(mock_run):
    """
    Test that main_prod calls run_server in production mode.
    """
    main_prod("localhost", 8000, 4)
    mock_run.assert_called_once()


@patch("src.main.uvicorn.run")
def test_create_stub_app(mock_run, client):
    """
    Test that create_stub_app creates a FastAPI instance with correct metadata.
    """
    app = create_stub_app()
    response = client.get("/")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"message": "Заглушечное приложение", "status": "running", "version": "1.0.0"}


@patch("src.main.uvicorn.run")
def test_main_call(mock_run):
    """
    Test that main calls run_server with appropriate arguments based on input parameters.
    """
    main("localhost", 8000, True, 4)
    mock_run.assert_called_once()


@patch("src.main.uvicorn.run")
def test_main_dev_mode(mock_run):
    """
    Test that main_dev calls run_server in development mode.
    """
    main_dev("localhost", 8000)
    mock_run.assert_called_once()


@patch("src.main.uvicorn.run")
def test_main_prod_mode(mock_run):
    """
    Test that main_prod calls run_server in production mode.
    """
    main_prod("localhost", 8000, 4)
    mock_run.assert_called_once()
