# Components Ml Model Registry Tests Test Model Registry

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_ml-model-registry_tests_test_model_registry.md`
- **Тип**: .MD
- **Размер**: 811 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
# Test Model Registry

- **Путь**: `components\ml-model-registry\tests\test_model_registry.py`
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
 
... (файл продолжается)
```
