# Components Ml Model Registry Tests Test Security

- **Путь**: `docs\obsidian-map\components_ml-model-registry_tests_test_security.md`
- **Тип**: .MD
- **Размер**: 859 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
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
        # Попытка инъ
... (файл продолжается)
```
