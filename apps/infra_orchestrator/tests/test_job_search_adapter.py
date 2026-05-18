"""
Тесты для интерфейса IJobSearch и адаптера CognitiveJobSearch
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.interfaces.job_search import IJobSearch
from apps.infra_orchestrator.src.adapters.job_search_adapter import CognitiveJobSearch


class TestCognitiveJobSearch:
    """Тесты для CognitiveJobSearch адаптера."""

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Тест успешного поиска вакансий."""
        # Создаем мок-ответ
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "vacancies": [
                {
                    "id": "123",
                    "title": "Python Developer",
                    "employer": "TechCorp",
                    "city": "Москва",
                    "payment": "от 150 000 ₽",
                    "url": "https://hh.ru/vacancy/123",
                    "content": "Ищем Python разработчика",
                    "created_at": "2026-05-18",
                }
            ]
        }
        mock_response.raise_for_status = lambda: None

        # Патчим HTTP-клиент
        with patch("apps.infra_orchestrator.src.adapters.job_search_adapter.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            MockClient.return_value = mock_client_instance

            # Создаем адаптер
            adapter = CognitiveJobSearch(base_url="http://test:8000")

            # Вызываем метод
            result = await adapter.search("Python Developer", location="Москва")

            # Проверяем результат
            assert len(result) == 1
            assert result[0]["title"] == "Python Developer"
            assert result[0]["company"] == "TechCorp"
            assert result[0]["location"] == "Москва"
            assert result[0]["source"] == "cognitive-agent"

            # Проверяем, что HTTP-запрос был вызван с правильными параметрами
            mock_client_instance.get.assert_called_once_with(
                "http://test:8000/api/v1/jobs/search",
                params={"query": "Python Developer", "location": "Москва"}
            )

    @pytest.mark.asyncio
    async def test_search_empty(self):
        """Тест пустого результата поиска."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"vacancies": []}
        mock_response.raise_for_status = lambda: None

        with patch("apps.infra_orchestrator.src.adapters.job_search_adapter.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            MockClient.return_value = mock_client_instance

            adapter = CognitiveJobSearch(base_url="http://test:8000")
            result = await adapter.search("NonExistentJob")

            assert result == []

    @pytest.mark.asyncio
    async def test_get_details(self):
        """Тест получения деталей вакансии."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "id": "123",
            "title": "Python Developer",
            "employer": "TechCorp",
            "city": "Москва",
            "payment": "от 150 000 ₽",
            "url": "https://hh.ru/vacancy/123",
            "content": "Подробное описание",
            "created_at": "2026-05-18",
        }
        mock_response.raise_for_status = lambda: None

        with patch("apps.infra_orchestrator.src.adapters.job_search_adapter.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            MockClient.return_value = mock_client_instance

            adapter = CognitiveJobSearch(base_url="http://test:8000")
            result = await adapter.get_details("123")

            assert result["title"] == "Python Developer"
            assert result["company"] == "TechCorp"
            assert result["job_id"] == "123"

    def test_interface_implementation(self):
        """Тест, что CognitiveJobSearch реализует IJobSearch."""
        assert isinstance(CognitiveJobSearch(), IJobSearch)


class TestJobSearchInterface:
    """Тесты для интерфейса IJobSearch."""

    def test_interface_is_abstract(self):
        """Тест, что IJobSearch — абстрактный класс."""
        with pytest.raises(TypeError):
            IJobSearch()  # type: ignore

    def test_search_signature(self):
        """Тест сигнатуры метода search."""
        import inspect
        sig = inspect.signature(IJobSearch.search)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "query" in params
