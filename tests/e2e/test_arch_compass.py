import pytest
import subprocess

@pytest.mark.e2e
def test_arch_compass_module():
    result = subprocess.run(["pwsh", "-Command", "Import-Module ./apps/arch-compass-framework/ArchCompass.psm1; Get-Command ArchCompass"], capture_output=True)
    assert result.returncode == 0
