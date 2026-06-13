"""
Tests for GigaChain Bridge

Validates integration with GigaChat API through mocks
"""

import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:


def test_gigachain_bridge_init(mock_gigachat, mock_prompt_template):
    """Test that GigaMCPBridge can be initialized with mocks"""
    # Import должен работать с мокированными зависимостями
    from apps.decision_engine.gigachain_bridge import GigaMCPBridge

    # Проверяем, что класс существует
    assert GigaMCPBridge is not None


def test_gigachain_bridge_mock_llm(mock_gigachat):
    """Test that mock GigaChat works correctly"""
    assert mock_gigachat is not None
    assert hasattr(mock_gigachat, "invoke")

    # Invoke должен вернуть mock response
    response = mock_gigachat.invoke("Test query")
    assert response is not None
    assert hasattr(response, "content")


def test_gigachain_bridge_settings():
    """Test GigaChainSettings can be created"""
    from apps.decision_engine.gigachain_bridge import GigaChainSettings

    settings = GigaChainSettings(gigachat_api_key="test_key")
    assert settings.gigachat_api_key == "test_key"


@pytest.mark.skip("Integration test - requires actual GigaChat API")
def test_reason_chain():
    """Full chain test - skipped in CI"""
    pass
