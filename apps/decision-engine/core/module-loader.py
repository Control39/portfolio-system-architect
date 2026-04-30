import importlib.util
from pathlib import Path

from ..config.loader import COMPONENT_CONFIG


def load_module_by_name(module_name):
    """Загружает Python‑модуль по имени из конфигурации."""
    for module_info in COMPONENT_CONFIG["modules"]:
        if module_info["name"] == module_name:
            module_path = Path(__file__).parent.parent / module_info["path"]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"Модуль {module_name} не найден в конфигурации")


# Пример использования
reasoning_engine = loadmodule_by_name("reasoning_engine")
print(f"✅ Модуль {reasoning_engine.__name__} загружен")
