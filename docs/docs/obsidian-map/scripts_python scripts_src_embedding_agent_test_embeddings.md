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
        ("def hello(): print('world')", "простая функция"),
        ("class Test: pass", "простой класс"),
        ("import numpy as np", "импорт библиотеки")
    ]
    
    print("Тестирование эмбеддера...")
    for code, description in test
... (файл продолжается)
```

