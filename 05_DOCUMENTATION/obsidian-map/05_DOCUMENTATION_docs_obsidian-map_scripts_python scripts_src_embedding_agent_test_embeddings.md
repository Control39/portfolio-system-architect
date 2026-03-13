# Scripts Python Scripts Src Embedding Agent Test Embeddings

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\scripts_python scripts_src_embedding_agent_test_embeddings.md`
- **Тип**: .MD
- **Размер**: 904 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
# Test Embeddings

- **Путь**: `scripts\python scripts\src\embedding_agent\test_embeddings.py`
- **Тип**: .PY
- **Размер**: 1,035 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_agent.embedder import CodeEmbedder

def test_embedder():
    """Тестирование работы эмбеддера"""
    embedder = CodeEmbedder()
    
    test_cases = [
        ("def hello(): print('world')", "про
... (файл продолжается)
```
