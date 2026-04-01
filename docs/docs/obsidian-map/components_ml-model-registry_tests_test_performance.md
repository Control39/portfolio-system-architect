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
        """Проверка производительности при регистрации множества моделей"""
        start_time = time.time()
        
        # Регистрация 1000 моделей
        for i in range(1000):
            model_data = {
                "name": f"Model 
... (файл продолжается)
```

