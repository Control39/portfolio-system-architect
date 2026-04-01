# Components Ml Model Registry Tests Test Performance

- **Путь**: `docs\obsidian-map\components_ml-model-registry_tests_test_performance.md`
- **Тип**: .MD
- **Размер**: 881 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Test Performance

- **Путь**: `components\ml-model-registry\tests\test_performance.py`
- **Тип**: .PY
- **Размер**: 3,465 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
import time
from src.core.model_registry import ModelRegistry

class TestModelRegistryPerformance(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_many_models_performance(self):
        """Проверка производительности при регистр
... (файл продолжается)
```

