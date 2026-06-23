"""Test import from ai_config_manager.config_manager."""

import sys

# Simulate what conftest.py does
sys.path.insert(0, "C:/repo/apps/ai_config_manager/src")
sys.path.insert(0, "C:/repo/src")
sys.path.append("C:/repo")

print("sys.path[0]:", sys.path[0])
print("sys.path[1]:", sys.path[1])

try:
    from ai_config_manager.config_manager import ConfigManager

    print(f"Success! ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
