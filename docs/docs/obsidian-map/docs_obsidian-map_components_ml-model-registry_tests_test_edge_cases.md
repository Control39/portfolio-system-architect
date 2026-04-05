# Components Ml Model Registry Tests Test Edge Cases

- **Путь**: `docs\obsidian-map\components_ml-model-registry_tests_test_edge_cases.md`
- **Тип**: .MD
- **Размер**: 878 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
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
      
... (файл продолжается)
```

