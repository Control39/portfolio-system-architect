# Main

- **Путь**: `02_MODULES\cloud-reason\cloud_reason\main.py`
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

    # Извлекаем порт из команды (если указан)
    port = 8000  # дефолтный порт
    if "--port" in api_script["command"]:
        port_str = api_script["com
... (файл продолжается)
```
