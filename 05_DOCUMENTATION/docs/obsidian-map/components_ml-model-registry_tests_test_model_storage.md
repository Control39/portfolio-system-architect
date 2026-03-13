# Test Model Storage

- **Путь**: `components\ml-model-registry\tests\test_model_storage.py`
- **Тип**: .PY
- **Размер**: 2,816 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
import os
import tempfile
import json
from src.storage.model_storage import ModelStorage

class TestModelStorage(unittest.TestCase):
    
    def setUp(self):
        self.storage = ModelStorage()
        # Создание временной директории для тестов
        self.test_dir = tempfile.mkdtemp()
        self.storage.storage_path = self.test_dir
    
    def tearDown(self):
        # Очистка временных файлов
        for file in os.listdir(self.test_dir):
            os.remove(os.path.jo
... (файл продолжается)
```
