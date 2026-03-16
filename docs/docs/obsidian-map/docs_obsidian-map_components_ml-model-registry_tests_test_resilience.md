# Components Ml Model Registry Tests Test Resilience

- **Путь**: `docs\obsidian-map\components_ml-model-registry_tests_test_resilience.md`
- **Тип**: .MD
- **Размер**: 862 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Test Resilience

- **Путь**: `components\ml-model-registry\tests\test_resilience.py`
- **Тип**: .PY
- **Размер**: 1,159 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```

import unittest
from unittest.mock import patch, MagicMock
from src.core.model_registry import ModelRegistry
from src.storage.model_storage import ModelStorage

class TestModelRegistryResilience(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_m
... (файл продолжается)
```
