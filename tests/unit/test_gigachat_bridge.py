"""Тесты для gigachat_bridge.py"""

import pytest
from unittest.mock import MagicMock, patch

from src.ai.gigachat_bridge import GigaMCPBridge, GigaChainSettings, measure_latency


def test_giga_mcp_bridge_init():
    """Test initialization of GigaMCPBridge without errors."""
    with patch("src.ai.gigachat_bridge.GigaChat") as mock_gigachat:
        mock_gigachat.return_value = MagicMock()
        bridge = GigaMCPBridge()
        assert isinstance(bridge, GigaMCPBridge)


def test_giga_request_happy_path():
    """Test successful execution of giga_request function."""
    with (
        patch("src.ai.gigachat_bridge.GigaChat") as mock_gigachat,
        patch("src.ai.gigachat_bridge.PromptTemplate") as mock_prompt,
    ):
        mock_gigachat.return_value = MagicMock()
        mock_prompt.return_value = MagicMock()

        bridge = GigaMCPBridge()
        bridge.llm = mock_gigachat.return_value
        bridge.prompt = mock_prompt.return_value
        bridge.chain = MagicMock()
        bridge.chain.invoke.return_value.content = "Test Response"

        result = bridge.giga_request(query="Test Query")

        assert "response" in result
        assert "trace" in result
        assert "verified" in result
        assert result["response"] == "Test Response"


def test_verify_inference_valid_response():
    """Test verification of inference when output length exceeds threshold."""
    bridge = GigaMCPBridge()
    mock_trace = {
        "input": "Test Input",
        "context": "Test Context",
        "output": "Long enough response with more than 50 characters!!!",
    }
    result = bridge.verify_inference(mock_trace)
    assert result is True


def test_verify_inference_invalid_response():
    """Test verification of inference when output length does not meet threshold."""
    bridge = GigaMCPBridge()
    mock_trace = {"input": "Test Input", "context": "Test Context", "output": "Too short"}
    result = bridge.verify_inference(mock_trace)
    assert result is False


def test_self_improve_average_length():
    """Test self-improvement logic based on average response length."""
    bridge = GigaMCPBridge()
    mock_traces = [{"output": "Short"}, {"output": "Medium Length Output"}, {"output": "Very Long Response"}]
    result = bridge.self_improve(mock_traces)
    assert "Avg response len" in result


def test_measure_latency():
    """Test latency measurement functionality."""

    def dummy_func():
        return "result"

    result, elapsed_time = measure_latency(dummy_func)
    assert result == "result"
    assert elapsed_time >= 0


def test_giga_request_missing_api_key():
    """Test error handling when GigaChat API key is missing."""
    # This test verifies that GigaChat initialization raises RuntimeError when GigaChat is None
    with patch("src.ai.gigachat_bridge.GigaChat", None):
        with pytest.raises(RuntimeError):
            GigaMCPBridge()


def test_giga_chain_settings_default_values():
    """Test that GigaChainSettings has correct default values."""
    settings = GigaChainSettings()
    assert settings.chroma_path == "./chroma_db"
    assert settings.mcp_url == "http://localhost:8000/mcp"


def test_measure_latency_with_args():
    """Test latency measurement with function arguments."""

    def add(a, b):
        return a + b

    result, elapsed_time = measure_latency(add, 2, 3)
    assert result == 5
    assert elapsed_time >= 0
