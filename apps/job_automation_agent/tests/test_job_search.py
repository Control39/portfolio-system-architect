"""Tests for job_search module."""

from pathlib import Path
from unittest.mock import patch

import pytest

# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent.parent

from job_automation_agent.src.job_search import (  # noqa: E402
    search_all_jobs,
    search_habr_career,
    search_hh_ru,
)


class TestJobSearch:
    """Tests for job search functionality."""

    @pytest.mark.asyncio
    async def test_search_hh_ru_success(self):
        """Test successful hh.ru search."""
        mock_response = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "employer": {"name": "Test Corp"},
                    "salary": {"from": 150000},
                    "alternate_url": "https://hh.ru/vacancy/123",
                }
            ]
        }

        with patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            results = await search_hh_ru("Python", "1")

            assert len(results) == 1
            assert results[0]["name"] == "Python Developer"
            assert results[0]["employer"] == "Test Corp"
            assert results[0]["url"] == "https://hh.ru/vacancy/123"

    @pytest.mark.asyncio
    async def test_search_hh_ru_empty_response(self):
        """Test hh.ru search with empty response."""
        mock_response = {"items": []}

        with patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            results = await search_hh_ru("NonExistent", "1")

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_hh_ru_request_error(self):
        """Test hh.ru search with request error."""
        from requests import RequestException

        with patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get:
            mock_get.side_effect = RequestException("Connection error")

            results = await search_hh_ru("Python", "1")

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_habr_career(self):
        """Test Habr Career search."""
        results = await search_habr_career("Python")

        assert len(results) == 1
        assert results[0]["name"] == "Python разработчик"
        assert results[0]["employer"] == "Компания Х"
        assert "career.habr.com" in results[0]["url"]

    @pytest.mark.asyncio
    async def test_search_all_jobs_combined(self):
        """Test combined search from all sources."""
        mock_hh_response = {
            "items": [
                {
                    "id": "1",
                    "name": "Backend Developer",
                    "employer": {"name": "HH Corp"},
                    "salary": None,
                    "alternate_url": "https://hh.ru/vacancy/1",
                }
            ]
        }

        with patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_hh_response
            mock_get.return_value.raise_for_status.return_value = None

            results = await search_all_jobs("Python")

            # hh.ru (1) + Habr Career (1) = 2 results
            assert len(results) == 2
            assert any(r["name"] == "Backend Developer" for r in results)
            assert any(r["name"] == "Python разработчик" for r in results)

    @pytest.mark.asyncio
    async def test_search_hh_ru_default_area(self):
        """Test hh.ru search with default area parameter."""
        mock_response = {"items": []}

        with patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            await search_hh_ru("Python")

            # Verify default area="1" was used
            call_args = mock_get.call_args
            assert "area=1" in call_args[0][0] or "area=1" in call_args[1].get("url", "")


class TestSecurityValidation:
    """Tests for security validation in job search."""

    @pytest.mark.asyncio
    async def test_url_validation_in_search(self):
        """Test that URL validation is called during search."""
        mock_response = {"items": []}

        with (
            patch("apps.job_automation_agent.src.job_search.is_safe_url") as mock_safe,
            patch("apps.job_automation_agent.src.job_search.requests.get") as mock_get,
        ):
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            await search_hh_ru("Python", "1")

            # is_safe_url should be called for URL validation
            mock_safe.assert_called_once()
