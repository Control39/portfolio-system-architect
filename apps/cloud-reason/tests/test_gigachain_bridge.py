import pytest
from ..cloud_reason.gigachain_bridge import GigaMCPBridge as GigachainBridge

def test_gigachain_bridge_init():
    bridge = GigachainBridge()
    assert bridge is not None

@pytest.mark.skip("Integration")
def test_reason_chain():
    # Full chain test
    pass
