# Scripts Python Scripts Search Code

- **Путь**: `docs\obsidian-map\scripts_python scripts_search_code.md`
- **Тип**: .MD
- **Размер**: 804 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
# Search Code

- **Путь**: `scripts\python scripts\search_code.py`
- **Тип**: .PY
- **Размер**: 1,527 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
import json
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    return response.json
... (файл продолжается)
```
