import os
import tempfile
import unittest

from apps.ml_model_registry.src.core.model_registry import ModelRegistry
from src.storage.model_storage import ModelStorage


class TestModelRegistryIntegration(unittest.TestCase):
    def setUp(self):
        self.registry = ModelRegistry()
        self.storage = ModelStorage()
        # Создание временной директории для тестов
        self.test_dir = tempfile.mkdtemp()
        self.storage.storage_path = self.test_dir

    def tearDown(self):
        # Очистка временных файлов
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_register_and_save_model(self):
        """Проверка регистрации и сохранения модели"""
        model_data = {
            "name": "Test Model",
            "version": "1.0",
            "description": "A test model for integration testing",
        }

        # Регистрация модели
        result = self.registry.register_model("test_model", model_data)
        self.assertEqual(result["status"], "success")

        # Сохранение модели
        save_result = self.storage.save_model("test_model", model_data)
        self.assertEqual(save_result["status"], "success")

        # Проверка, что модель зарегистрирована
        registered_model = self.registry.get_model("test_model")
        self.assertEqual(registered_model["name"], "Test Model")
        self.assertEqual(registered_model["version"], "1.0")

    def test_full_model_lifecycle(self):
        """Проверка полного цикла жизни модели"""
        model_data = {
            "name": "Lifecycle Test Model",
            "version": "1.0",
            "description": "Model for testing full lifecycle",
        }

        # 1. Регистрация модели
        self.registry.register_model("lifecycle_model", model_data)
        models = self.registry.list_models()
        self.assertIn("lifecycle_model", models)

        # 2. Обновление модели
        update_data = {"version": "2.0", "accuracy": 0.95}
        update_result = self.registry.update_model("lifecycle_model", update_data)
        self.assertEqual(update_result["status"], "success")

        # Проверка обновленных данных
        updated_model = self.registry.get_model("lifecycle_model")
        self.assertEqual(updated_model["version"], "2.0")
        self.assertEqual(updated_model["accuracy"], 0.95)

        # 3. Поиск модели
        search_results = self.registry.search_models("Lifecycle")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["name"], "Lifecycle Test Model")

        # 4. Удаление модели
        delete_result = self.registry.delete_model("lifecycle_model")
        self.assertEqual(delete_result["status"], "success")

        # Проверка, что модель удалена
        models_after_delete = self.registry.list_models()
        self.assertNotIn("lifecycle_model", models_after_delete)

    def test_multiple_model_versions(self):
        """Проверка работы с несколькими версиями модели"""
        # Регистрация нескольких версий модели
        self.registry.register_model(
            "classifier_v1",
            {"name": "Image Classifier", "version": "1.0", "accuracy": 0.85},
        )

        self.registry.register_model(
            "classifier_v2",
            {"name": "Image Classifier", "version": "2.0", "accuracy": 0.92},
        )

        self.registry.register_model(
            "classifier_v3",
            {"name": "Image Classifier", "version": "3.0", "accuracy": 0.95},
        )

        # Получение всех версий
        versions = self.registry.get_model_versions("Image Classifier")
        self.assertEqual(len(versions), 3)

        # Проверка сортировки по версии
        self.assertEqual(versions[0]["version"], "1.0")
        self.assertEqual(versions[1]["version"], "2.0")
        self.assertEqual(versions[2]["version"], "3.0")

        # Проверка точности каждой версии
        self.assertEqual(versions[0]["accuracy"], 0.85)
        self.assertEqual(versions[1]["accuracy"], 0.92)
        self.assertEqual(versions[2]["accuracy"], 0.95)


if __name__ == "__main__":
    unittest.main()
