import subprocess

import pytest


@pytest.mark.e2e
def test_arch_compass_module():
    result = subprocess.run(
        [
            "pwsh",
            "-Command",
            "Import-Module ./apps/infra-orchestrator/InfraOrchestrator.psm1; Get-Command InfraOrchestrator",
        ],
        capture_output=True,
    )
    assert result.returncode == 0
