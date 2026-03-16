# Components Cloud Reason Core Module Loader

- **Путь**: `docs\obsidian-map\components_cloud_reason_core_module-loader.md`
- **Тип**: .MD
- **Размер**: 825 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Module Loader

- **Путь**: `components\cloud_reason\core\module-loader.py`
- **Тип**: .PY
- **Размер**: 908 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import importlib.util
from pathlib import Path
from ..config.loader import COMPONENT_CONFIG

def load_module_by_name(module_name):
    """Загружает Python‑модуль по имени из конфигурации."""
    for module_info in COMPONENT_CONFIG["modules"]:
        if module_info["name"] == module_name:
            module_path = Path(_
... (файл продолжается)
```
