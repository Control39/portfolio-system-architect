import unittest

from apps.ml_model_registry.src.core.model_registry import ModelRegistry


class TestModelRegistryEdgeCases(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistry()

    def test_register_model_with_none_data(self):
        """Проверка регистрации модели с None вместо данных"""
        result = self.registry.register_model("test_model", None)
        self.assertEqual(result["status"], "success")

        # Проверка, что модель была зарегистрирована
        model = self.registry.get_model("test_model")
        self.assertIsNone(model)

    def test_register_model_with_empty_dict(self):
        """Проверка регистрации модели с пустым словарем"""
        result = self.registry.register_model("test_model", {})
        self.assertEqual(result["status"], "success")

        # Проверка, что модель была зарегистрирована
        model = self.registry.get_model("test_model")
        self.assertEqual(model, {})

    def test_update_nonexistent_model(self):
        """Проверка обновления несуществующей модели"""
        result = self.registry.update_model("nonexistent_model", {"version": "1.0"})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Model not found")

    def test_delete_nonexistent_model(self):
        """Проверка удаления несуществующей модели"""
        result = self.registry.delete_model("nonexistent_model")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Model not found")

    def test_get_nonexistent_model(self):
        """Проверка получения несуществующей модели"""
        result = self.registry.get_model("nonexistent_model")
        self.assertEqual(result["error"], "Model not found")

    def test_search_models_empty_registry(self):
        """Проверка поиска моделей в пустом реестре"""
        result = self.registry.search_models("test")
        self.assertEqual(result, [])

    def test_get_model_versions_nonexistent_model(self):
        """Проверка получения версий несуществующей модели"""
        result = self.registry.get_model_versions("Nonexistent Model")
        self.assertEqual(result, [])

    def test_register_model_with_special_characters(self):
        """Проверка регистрации модели со специальными символами в ID"""
        special_id = "model@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = self.registry.register_model(special_id, {"name": "Special Model"})
        self.assertEqual(result["status"], "success")

        # Проверка, что модель была зарегистрирована
        model = self.registry.get_model(special_id)
        self.assertEqual(model["name"], "Special Model")

if __name__ == "__main__":
    unittest.main()
