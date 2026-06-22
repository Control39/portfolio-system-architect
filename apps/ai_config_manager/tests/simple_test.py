import sys
print("sys.path[0:5]:")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

print("\nTrying import:")
try:
    import ai_config_manager
    print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
