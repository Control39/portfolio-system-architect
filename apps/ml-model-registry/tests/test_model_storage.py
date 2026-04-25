import unittest
import os
import tempfile
from apps.ml_model_registry.src.storage.model_storage import ModelStorage

class TestModelStorage(unittest.TestCase):
    
    def setUp(self):
        self.storage = ModelStorage()
        # Создание временной директории для тестов
        self.test_dir = tempfile.mkdtemp()
        self.storage.storage_path = self.test_dir
    
    def tearDown(self):
        # Очистка временных файлов
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_save_model(self):
        """Проверка сохранения модели"""
        model_data = {"name": "Test Model", "version": "1.0"}
        result = self.storage.save_model("test_model", model_data)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Model test_model saved")
    
    def test_load_model(self):
        """Проверка загрузки модели"""
        model_data = {"name": "Test Model", "version": "1.0"}
        self.storage.save_model("test_model", model_data)
        
        result = self.storage.load_model("test_model")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model_id"], "test_model")
    
    def test_delete_model(self):
        """Проверка удаления модели"""
        model_data = {"name": "Test Model", "version": "1.0"}
        self.storage.save_model("test_model", model_data)
        
        result = self.storage.delete_model("test_model")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Model test_model deleted")
    
    def test_save_model_with_none_data(self):
        """Проверка сохранения модели с None вместо данных"""
        result = self.storage.save_model("test_model", None)
        self.assertEqual(result["status"], "success")
    
    def test_load_nonexistent_model(self):
        """Проверка загрузки несуществующей модели"""
        result = self.storage.load_model("nonexistent_model")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model_id"], "nonexistent_model")
    
    def test_delete_nonexistent_model(self):
        """Проверка удаления несуществующей модели"""
        result = self.storage.delete_model("nonexistent_model")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Model nonexistent_model deleted")

if __name__ == "__main__":
    unittest.main()
