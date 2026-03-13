# Test Security

- **Путь**: `components\ml-model-registry\tests\test_security.py`
- **Тип**: .PY
- **Размер**: 3,767 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
from src.core.model_registry import ModelRegistry

class TestModelRegistrySecurity(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_model_id_injection_attempt(self):
        """Проверка попытки инъекции через ID модели"""
        # Попытка инъекции через ID модели
        malicious_id = "test_model'; DROP TABLE models; --"
        model_data = {"name": "Test Model", "version": "1.0"}
        
        result = self.registry.re
... (файл продолжается)
```
