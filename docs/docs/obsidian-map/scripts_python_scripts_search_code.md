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
    return response.json()["embedding"]

def search_code(query, index_file="code_index.json"):
    # Загружаем индекс
    with open(index_file, "r") as f:
        index_data = json.load(f)
    

... (файл продолжается)
```

