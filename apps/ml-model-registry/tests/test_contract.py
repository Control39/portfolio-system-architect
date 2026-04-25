import unittest

from apps.ml_model_registry.src.core.model_registry import ModelRegistry


class TestModelRegistryContract(unittest.TestCase):
    """Контрактные тесты для проверки совместимости интерфейсов"""

    def setUp(self):
        self.registry = ModelRegistry()

    def test_register_model_contract(self):
        """Проверка контракта для метода register_model"""
        model_id = "contract_test_model"
        model_data = {
            "name": "Contract Test Model",
            "version": "1.0",
            "description": "Model for contract testing",
            "tags": ["test", "contract"],
        }

        # Вызов тестируемого метода
        result = self.registry.register_model(model_id, model_data)

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("model_id", result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model_id"], model_id)

    def test_get_model_contract(self):
        """Проверка контракта для метода get_model"""
        model_id = "contract_test_model"
        model_data = {
            "name": "Contract Test Model",
            "version": "1.0",
            "description": "Model for contract testing",
        }

        # Предварительная регистрация модели
        self.registry.register_model(model_id, model_data)

        # Вызов тестируемого метода
        result = self.registry.get_model(model_id)

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("version", result)
        self.assertEqual(result["name"], model_data["name"])
        self.assertEqual(result["version"], model_data["version"])

    def test_get_model_not_found_contract(self):
        """Проверка контракта для метода get_model при отсутствующей модели"""
        # Вызов тестируемого метода для несуществующей модели
        result = self.registry.get_model("nonexistent_model")

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Model not found")

    def test_list_models_contract(self):
        """Проверка контракта для метода list_models"""
        # Очистка реестра перед тестом
        self.registry.models = {}

        # Добавление тестовых моделей
        self.registry.register_model("model_1", {"name": "Model 1"})
        self.registry.register_model("model_2", {"name": "Model 2"})

        # Вызов тестируемого метода
        result = self.registry.list_models()

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("model_1", result)
        self.assertIn("model_2", result)

    def test_update_model_contract(self):
        """Проверка контракта для метода update_model"""
        model_id = "contract_test_model"
        initial_data = {"name": "Initial Model", "version": "1.0"}
        update_data = {"version": "2.0", "description": "Updated model"}

        # Предварительная регистрация модели
        self.registry.register_model(model_id, initial_data)

        # Вызов тестируемого метода
        result = self.registry.update_model(model_id, update_data)

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("model_id", result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model_id"], model_id)

        # Проверка, что модель была обновлена
        updated_model = self.registry.get_model(model_id)
        self.assertEqual(updated_model["version"], "2.0")
        self.assertEqual(updated_model["description"], "Updated model")
        self.assertEqual(updated_model["name"], "Initial Model")  # Неизменное поле

    def test_delete_model_contract(self):
        """Проверка контракта для метода delete_model"""
        model_id = "contract_test_model"

        # Предварительная регистрация модели
        self.registry.register_model(model_id, {"name": "Test Model"})

        # Вызов тестируемого метода
        result = self.registry.delete_model(model_id)

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("message", result)
        self.assertEqual(result["status"], "success")

        # Проверка, что модель была удалена
        deleted_model = self.registry.get_model(model_id)
        self.assertIn("error", deleted_model)
        self.assertEqual(deleted_model["error"], "Model not found")

    def test_search_models_contract(self):
        """Проверка контракта для метода search_models"""
        # Регистрация тестовых моделей
        self.registry.register_model("image_classifier", {"name": "Image Classifier", "type": "CNN"})
        self.registry.register_model("text_analyzer", {"name": "Text Analyzer", "type": "NLP"})

        # Вызов тестируемого метода
        result = self.registry.search_models("Image")

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertIn("name", result[0])
        self.assertIn("type", result[0])
        self.assertIn("id", result[0])
        self.assertEqual(result[0]["name"], "Image Classifier")

    def test_get_model_versions_contract(self):
        """Проверка контракта для метода get_model_versions"""
        model_name = "Versioned Model"

        # Регистрация версий модели
        self.registry.register_model("versioned_model_v1", {"name": model_name, "version": "1.0"})
        self.registry.register_model("versioned_model_v2", {"name": model_name, "version": "2.0"})

        # Вызов тестируемого метода
        result = self.registry.get_model_versions(model_name)

        # Проверка структуры возвращаемого значения
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        for version in result:
            self.assertIsInstance(version, dict)
            self.assertIn("name", version)
            self.assertIn("version", version)
            self.assertIn("id", version)
            self.assertEqual(version["name"], model_name)

        # Проверка сортировки по версии
        self.assertEqual(result[0]["version"], "1.0")
        self.assertEqual(result[1]["version"], "2.0")

if __name__ == "__main__":
    unittest.main()

