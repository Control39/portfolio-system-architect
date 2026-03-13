# Components Ml Model Registry Tests Test Model Storage

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_ml-model-registry_tests_test_model_storage.md`
- **Тип**: .MD
- **Размер**: 870 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
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
        self.test_dir = tempfile.mkdtemp
... (файл продолжается)
```
