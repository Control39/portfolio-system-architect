# Generate Docs

- **Путь**: `scripts\generate_docs.py`
- **Тип**: .PY
- **Размер**: 1,039 байт
- **Последнее изменение**: 2026-03-05 05:17:36

## Превью

```
from ..config.loader import COMPONENT_CONFIG

def generate_api_docs():
    """Генерирует документацию API на основе конфигурации."""
    docs = f"# {COMPONENT_CONFIG['component']['name']}\n\n"
    docs += f"**Версия:** {COMPONENT_CONFIG['component']['version']}\n\n"
    docs += "## Эндпоинты\n\n"

    for endpoint in COMPONENT_CONFIG["endpoints"]:
        docs += f"### {endpoint['method']} {endpoint['path']}\n"
        docs += f"{endpoint['description']}\n\n"

        if "parameters" in endpoint
... (файл продолжается)
```
