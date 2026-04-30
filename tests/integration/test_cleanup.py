import os

import pytest


def test_repo_clean():
    # Verify cleanup: no 02_METHODOLOGY dir
    assert not os.path.exists("02_METHODOLOGY")
    print("Cleanup verified: 02_METHODOLOGY absent")


@pytest.mark.skip(reason="Docker manual start needed")
def test_docker_services():
    pass
