import unittest
from apps.ml_model_registry.src.core.model_registry import ModelRegistry

class TestModelRegistrySecurity(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_model_id_injection_attempt(self):
        """Проверка попытки инъекции через ID модели"""
        # Попытка инъекции через ID модели
        malicious_id = "test_model'; DROP TABLE models; --"
        model_data = {"name": "Test Model", "version": "1.0"}
        
        result = self.registry.register_model(malicious_id, model_data)
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель была зарегистрирована с точным ID
        retrieved_model = self.registry.get_model(malicious_id)
        self.assertEqual(retrieved_model["name"], "Test Model")
    
    def test_model_data_injection_attempt(self):
        """Проверка попытки инъекции через данные модели"""
        model_id = "test_model"
        malicious_data = {
            "name": "Test Model",
            "version": "1.0'; DROP TABLE models; --",
            "description": "Test description"
        }
        
        result = self.registry.register_model(model_id, malicious_data)
        self.assertEqual(result["status"], "success")
        
        # Проверка, что данные сохранены как есть без выполнения инъекции
        retrieved_model = self.registry.get_model(model_id)
        self.assertEqual(retrieved_model["version"], "1.0'; DROP TABLE models; --")
    
    def test_xss_attempt_in_model_data(self):
        """Проверка попытки XSS через данные модели"""
        model_id = "test_model"
        xss_data = {
            "name": "<script>alert('XSS')</script>",
            "version": "1.0",
            "description": "Test description"
        }
        
        result = self.registry.register_model(model_id, xss_data)
        self.assertEqual(result["status"], "success")
        
        # Проверка, что данные сохранены как есть
        retrieved_model = self.registry.get_model(model_id)
        self.assertEqual(retrieved_model["name"], "<script>alert('XSS')</script>")
    
    def test_path_traversal_attempt(self):
        """Проверка попытки обхода путей файловой системы"""
        malicious_id = "../../../etc/passwd"
        model_data = {"name": "Test Model", "version": "1.0"}
        
        result = self.registry.register_model(malicious_id, model_data)
        self.assertEqual(result["status"], "success")
        
        # Проверка, что модель была зарегистрирована с точным ID
        retrieved_model = self.registry.get_model(malicious_id)
        self.assertEqual(retrieved_model["name"], "Test Model")
    
    def test_sql_injection_in_search(self):
        """Проверка попытки SQL-инъекции через поиск"""
        # Регистрация тестовой модели
        self.registry.register_model("test_model", {
            "name": "Test Model",
            "version": "1.0"
        })
        
        # Попытка SQL-инъекции через поиск
        malicious_query = "test' OR '1'='1"
        results = self.registry.search_models(malicious_query)
        
        # Проверка, что инъекция не сработала
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
