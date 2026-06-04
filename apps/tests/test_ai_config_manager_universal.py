"""
Универсальные тесты для интеграции AI Config Manager
Этот файл тестирует все сервисы одновременно
"""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent.parent

SERVICES: list[dict[str, str]] = [
    {"folder": "auth_service", "class": "AuthServiceConfig", "key": "auth_service"},
    {
        "folder": "career_development",
        "class": "CareerDevelopmentConfig",
        "key": "career_development",
    },
    {"folder": "cognitive_agent", "class": "CognitiveAgentConfig", "key": "cognitive_agent"},
    {"folder": "decision_engine", "class": "DecisionEngineConfig", "key": "decision_engine"},
    {
        "folder": "infra_orchestrator",
        "class": "InfraOrchestratorConfig",
        "key": "infra_orchestrator",
    },
    {"folder": "it_compass", "class": "ItCompassConfig", "key": "it_compass"},
    {
        "folder": "job_automation_agent",
        "class": "JobAutomationAgentConfig",
        "key": "job_automation_agent",
    },
    {"folder": "knowledge_graph", "class": "KnowledgeGraphConfig", "key": "knowledge_graph"},
    {"folder": "mcp_server", "class": "McpServerConfig", "key": "mcp_server"},
    {"folder": "ml_model_registry", "class": "MlModelRegistryConfig", "key": "ml_model_registry"},
    {
        "folder": "portfolio_organizer",
        "class": "PortfolioOrganizerConfig",
        "key": "portfolio_organizer",
    },
    {"folder": "system_proof", "class": "SystemProofConfig", "key": "system_proof"},
    {
        "folder": "thought_architecture",
        "class": "ThoughtArchitectureConfig",
        "key": "thought_architecture",
    },
]


def load_config_module(service: dict[str, str]):
    """Динамическая загрузка модуля интеграции"""
    src_path = REPO_ROOT / "apps" / service["folder"] / "src"
    config_file = src_path / "config_integration.py"

    if not config_file.exists():
        pytest.skip(f"Файл интеграции не найден: {config_file}")

    import importlib.util

    spec = importlib.util.spec_from_file_location("config_integration", config_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class TestAIConfigManagerIntegration:
    """Общие тесты для всех сервисов"""

    def test_ai_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from apps.ai_config_manager.src.config_manager import ConfigManager

            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    @pytest.mark.parametrize("service", SERVICES)
    def test_config_module_exists(self, service: dict[str, str]):
        """Проверка что модуль интеграции существует"""
        config_file = REPO_ROOT / "apps" / service["folder"] / "src" / "config_integration.py"
        assert config_file.exists(), f"Модуль интеграции не найден: {config_file}"

    @pytest.mark.parametrize("service", SERVICES)
    def test_config_class_exists(self, service: dict[str, str]):
        """Проверка что класс конфигурации существует"""
        module = load_config_module(service)
        assert hasattr(module, service["class"]), f"Класс {service['class']} не найден"

    @pytest.mark.parametrize("service", SERVICES)
    def test_get_config_function_exists(self, service: dict[str, str]):
        """Проверка что функция get_config существует"""
        module = load_config_module(service)
        assert hasattr(module, "get_config"), "Функция get_config не найдена"
        assert callable(module.get_config), "get_config не вызываемая"

    @pytest.mark.parametrize("service", SERVICES)
    def test_reload_config_function_exists(self, service: dict[str, str]):
        """Проверка что функция reload_config существует"""
        module = load_config_module(service)
        assert hasattr(module, "reload_config"), "Функция reload_config не найдена"
        assert callable(module.reload_config), "reload_config не вызываемая"

    @pytest.mark.parametrize("service", SERVICES)
    def test_config_get_config_returns_dict(self, service: dict[str, str]):
        """Проверка что get_config() возвращает dict"""
        module = load_config_module(service)
        config_instance = module.get_config()
        result = config_instance.get_config()
        assert isinstance(
            result, dict
        ), f"get_config() должно возвращать dict, получено {type(result)}"

    @pytest.mark.parametrize("service", SERVICES)
    def test_config_reload_works(self, service: dict[str, str]):
        """Проверка что reload() не выбрасывает исключений"""
        module = load_config_module(service)
        # Не должно выбрасывать исключений
        module.reload_config()

    @pytest.mark.parametrize("service", SERVICES)
    def test_config_is_available_method(self, service: dict[str, str]):
        """Проверка метода is_available()"""
        module = load_config_module(service)
        config_instance = module.get_config()
        assert hasattr(config_instance, "is_available"), "Метод is_available не найден"
        assert callable(config_instance.is_available), "is_available не вызываемая"

    @pytest.mark.parametrize("service", SERVICES)
    def test_singleton_pattern(self, service: dict[str, str]):
        """Проверка singleton паттерна"""
        module = load_config_module(service)
        config1 = module.get_config()
        config2 = module.get_config()
        assert config1 is config2, "Singleton паттерн нарушен"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
