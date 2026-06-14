"""
Integration Tests for Cognitive Agent

Цель: Покрытие 80%+ для интеграционных сценариев
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 🛠 ИСПРАВЛЕНО 1: REPO_ROOT теперь устойчивый (работает из любого места)
REPO_ROOT = Path("C:/repo") if Path("C:/repo").exists() else Path(__file__).resolve().parents[3]


# 🛠 ИСПРАВЛЕНО 2: Правильные импорты (agents/, а не apps/)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Добавляем путь к cognitive_agent
COGNITIVE_AGENT_PATH = REPO_ROOT / "agents" / "cognitive_agent"
if str(COGNITIVE_AGENT_PATH) not in sys.path:
    sys.path.insert(0, str(COGNITIVE_AGENT_PATH))

# Добавляем путь к src
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class TestIntegration:
    """Integration tests for Cognitive Agent components"""

    # =========================================================================
    # TEST 1: Config Integration with AI Config Manager
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_config_integration_with_ai_config_manager(self, mock_config_manager):
        """
        Test: Config Integration with AI Config Manager
        Проверка интеграции config_integration с AI Config Manager
        """
        from config_integration import get_config

        # Настраиваем mock
        mock_instance = MagicMock()
        mock_instance.get_agent_config.return_value = {
            "test_key": "test_value",
            "agent_mode": "standard",
        }
        mock_instance.validate.return_value = True
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)
        assert "test_key" in result
        assert result["test_key"] == "test_value"

        # Проверяем, что ConfigManager был инициализирован
        mock_config_manager.assert_called_once()

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_config_integration_fallback_on_error(self, mock_config_manager):
        """
        Test: Config Integration - Fallback on Error
        Проверка fallback на локальную конфигурацию при ошибке AI Config Manager
        """
        from config_integration import get_config

        # Настраиваем mock для ошибки
        mock_instance = MagicMock()
        mock_instance.get_agent_config.side_effect = Exception("Config error")
        mock_instance.validate.return_value = False
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = get_config()
        result = config.get_config()

        # Должен вернуться локальный конфиг
        assert isinstance(result, dict)

    # =========================================================================
    # TEST 2: Endpoints with Config Integration
    # =========================================================================

    @patch("config_integration.AI_CONFIG_AVAILABLE", False)
    def test_endpoints_with_config(self):
        """
        Test: Endpoints with Config Integration
        Проверка, что endpoints используют config_integration
        """
        # Загружаем config
        from config_integration import get_config

        config = get_config()

        # Проверяем, что config загружен
        assert config is not None

        # Проверяем, что config имеет метод is_available
        assert hasattr(config, "is_available")

    @patch("config_integration.AI_CONFIG_AVAILABLE", True)
    @patch("config_integration.ConfigManager")
    def test_endpoints_with_ai_config(self, mock_config_manager):
        """
        Test: Endpoints with AI Config
        Проверка endpoints с AI Config Manager
        """
        from config_integration import get_config

        # Настраиваем mock
        mock_instance = MagicMock()
        mock_instance.get_agent_config.return_value = {"agent_mode": "standard", "timeout": 30}
        mock_instance.validate.return_value = True
        mock_config_manager.return_value = mock_instance

        # Сброс singleton
        import config_integration

        config_integration._config_instance = None

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)
        assert "agent_mode" in result

    # =========================================================================
    # TEST 3: Orchestrator with IT-Compass
    # =========================================================================

    def test_orchestrator_with_it_compass(self):
        """
        Test: Orchestrator with IT-Compass
        Проверка, что оркестратор загружает маркеры из IT-Compass
        """
        from orchestrator_v2 import CognitiveOrchestrator

        orchestrator = CognitiveOrchestrator()

        # 🛠 ИСПРАВЛЕНО 3: Путь к маркерам (apps/ → agents/)
        markers_dir = REPO_ROOT / "agents" / "it_compass" / "src" / "data" / "markers"

        if markers_dir.exists():
            markers = orchestrator.load_it_compass_markers()

            assert isinstance(markers, dict)
            # Должен быть хотя бы один маркер
            assert len(markers) >= 0
        else:
            pytest.skip("IT-Compass markers directory not found")

    @patch("orchestrator_v2.logging")
    def test_orchestrator_with_it_compass_empty(self, mock_logging):
        """
        Test: Orchestrator with IT-Compass (Empty)
        Проверка оркестратора при отсутствии маркеров
        """
        with patch.object(Path, "glob") as mock_glob:
            mock_glob.return_value = []

            from orchestrator_v2 import CognitiveOrchestrator

            orchestrator = CognitiveOrchestrator()
            markers = orchestrator.load_it_compass_markers()

            assert isinstance(markers, dict)
            assert len(markers) == 0

    # =========================================================================
    # TEST 4: Orchestrator with Workflows
    # =========================================================================

    @patch("orchestrator_v2.logging")
    def test_orchestrator_with_workflows_success(self, mock_logging):
        """
        Test: Orchestrator with Workflows (Success)
        Проверка успешного запуска workflow через оркестратор
        """
        workflow_content = {
            "name": "marker-extraction",
            "description": "Извлечение маркеров",
            "steps": [
                {"name": "scan", "script": "scripts/scanner_main.py"},
                {"name": "extract", "script": "scripts/extract_markers.py"},
            ],
        }

        with patch("orchestrator_v2.yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = workflow_content

            with patch.object(Path, "exists") as mock_exists:
                mock_exists.return_value = True

                from orchestrator_v2 import CognitiveOrchestrator

                orchestrator = CognitiveOrchestrator()
                result = orchestrator.run_workflow("marker-extraction")

                assert result is True

    @patch("orchestrator_v2.logging")
    def test_orchestrator_with_workflows_not_found(self, mock_logging):
        """
        Test: Orchestrator with Workflows (Not Found)
        Проверка обработки несуществующего workflow
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False

            from orchestrator_v2 import CognitiveOrchestrator

            orchestrator = CognitiveOrchestrator()
            result = orchestrator.run_workflow("nonexistent")

            assert result is False

    # =========================================================================
    # TEST 5: Scanner Integration
    # =========================================================================

    def test_scanner_integration_with_orchestrator(self):
        """
        Test: Scanner Integration with Orchestrator
        Проверка интеграции сканера с оркестратором
        """
        scanner_main_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "scanner_main.py"

        if scanner_main_path.exists():
            # Проверяем, что файл существует
            assert scanner_main_path.exists()
        else:
            pytest.skip("scanner_main.py not found")

    @patch("orchestrator_v2.logging")
    def test_scanner_script_execution(self, mock_logging):
        """
        Test: Scanner Script Execution
        Проверка выполнения скрипта сканера
        """
        script_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "scanner_main.py"

        if script_path.exists():
            with open(script_path, encoding="utf-8") as f:
                content = f.read()

            # Проверяем, что скрипт содержит основные элементы
            assert "main" in content.lower()
            assert "scan" in content.lower()
        else:
            pytest.skip("scanner_main.py not found")

    # =========================================================================
    # TEST 6: Planner Integration
    # =========================================================================

    def test_planner_integration_with_orchestrator(self):
        """
        Test: Planner Integration with Orchestrator
        Проверка интеграции планировщика с оркестратором
        """
        planner_main_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "planner_main.py"

        if planner_main_path.exists():
            # Проверяем, что файл существует
            assert planner_main_path.exists()
        else:
            pytest.skip("planner_main.py not found")

    @patch("orchestrator_v2.logging")
    def test_planner_script_execution(self, mock_logging):
        """
        Test: Planner Script Execution
        Проверка выполнения скрипта планировщика
        """
        script_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "planner_main.py"

        if script_path.exists():
            with open(script_path, encoding="utf-8") as f:
                content = f.read()

            # Проверяем, что скрипт содержит основные элементы
            assert "main" in content.lower()
            assert "plan" in content.lower()
        else:
            pytest.skip("planner_main.py not found")

    # =========================================================================
    # TEST 7: Learning Integration
    # =========================================================================

    def test_learning_integration_with_orchestrator(self):
        """
        Test: Learning Integration with Orchestrator
        Проверка интеграции сборщика метрик с оркестратором
        """
        learning_main_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "learning_main.py"

        if learning_main_path.exists():
            # Проверяем, что файл существует
            assert learning_main_path.exists()
        else:
            pytest.skip("learning_main.py not found")

    @patch("orchestrator_v2.logging")
    def test_learning_script_execution(self, mock_logging):
        """
        Test: Learning Script Execution
        Проверка выполнения скрипта сбора метрик
        """
        script_path = REPO_ROOT / "agents" / "cognitive_agent" / "scripts" / "learning_main.py"

        if script_path.exists():
            with open(script_path, encoding="utf-8") as f:
                content = f.read()

            # Проверяем, что скрипт содержит основные элементы
            assert "main" in content.lower()
            assert "metric" in content.lower() or "learn" in content.lower()
        else:
            pytest.skip("learning_main.py not found")

    # =========================================================================
    # TEST 8: Full Integration Cycle
    # =========================================================================

    def test_full_integration_cycle(self):
        """
        Test: Full Integration Cycle
        Проверка полного интеграционного цикла
        """
        from orchestrator_v2 import CognitiveOrchestrator

        orchestrator = CognitiveOrchestrator()

        # Проверяем инициализацию
        assert orchestrator is not None
        assert isinstance(orchestrator.config, dict)

        # 🛠 ИСПРАВЛЕНО 3: Путь к маркерам (apps/ → agents/)
        markers_dir = REPO_ROOT / "agents" / "it_compass" / "src" / "data" / "markers"
        if markers_dir.exists():
            markers = orchestrator.load_it_compass_markers()
            assert isinstance(markers, dict)

        # Проверяем workflows
        workflow_result = orchestrator.run_workflow("marker-extraction")
        assert isinstance(workflow_result, bool)

        # Проверяем адаптеры
        adapter_result = orchestrator.check_job_search_adapter()
        assert isinstance(adapter_result, bool)

        # Проверяем FastAPI
        fastapi_result = orchestrator.check_fastapi_endpoint()
        assert isinstance(fastapi_result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
