# Search Demo

- **Путь**: `07_TOOLS\scripts\scripts\python scripts\src\embedding_agent\search_demo.py`
- **Тип**: .PY
- **Размер**: 4,106 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
#!/usr/bin/env python
import sys
from pathlib import Path
import json
import numpy as np

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder

def load_full_index(index_file: str):
    """Загружает полный индекс с эмбеддингами"""
    with open(index_file, 'r') as f:
        index_meta = json.load(f)
    
    # Здесь нужно загружать полные эмбеддинги из отдельного хранилища
    # Для демо будем переиндексировать при поис
... (файл продолжается)
```
