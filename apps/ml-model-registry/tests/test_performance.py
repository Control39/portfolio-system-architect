import time
import unittest

from apps.ml_model_registry.src.core.model_registry import ModelRegistry


class TestModelRegistryPerformance(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistry()

    def test_register_many_models_performance(self):
        """Проверка производительности при регистрации множества моделей"""
        start_time = time.time()

        # Регистрация 1000 моделей
        for i in range(1000):
            model_data = {
                "name": f"Model {i}",
                "version": "1.0",
                "description": f"Description for model {i}",
            }
            self.registry.register_model(f"model_{i}", model_data)

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверка, что операция выполняется за разумное время (менее 5 секунд)
        self.assertLess(execution_time, 5.0)

        # Проверка, что все модели зарегистрированы
        models = self.registry.list_models()
        self.assertEqual(len(models), 1000)

    def test_search_models_performance(self):
        """Проверка производительности поиска моделей"""
        # Регистрация 1000 моделей
        for i in range(1000):
            model_data = {
                "name": f"Model {i}",
                "version": "1.0",
                "description": f"Description for model {i}",
            }
            self.registry.register_model(f"model_{i}", model_data)

        start_time = time.time()

        # Поиск моделей
        results = self.registry.search_models("Model 5")

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверка, что операция выполняется за разумное время (менее 1 секунды)
        self.assertLess(execution_time, 1.0)

        # Проверка, что найдены некоторые модели
        self.assertGreater(len(results), 0)

    def test_get_model_versions_performance(self):
        """Проверка производительности получения версий модели"""
        # Регистрация 100 версий модели
        for i in range(100):
            model_data = {
                "name": "Test Model",
                "version": f"{i}.0",
                "description": f"Version {i}.0 of test model",
            }
            self.registry.register_model(f"test_model_v{i}", model_data)

        start_time = time.time()

        # Получение версий модели
        versions = self.registry.get_model_versions("Test Model")

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверка, что операция выполняется за разумное время (менее 1 секунды)
        self.assertLess(execution_time, 1.0)

        # Проверка, что получены все версии
        self.assertEqual(len(versions), 100)

if __name__ == "__main__":
    unittest.main()
