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
    
    def test_register_model_with_storage_failure(self):
        """Проверка регистрации модели при сбое хранилища"""
        # Регистрация модели
        model_data = {"name": "Test Model", "version": "1.0"}
     
... (файл продолжается)
```

