#!/usr/bin/env python3
"""
Rename integration test files to avoid pytest conflicts
"""

from pathlib import Path

services = [
    "cognitive_agent",
    "decision_engine",
    "it_compass",
    "mcp_server",
    "infra_orchestrator",
]

root = Path(".").resolve() / "apps"

for service in services:
    test_file = root / service / "tests" / "test_integration.py"
    new_file = root / service / "tests" / f"test_integration_{service.replace('-', '_')}.py"

    if test_file.exists():
        test_file.rename(new_file)
        print(f"✅ Renamed: {service}")

print("\n✅ All test files renamed to avoid conflicts")
