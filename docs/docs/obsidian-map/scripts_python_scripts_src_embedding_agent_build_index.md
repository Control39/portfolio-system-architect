# Build Index

- **Путь**: `scripts\python scripts\src\embedding_agent\build_index.py`
- **Тип**: .PY
- **Размер**: 1,442 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
#!/usr/bin/env python
import sys
from pathlib import Path

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder
from src.embedding_agent.indexer import CodeIndexer

def main():
    print("🚀 Начинаем индексацию кодовой базы...")
    
    # Инициализируем компоненты
    embedder = CodeEmbedder(model_name="nomic-embed-text")
    indexer = CodeIndexer(embedder)
    
    # Индексируем текущий репозиторий
    repo_path = Path(
... (файл продолжается)
```

