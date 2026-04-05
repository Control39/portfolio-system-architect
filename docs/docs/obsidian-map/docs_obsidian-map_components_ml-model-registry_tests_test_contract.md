# Components Ml Model Registry Tests Test Contract

- **Путь**: `docs\obsidian-map\components_ml-model-registry_tests_test_contract.md`
- **Тип**: .MD
- **Размер**: 877 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Test Contract

- **Путь**: `components\ml-model-registry\tests\test_contract.py`
- **Тип**: .PY
- **Размер**: 8,142 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
from src.core.model_registry import ModelRegistry

class TestModelRegistryContract(unittest.TestCase):
    """Контрактные тесты для проверки совместимости интерфейсов"""
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_model_contract(self):
        """Пр
... (файл продолжается)
```

