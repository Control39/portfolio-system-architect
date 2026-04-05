# Scripts Generate Docs

- **Путь**: `docs\obsidian-map\scripts_generate_docs.md`
- **Тип**: .MD
- **Размер**: 827 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
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

    for endpoint in COMPONENT_CONFIG["endp
... (файл продолжается)
```

