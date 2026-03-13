# Indexer

- **Путь**: `07_TOOLS\scripts\scripts\python scripts\indexer.py`
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
        
    def chunk_python_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Разбивает Python файл на логические блоки"""
        chunks = []
        
        try:
            wit
... (файл продолжается)
```
