# Components Cloud Reason Main

- **Путь**: `docs\obsidian-map\components_cloud_reason_main.md`
- **Тип**: .MD
- **Размер**: 854 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Main

- **Путь**: `components\cloud_reason\main.py`
- **Тип**: .PY
- **Размер**: 788 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import uvicorn
from .config.loader import COMPONENT_CONFIG
from .api.endpoints import app

def run_server():
    # Берём команду запуска из конфигурации
    api_script = next(
        script for script in COMPONENT_CONFIG["automation"]["scripts"]
        if script["name"] == "run_api"
    )

    print(f"Запуск API: {api_script['command']}")

 
... (файл продолжается)
```

