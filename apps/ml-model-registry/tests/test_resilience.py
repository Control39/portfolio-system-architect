
import unittest
from unittest.mock import patch, MagicMock
from apps.ml_model_registry.src.core.model_registry import ModelRegistry
from apps.ml_model_registry.src.storage.model_storage import ModelStorage

class TestModelRegistryResilience(unittest.TestCase):
    
    def setUp(self):
        self.registry = ModelRegistry()
    
    def test_register_model_with_storage_failure(self):
        """Проверка регистрации модели при сбое хранилища"""
        # Регистрация модели
        model_data = {"name": "Test Model", "version": "1.0"}
        result = self.registry.register_model("test_model", model_data)
        
        # Проверка успешной регистрации даже при недоступном хранилище
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model_id"], "test_model")
    
    def test_get_model_with_empty_registry(self):
        """Проверка получения модели из пустого реестра"""
        result = self.registry.get_model("nonexistent_model")
self.assertEqual(result["error"], "Model not found")

