import sys
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402

from apps.decision_engine.gigachain_bridge import GigaMCPBridge as GigachainBridge  # noqa: E402


def test_gigachain_bridge_init():
    bridge = GigachainBridge()
    assert bridge is not None


@pytest.mark.skip("Integration")
def test_reason_chain():
    # Full chain test
    pass
