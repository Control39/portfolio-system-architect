# Components Ml Model Registry Src Core Model Registry

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_ml-model-registry_src_core_model_registry.md`
- **Тип**: .MD
- **Размер**: 894 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
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
        return {"status": "success", "
... (файл продолжается)
```
