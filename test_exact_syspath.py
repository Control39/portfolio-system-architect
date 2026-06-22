import sys
sys.path = ['C:\\repo\\src', 'C:\\repo\\apps\\ai_config_manager\\src', 'C:\\repo'] + sys.path[3:]

print("sys.path[0:3]:", sys.path[0:3])

try:
    import ai_config_manager
    print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
