# Test Integration

- **Путь**: `components\ml-model-registry\tests\test_integration.py`
- **Тип**: .PY
- **Размер**: 4,883 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
import os
import tempfile
import json
from src.core.model_registry import ModelRegistry
from src.storage.model_storage import ModelStorage

class TestModelRegistryIntegration(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
        self.storage = ModelStorage()
        # Создание временной директории для тестов
        self.test_dir = tempfile.mkdtemp()
        self.storage.storage_path = self.test_dir
    
    def tearDown(self):
        # Оч
... (файл продолжается)
```

