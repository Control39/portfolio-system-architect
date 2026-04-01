# Components Cloud Reason Configs Loader

- **Путь**: `docs\obsidian-map\components_cloud_reason_configs_loader.md`
- **Тип**: .MD
- **Размер**: 850 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Loader

- **Путь**: `components\cloud_reason\configs\loader.py`
- **Тип**: .PY
- **Размер**: 857 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# components/cloud-reason/config/loader.py
import yaml
from pathlib import Path

def load_component_config():
    """Загружает конфигурацию компонента из component-config.yaml в корне проекта."""
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "component-config.yaml"

    if not config_path.e
... (файл продолжается)
```

