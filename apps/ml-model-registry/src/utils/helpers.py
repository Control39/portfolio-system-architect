def validate_model_metadata(metadata):
    """Проверка метаданных модели"""
    required_fields = ["name", "version", "framework"]
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
        "framework": model_data.get("framework"),
        "created_at": model_data.get("created_at"),
    }
