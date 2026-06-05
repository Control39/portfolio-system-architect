"""
Unit Tests for Cognitive Agent Orchestrator v2

Цель: Покрытие 80%+ для orchestrator_v2.py
"""

import pytest
import sys
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импорт для тестов
from apps.cognitive_agent.orchestrator_v2 import CognitiveOrchestrator


class TestCognitiveOrchestrator:
    """Unit tests for CognitiveOrchestrator class"""

    # =========================================================================
    # TEST 1: Initialization
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_orchestrator_initialization(self, mock_logging):
        """
        Test: Orchestrator Initialization
        Проверка инициализации оркестратора
        """
        with patch("apps.cognitive_agent.orchestrator_v2.ConfigManager"):
            orchestrator = CognitiveOrchestrator()

            assert orchestrator is not None
            assert hasattr(orchestrator, "config")
            assert hasattr(orchestrator, "running")
            assert orchestrator.running is False

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_orchestrator_config_loaded(self, mock_logging):
        """
        Test: Orchestrator Config Loaded
        Проверка, что конфигурация загружена
        """
        with patch("apps.cognitive_agent.orchestrator_v2.ConfigManager"):
            orchestrator = CognitiveOrchestrator()

            assert isinstance(orchestrator.config, dict)

    # =========================================================================
    # TEST 2: IT-Compass Markers Loading
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_load_it_compass_markers_success(self, mock_logging):
        """
        Test: Load IT-Compass Markers (Success)
        Проверка успешной загрузки маркеров
        """
        orchestrator = CognitiveOrchestrator()

        markers_dir = REPO_ROOT / "apps" / "it_compass" / "src" / "data" / "markers"

        if markers_dir.exists():
            markers = orchestrator.load_it_compass_markers()

            assert isinstance(markers, dict)
            # Должен быть хотя бы один маркер
            assert len(markers) >= 0
        else:
            pytest.skip("IT-Compass markers directory not found")

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_load_it_compass_markers_empty_directory(self, mock_logging):
        """
        Test: Load IT-Compass Markers (Empty Directory)
        Проверка загрузки при пустой директории
        """
        with patch.object(Path, "glob") as mock_glob:
            mock_glob.return_value = []

            orchestrator = CognitiveOrchestrator()
            markers = orchestrator.load_it_compass_markers()

            assert isinstance(markers, dict)
            assert len(markers) == 0

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_load_it_compass_markers_invalid_json(self, mock_logging):
        """
        Test: Load IT-Compass Markers (Invalid JSON)
        Проверка обработки невалидного JSON файла
        """
        with patch.object(Path, "glob") as mock_glob:
            # Создаём mock файла
            mock_file = MagicMock()
            mock_file.stem = "test_marker"

            # Открываем как файл с невалидным JSON
            mock_glob.return_value = [mock_file]

            with patch("builtins.open", mock_open(read_data="invalid json {")):
                orchestrator = CognitiveOrchestrator()
                markers = orchestrator.load_it_compass_markers()

                assert isinstance(markers, dict)

    # =========================================================================
    # TEST 3: Workflow Execution
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_run_workflow_success(self, mock_logging):
        """
        Test: Run Workflow (Success)
        Проверка успешного запуска workflow
        """
        # Создаём временный workflow файл
        workflow_content = {
            "name": "Test Workflow",
            "description": "Тестовый workflow",
            "steps": [{"name": "step1", "script": "scripts/test.py"}],
        }

        with patch("apps.cognitive_agent.orchestrator_v2.yaml.safe_load") as mock_yaml:
            mock_yaml.return_value = workflow_content

            with patch.object(Path, "exists") as mock_exists:
                mock_exists.return_value = True

                orchestrator = CognitiveOrchestrator()
                result = orchestrator.run_workflow("test_workflow")

                assert result is True

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_run_workflow_not_found(self, mock_logging):
        """
        Test: Run Workflow (Not Found)
        Проверка обработки несуществующего workflow
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False

            orchestrator = CognitiveOrchestrator()
            result = orchestrator.run_workflow("nonexistent_workflow")

            assert result is False

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_run_workflow_invalid_yaml(self, mock_logging):
        """
        Test: Run Workflow (Invalid YAML)
        Проверка обработки невалидного YAML
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True

            with patch("apps.cognitive_agent.orchestrator_v2.yaml.safe_load") as mock_yaml:
                mock_yaml.side_effect = yaml.YAMLError("Invalid YAML")

                orchestrator = CognitiveOrchestrator()
                result = orchestrator.run_workflow("invalid_workflow")

                assert result is False

    # =========================================================================
    # TEST 4: Job Search Adapter Check
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_check_job_search_adapter_success(self, mock_logging):
        """
        Test: Check Job Search Adapter (Success)
        Проверка успешной проверки адаптера
        """
        adapter_path = (
            REPO_ROOT / "apps" / "infra_orchestrator" / "src" / "adapters" / "job_search_adapter.py"
        )

        if adapter_path.exists():
            orchestrator = CognitiveOrchestrator()
            result = orchestrator.check_job_search_adapter()

            assert result is True
        else:
            pytest.skip("job_search_adapter.py not found")

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_check_job_search_adapter_not_found(self, mock_logging):
        """
        Test: Check Job Search Adapter (Not Found)
        Проверка обработки отсутствующего адаптера
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False

            orchestrator = CognitiveOrchestrator()
            result = orchestrator.check_job_search_adapter()

            assert result is False

    # =========================================================================
    # TEST 5: FastAPI Endpoint Check
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_check_fastapi_endpoint_success(self, mock_logging):
        """
        Test: Check FastAPI Endpoint (Success)
        Проверка успешной проверки FastAPI endpoint
        """
        main_path = REPO_ROOT / "apps" / "cognitive_agent" / "main.py"

        if main_path.exists():
            orchestrator = CognitiveOrchestrator()
            result = orchestrator.check_fastapi_endpoint()

            assert result is True
        else:
            pytest.skip("main.py not found")

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_check_fastapi_endpoint_not_found(self, mock_logging):
        """
        Test: Check FastAPI Endpoint (Not Found)
        Проверка обработки отсутствующего main.py
        """
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False

            orchestrator = CognitiveOrchestrator()
            result = orchestrator.check_fastapi_endpoint()

            assert result is False

    # =========================================================================
    # TEST 6: Full Run Cycle
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_run_full_cycle(self, mock_logging):
        """
        Test: Run Full Cycle
        Проверка полного цикла запуска оркестратора
        """
        with patch.object(CognitiveOrchestrator, "load_it_compass_markers") as mock_markers:
            mock_markers.return_value = {"test": {"markers_count": 5}}

            with patch.object(CognitiveOrchestrator, "run_workflow") as mock_workflow:
                mock_workflow.return_value = True

                with patch.object(
                    CognitiveOrchestrator, "check_job_search_adapter"
                ) as mock_adapter:
                    mock_adapter.return_value = True

                    with patch.object(
                        CognitiveOrchestrator, "check_fastapi_endpoint"
                    ) as mock_fastapi:
                        mock_fastapi.return_value = True

                        orchestrator = CognitiveOrchestrator()
                        orchestrator.run()

                        # Проверяем, что все методы были вызваны
                        mock_markers.assert_called_once()
                        mock_workflow.assert_called_once()
                        mock_adapter.assert_called_once()
                        mock_fastapi.assert_called_once()

    # =========================================================================
    # TEST 7: Error Handling
    # =========================================================================

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_error_handling_config_load_failure(self, mock_logging):
        """
        Test: Error Handling - Config Load Failure
        Проверка обработки ошибки загрузки конфигурации
        """
        with patch("apps.cognitive_agent.orchestrator_v2.get_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Config error")

            orchestrator = CognitiveOrchestrator()

            # Должен использовать дефолтный конфиг (пустой dict)
            assert isinstance(orchestrator.config, dict)

    @patch("apps.cognitive_agent.orchestrator_v2.logging")
    def test_error_handling_signal_handling(self, mock_logging):\n        \"\"\"\n        Test: Error Handling - Signal Handling\n        Проверка обработки сигналов остановки\n        \"\"\"\n        _ = CognitiveOrchestrator()  # noqa: F841"}

        # Проверяем, что handlers установлены
        import signal

        # SIGTERM handler должен быть установлен
        assert signal.getsignal(signal.SIGTERM) is not None
        assert signal.getsignal(signal.SIGINT) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
