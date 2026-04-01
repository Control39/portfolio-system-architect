# Test Edge Cases

- **Путь**: `components\ml-model-registry\tests\test_edge_cases.py`
- **Тип**: .PY
- **Размер**: 3,248 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
from src.core.model_registry import ModelRegistry

class TestModelRegistryEdgeCases(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_model_with_none_data(self):
        """Проверка регистрации модели с None вместо данных"""
        result = self.registry.register_model("test_model", None)
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель была зарегистрирована
        model 
... (файл продолжается)
```

