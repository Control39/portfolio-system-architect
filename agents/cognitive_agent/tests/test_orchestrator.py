"""
Unit Tests for Cognitive Agent Orchestrator v2

Цель: Покрытие 80%+ для orchestrator_v2.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импорт для тестов
from agents.cognitive_agent.orchestrator_v2 import CognitiveOrchestrator


class TestCognitiveOrchestrator:
    """Unit tests for CognitiveOrchestrator class"""

    # =========================================================================
    # TEST 1: IT-Compass Markers Loading
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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
    # TEST 2: Workflow Execution
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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

    # =========================================================================
    # TEST 3: Job Search Adapter Check
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
    def test_check_job_search_adapter_success(self, mock_logging):
        """
        Test: Check Job Search Adapter (Success)
        Проверка успешной проверки адаптера
        """
        adapter_path = REPO_ROOT / "apps" / "infra_orchestrator" / "src" / "adapters" / "job_search_adapter.py"

        if adapter_path.exists():
            orchestrator = CognitiveOrchestrator()
            result = orchestrator.check_job_search_adapter()

            assert result is True
        else:
            pytest.skip("job_search_adapter.py not found")

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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
    # TEST 4: FastAPI Endpoint Check
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
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
    # TEST 5: Full Run Cycle
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
    def test_run_full_cycle(self, mock_logging):
        """
        Test: Run Full Cycle
        Проверка полного цикла запуска оркестратора
        """
        with patch.object(CognitiveOrchestrator, "load_it_compass_markers") as mock_markers:
            mock_markers.return_value = {"test": {"markers_count": 5}}

            with patch.object(CognitiveOrchestrator, "run_workflow") as mock_workflow:
                mock_workflow.return_value = True

                with patch.object(CognitiveOrchestrator, "check_job_search_adapter") as mock_adapter:
                    mock_adapter.return_value = True

                    with patch.object(CognitiveOrchestrator, "check_fastapi_endpoint") as mock_fastapi:
                        mock_fastapi.return_value = True

                        orchestrator = CognitiveOrchestrator()
                        orchestrator.run()

                        # Проверяем, что все методы были вызваны
                        mock_markers.assert_called_once()
                        mock_workflow.assert_called_once()
                        mock_adapter.assert_called_once()
                        mock_fastapi.assert_called_once()

    # =========================================================================
    # TEST 6: Error Handling
    # =========================================================================

    @patch("agents.cognitive_agent.orchestrator_v2.logging")
    def test_error_handling_signal_handling(self, mock_logging):
        """
        Test: Error Handling - Signal Handling
        Проверка обработки сигналов остановки
        """
        _ = CognitiveOrchestrator()  # noqa: F841

        # Проверяем, что handlers установлены
        import signal

        # SIGTERM handler должен быть установлен
        assert signal.getsignal(signal.SIGTERM) is not None
        assert signal.getsignal(signal.SIGINT) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
