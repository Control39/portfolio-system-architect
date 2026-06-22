import sys

# Store original sys.path
original_path = sys.path.copy()

# Set new sys.path
sys.path = ['C:\\repo\\src', 'C:\\repo\\apps\\ai_config_manager\\src', 'C:\\repo']

print("sys.path[0:5]:", sys.path[0:5])

try:
    import ai_config_manager
    print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()

# Restore
sys.path = original_path
