# Helpers

- **Путь**: `components\ml-model-registry\src\utils\helpers.py`
- **Тип**: .PY
- **Размер**: 678 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
def validate_model_metadata(metadata):
    """Проверка метаданных модели"""
    required_fields = ['name', 'version', 'framework']
    for field in required_fields:
        if field not in metadata:
            return False, f"Missing required field: {field}"
    return True, "Valid"

def format_model_info(model_data):
    """Форматирование информации о модели"""
    return {
        "id": model_data.get("id"),
        "name": model_data.get("name"),
        "version": model_data.get("version"),
... (файл продолжается)
```

