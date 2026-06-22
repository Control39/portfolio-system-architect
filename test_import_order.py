"""Test import order issue."""
import sys

# Order 1: src first (current)
print("Order 1: src first")
sys.path1 = ["C:/repo/src", "C:/repo/apps/ai_config_manager/src", "C:/repo", "C:/repo/apps"] + sys.path[3:]
try:
    import ai_config_manager
    print(f"  ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"  config_manager import: OK")
except Exception as e:
    print(f"  Failed: {e}")

# Order 2: apps first
print("\nOrder 2: apps first")
sys.path2 = ["C:/repo/apps", "C:/repo", "C:/repo/src", "C:/repo/apps/ai_config_manager/src"] + sys.path[4:]
try:
    import ai_config_manager
    print(f"  ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"  config_manager import: OK")
except Exception as e:
    print(f"  Failed: {e}")

# Order 3: apps/ai_config_manager/src first
print("\nOrder 3: ai_config_manager/src first")
sys.path3 = ["C:/repo/apps/ai_config_manager/src", "C:/repo/src", "C:/repo/apps", "C:/repo"] + sys.path[4:]
try:
    import ai_config_manager
    print(f"  ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"  config_manager import: OK")
except Exception as e:
    print(f"  Failed: {e}")
