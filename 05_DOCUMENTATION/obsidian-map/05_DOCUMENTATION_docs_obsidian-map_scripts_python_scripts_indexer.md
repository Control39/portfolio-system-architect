# Scripts Python Scripts Indexer

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\scripts_python_scripts_indexer.md`
- **Тип**: .MD
- **Размер**: 808 байт
- **Последнее изменение**: 2026-03-12 10:08:02

## Превью

```
# Indexer

- **Путь**: `scripts\python scripts\indexer.py`
- **Тип**: .PY
- **Размер**: 5,838 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
import ast
from pathlib import Path
from typing import List, Dict, Any
import json
from .embedder import CodeEmbedder

class CodeIndexer:
    def __init__(self, embedder: CodeEmbedder, chunk_size: int = 1000):
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.index = []
        
    def chunk_python_file
... (файл продолжается)
```
