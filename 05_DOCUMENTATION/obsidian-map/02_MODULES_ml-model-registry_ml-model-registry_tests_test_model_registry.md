# Test Model Registry

- **Путь**: `02_MODULES\ml-model-registry\ml-model-registry\tests\test_model_registry.py`
- **Тип**: .PY
- **Размер**: 4,627 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
from src.core.model_registry import ModelRegistry

class TestModelRegistry(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_model(self):
        result = self.registry.register_model("test_model", {"name": "Test Model"})
        self.assertEqual(result["status"], "success")
    
    def test_get_model(self):
        self.registry.register_model("test_model", {"name": "Test Model"})
        result = self.registry.get_
... (файл продолжается)
```
