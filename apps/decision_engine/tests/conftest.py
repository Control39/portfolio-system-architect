"""
Test configuration and fixtures for decision_engine
Includes mocks for GigaChat API to avoid external dependencies
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ============================================================================
# MOCK CLASSES FOR EXTERNAL DEPENDENCIES
# ============================================================================


class MockGigaChat:
    """Mock for langchain_community.llms.GigaChat"""

    def __init__(self, *args, **kwargs):
        self.api_key = kwargs.get("api_key", "")
        self.model = kwargs.get("model", "gigachat:latest")

    def invoke(self, text):
        """Mock invoke method"""
        return MagicMock(content=f"Mock response for: {text}")

    def __call__(self, *args, **kwargs):
        """Allow calling as function"""
        return self.invoke(*args, **kwargs)


class MockPromptTemplate:
    """Mock for langchain_core.prompts.PromptTemplate"""

    def __init__(self, *args, **kwargs):
        self.template = kwargs.get("template", "")
        self.input_variables = kwargs.get("input_variables", [])

    def __or__(self, other):
        """Mock the | operator for chaining"""
        return MagicMock(invoke=lambda x: MagicMock(content="Mock chain response"))


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def mock_langchain_modules():
    """Mock langchain modules to avoid import errors in CI"""
    # Mock langchain imports
    mock_langchain = MagicMock()
    mock_langchain.prompts.PromptTemplate = MockPromptTemplate
    sys.modules["langchain"] = mock_langchain
    sys.modules["langchain.prompts"] = MagicMock(PromptTemplate=MockPromptTemplate)

    # Mock langchain_core imports
    mock_langchain_core = MagicMock()
    mock_langchain_core.prompts.PromptTemplate = MockPromptTemplate
    sys.modules["langchain_core"] = mock_langchain_core
    sys.modules["langchain_core.prompts"] = MagicMock(PromptTemplate=MockPromptTemplate)

    # Mock langchain_community imports
    mock_langchain_community = MagicMock()
    mock_langchain_community.llms.GigaChat = MockGigaChat
    sys.modules["langchain_community"] = mock_langchain_community
    sys.modules["langchain_community.llms"] = MagicMock(GigaChat=MockGigaChat)

    # Mock langchain_gigachat
    mock_langchain_gigachat = MagicMock()
    mock_langchain_gigachat.GigaChat = MockGigaChat
    sys.modules["langchain_gigachat"] = mock_langchain_gigachat

    yield

    # Cleanup
    for key in list(sys.modules.keys()):
        if key.startswith("langchain"):
            del sys.modules[key]


@pytest.fixture
def mock_gigachat():
    """Fixture providing a mock GigaChat instance"""
    return MockGigaChat(api_key="test_key", model="gigachat:latest")


@pytest.fixture
def mock_prompt_template():
    """Fixture providing a mock PromptTemplate instance"""
    return MockPromptTemplate(
        input_variables=["context", "query"], template="Context: {context}\nQuery: {query}"
    )


@pytest.fixture
def config():
    """Service configuration fixture"""
    return {
        "service_name": "decision-engine",
        "environment": "test",
        "debug": True,
        "timeout": 5.0,
    }


@pytest.fixture
def mock_logger():
    """Mock logger fixture"""
    return MagicMock()
