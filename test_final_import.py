import sys

# Simulate the sys.path from conftest.py
sys.path.insert(0, "C:/repo/src")
sys.path.insert(0, "C:/repo/apps/ai_config_manager/src")
sys.path.insert(0, "C:/repo/apps")
sys.path.insert(0, "C:/repo")

print("sys.path[0:5]:")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

print("\nTesting import:")
try:
    import ai_config_manager

    print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager

    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
