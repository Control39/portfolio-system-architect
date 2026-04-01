import unittest
from hypothesis import given, strategies as st
from apps.ml_model_registry.src.core.model_registry import ModelRegistry

class TestModelRegistryFuzz(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    @given(st.text(min_size=1, max_size=100))
    def test_register_model_with_random_id(self, model_id):
        """Fuzz-тестирование регистрации модели с произвольными идентификаторами"""
        model_data = {"name": "Test Model", "version": "1.0"}
        result = self.registry.register_model(model_id, model_data)
        
        # Проверка, что регистрация прошла успешно
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель можно получить
        retrieved_model = self.registry.get_model(model_id)
        self.assertEqual(retrieved_model["name"], "Test Model")
    
    @given(st.dictionaries(st.text(min_size=1), st.text()))
    def test_register_model_with_random_data(self, model_data):
        """Fuzz-тестирование регистрации модели с произвольными данными"""
        model_id = "test_model"
        result = self.registry.register_model(model_id, model_data)
        
        # Проверка, что регистрация прошла успешно
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель можно получить
        retrieved_model = self.registry.get_model(model_id)
        # Проверяем, что все ключи из исходных данных присутствуют в полученной модели
        for key in model_data:
            self.assertIn(key, retrieved_model)
    
    @given(st.text())
    def test_get_model_with_random_id(self, model_id):
        """Fuzz-тестирование получения модели с произвольными идентификаторами"""
        result = self.registry.get_model(model_id)
        
        # Результат должен быть словарем
        self.assertIsInstance(result, dict)
        
        # Если модель не найдена, должен возвращаться словарь с ошибкой
        if "error" in result:
            self.assertEqual(result["error"], "Model not found")
    
    @given(st.text(min_size=1, max_size=100))
    def test_update_model_with_random_id(self, model_id):
        """Fuzz-тестирование обновления модели с произвольными идентификаторами"""
        # Регистрация модели
        self.registry.register_model("existing_model", {"name": "Existing Model"})
        
        # Попытка обновления с произвольным ID
        update_data = {"version": "2.0"}
        result = self.registry.update_model(model_id, update_data)
        
        # Результат должен быть словарем
        self.assertIsInstance(result, dict)
        
        # Если модель не найдена, статус должен быть "error"
        if result.get("status") == "error":
            self.assertEqual(result["message"], "Model not found")
    
    @given(st.text(min_size=1, max_size=100))
    def test_delete_model_with_random_id(self, model_id):
        """Fuzz-тестирование удаления модели с произвольными идентификаторами"""
        # Регистрация модели
        self.registry.register_model("existing_model", {"name": "Existing Model"})
        
        # Попытка удаления с произвольным ID
        result = self.registry.delete_model(model_id)
        
        # Результат должен быть словарем
        self.assertIsInstance(result, dict)
        
        # Если модель не найдена, статус должен быть "error"
        if result.get("status") == "error":
            self.assertEqual(result["message"], "Model not found")

if __name__ == "__main__":
    unittest.main()
