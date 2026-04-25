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

    def list_models(self):
        """Список всех моделей"""
        return list(self.models.keys())

    def update_model(self, model_id, model_data):
        """Обновление информации о модели"""
        if model_id in self.models:
            self.models[model_id].update(model_data)
            return {"status": "success", "model_id": model_id}
        return {"status": "error", "message": "Model not found"}

    def delete_model(self, model_id):
        """Удаление модели"""
        if model_id in self.models:
            del self.models[model_id]
            return {"status": "success", "message": f"Model {model_id} deleted"}
        return {"status": "error", "message": "Model not found"}

    def search_models(self, query):
        """Поиск моделей по имени или другим критериям"""
        results = []
        for model_id, model_data in self.models.items():
            if query.lower() in model_data.get("name", "").lower() or query in model_id:
                results.append({**model_data, "id": model_id})
        return results

    def get_model_versions(self, model_name):
        """Получение всех версий модели по имени"""
        versions = []
        for model_id, model_data in self.models.items():
            if model_data.get("name") == model_name:
                versions.append({**model_data, "id": model_id})
        return sorted(versions, key=lambda x: x.get("version", ""))

