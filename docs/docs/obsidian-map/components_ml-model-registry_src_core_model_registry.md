# Model Registry

- **Путь**: `components\ml-model-registry\src\core\model_registry.py`
- **Тип**: .PY
- **Размер**: 2,182 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
class ModelRegistry:
    """Основной класс для управления реестром моделей"""
    
    def __init__(self):
        self.models = {}
    
    def register_model(self, model_id, model_data):
        """Регистрация новой модели"""
        self.models[model_id] = model_data
        return {"status": "success", "model_id": model_id}
    
    def get_model(self, model_id):
        """Получение информации о модели"""
        return self.models.get(model_id, {"error": "Model not found"})
    
    def li
... (файл продолжается)
```

