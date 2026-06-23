import sys

sys.path.insert(0, "C:/repo/src")
sys.path.insert(0, "C:/repo/apps/ai_config_manager/src")

print("sys.path[0:3]:", sys.path[0:3])

import ai_config_manager

print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
print(f"ai_config_manager.__path__: {ai_config_manager.__path__}")

# Check if config_manager submodule exists
import os

print("\nContents of ai_config_manager package:")
pkg_path = os.path.dirname(ai_config_manager.__file__)
for f in os.listdir(pkg_path):
    print(f"  {f}")

# Try to import config_manager
try:
    import ai_config_manager.config_manager
    print(f"\nai_config_manager.config_manager.__file__: {ai_config_manager.config_manager.__file__}")
except Exception as e:
    print(f"\nFailed to import config_manager: {e}")
