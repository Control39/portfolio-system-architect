# Components Cloud Reason Api Endpoints

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_cloud_reason_api_endpoints.md`
- **Тип**: .MD
- **Размер**: 785 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
# Endpoints

- **Путь**: `components\cloud_reason\api\endpoints.py`
- **Тип**: .PY
- **Размер**: 1,890 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# components/cloud-reason/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..config.loader import COMPONENT_CONFIG
from ..config.utils import get_module_path, find_endpoint_by_path

app = FastAPI(
    title=COMPONENT_CONFIG["component"]["name"],
    version=COMPONENT_CONFIG["compon
... (файл продолжается)
```
