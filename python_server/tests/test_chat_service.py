"""
Test suite for ChatService.
Currently disabled due to missing ConnectionTaskManager.
Will be restored after implementation.
"""

import pytest


@pytest.mark.skip(reason="ConnectionTaskManager not implemented yet")
def test_placeholder():
    assert True
