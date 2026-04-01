# Scripts Python Scripts Src Embedding Agent Search Demo

- **Путь**: `docs\obsidian-map\scripts_python scripts_src_embedding_agent_search_demo.md`
- **Тип**: .MD
- **Размер**: 946 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
# Search Demo

- **Путь**: `scripts\python scripts\src\embedding_agent\search_demo.py`
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
   
... (файл продолжается)
```

