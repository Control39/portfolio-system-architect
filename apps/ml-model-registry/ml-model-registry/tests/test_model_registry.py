import unittest
from apps.ml_model_registry.src.core.model_registry import ModelRegistry

class TestModelRegistry(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_model(self):
        result = self.registry.register_model("test_model", {"name": "Test Model"})
        self.assertEqual(result["status"], "success")
    
    def test_get_model(self):
        self.registry.register_model("test_model", {"name": "Test Model"})
        result = self.registry.get_model("test_model")
        self.assertEqual(result["name"], "Test Model")
    
    def test_list_models(self):
        # Очистка реестра перед тестом
        self.registry.models = {}
        
        # Проверка пустого списка
        result = self.registry.list_models()
        self.assertEqual(result, [])
        
        # Добавление моделей
        self.registry.register_model("test_model_1", {"name": "Test Model 1"})
        self.registry.register_model("test_model_2", {"name": "Test Model 2"})
        
        # Проверка наличия моделей
        result = self.registry.list_models()
        self.assertIn("test_model_1", result)
        self.assertIn("test_model_2", result)
        self.assertEqual(len(result), 2)
    
    def test_update_model(self):
        # Регистрация модели
        self.registry.register_model("test_model", {"name": "Test Model", "version": "1.0"})
        
        # Обновление модели
        update_data = {"version": "2.0", "description": "Updated model"}
        result = self.registry.update_model("test_model", update_data)
        
        # Проверка результата обновления
        self.assertEqual(result["status"], "success")
        
        # Проверка обновленных данных
        updated_model = self.registry.get_model("test_model")
        self.assertEqual(updated_model["version"], "2.0")
        self.assertEqual(updated_model["description"], "Updated model")
    
    def test_delete_model(self):
        # Регистрация модели
        self.registry.register_model("test_model", {"name": "Test Model"})
        
        # Удаление модели
        result = self.registry.delete_model("test_model")
        
        # Проверка результата удаления
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель удалена
        deleted_model = self.registry.get_model("test_model")
        self.assertEqual(deleted_model["error"], "Model not found")
    
    def test_search_models(self):
        # Регистрация тестовых моделей
        self.registry.register_model("model_1", {"name": "Image Classifier", "type": "CNN"})
        self.registry.register_model("model_2", {"name": "Text Analyzer", "type": "NLP"})
        self.registry.register_model("model_3", {"name": "Data Predictor", "type": "Regression"})
        
        # Поиск по имени
        results = self.registry.search_models("Image")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Image Classifier")
        
        # Поиск по ID
        results = self.registry.search_models("model_2")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Text Analyzer")
        
        # Поиск без результатов
        results = self.registry.search_models("NonExistent")
        self.assertEqual(len(results), 0)
    
    def test_get_model_versions(self):
        # Регистрация версий модели
        self.registry.register_model("image_classifier_v1", {"name": "Image Classifier", "version": "1.0"})
        self.registry.register_model("image_classifier_v2", {"name": "Image Classifier", "version": "2.0"})
        self.registry.register_model("text_analyzer_v1", {"name": "Text Analyzer", "version": "1.0"})
        
        # Получение версий
        versions = self.registry.get_model_versions("Image Classifier")
        
        # Проверка количества версий
        self.assertEqual(len(versions), 2)
        
        # Проверка сортировки по версии
        self.assertEqual(versions[0]["version"], "1.0")
        self.assertEqual(versions[1]["version"], "2.0")

if __name__ == "__main__":
    unittest.main()
