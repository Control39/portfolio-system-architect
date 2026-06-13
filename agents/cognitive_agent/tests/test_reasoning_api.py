"""
Тесты для модуля reasoning_api.py

Покрывает:
- handler (основной обработчик)
- chat_handler (обработчик чата)
- health_check (health check endpoint)
- call_model_with_retry (вызов модели с retry логикой)
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Мок для yandexcloud
yandexcloud_mock = MagicMock()


@pytest.fixture(autouse=True)
def setup_mocks():
    """Настройка моков перед каждым тестом"""
    # Создаем моки для всех зависимостей
    mock_logger = MagicMock()
    mock_time = MagicMock()
    mock_time.sleep = MagicMock()

    # Создаем моки для yandexcloud
    mock_sdk = MagicMock()
    mock_client = MagicMock()
    mock_service = MagicMock()

    yandexcloud_mock.SDK.return_value = mock_sdk
    mock_sdk.client.return_value = mock_client
    mock_client.TextGeneration.return_value = mock_service

    # Модуль yandex.cloud.ai.foundation_models.v1.text_common_pb2
    mock_text_common_pb2 = MagicMock()
    mock_text_generation_request = MagicMock()
    mock_text_common_pb2.TextGenerationRequest = MagicMock(return_value=mock_text_generation_request)

    # Модуль yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc
    mock_grpc = MagicMock()
    mock_text_generation_service_stub = MagicMock()
    mock_grpc.TextGenerationServiceStub = mock_text_generation_service_stub

    # Патчим все зависимости
    with patch.dict(os.environ, {"API_KEY": "test_key", "FOLDER_ID": "test_folder"}, clear=True):
        with patch("agents.cognitive_agent.src.api.reasoning_api.logger", mock_logger):
            with patch("agents.cognitive_agent.src.api.reasoning_api.time", mock_time):
                with patch("agents.cognitive_agent.src.api.reasoning_api.yandexcloud", yandexcloud_mock):
                    with patch(
                        "agents.cognitive_agent.src.api.reasoning_api.TextGenerationRequest",
                        mock_text_common_pb2.TextGenerationRequest,
                    ):
                        with patch(
                            "agents.cognitive_agent.src.api.reasoning_api.TextGenerationServiceStub",
                            mock_grpc.TextGenerationServiceStub,
                        ):
                            # Импорт после мокирования
                            from agents.cognitive_agent.src.api import reasoning_api

                            # Делаем моки доступными для тестов через атрибуты модуля
                            reasoning_api.mock_logger = mock_logger
                            reasoning_api.mock_time = mock_time
                            reasoning_api.mock_sdk = mock_sdk
                            reasoning_api.mock_client = mock_client
                            reasoning_api.mock_service = mock_service
                            reasoning_api.mock_text_generation_request = mock_text_generation_request
                            reasoning_api.yandexcloud_mock = yandexcloud_mock
                            yield reasoning_api


class TestHealthCheck:
    """Тесты для health_check функции"""

    def test_health_check_success(self, setup_mocks):
        """Тест успешного health check"""
        result = setup_mocks.health_check()

        assert result["statusCode"] == 200
        assert result["headers"]["Content-Type"] == "application/json"
        body = json.loads(result["body"])
        assert body["status"] == "healthy"
        assert "timestamp" in body

    def test_health_check_exception_handling(self, setup_mocks):
        """Тест обработки исключения в health check"""
        setup_mocks.mock_logger.log_error = MagicMock()

        with patch(
            "agents.cognitive_agent.src.api.reasoning_api.time",
            MagicMock(side_effect=Exception("test error")),
        ):
            result = setup_mocks.health_check()

            assert result["statusCode"] == 500
            body = json.loads(result["body"])
            assert body["status"] == "unhealthy"
            assert "error" in body


class TestCallModelWithRetry:
    """Тесты для call_model_with_retry функции"""

    def test_call_model_success_first_attempt(self, setup_mocks):
        """Тест успешного вызова модели с первой попытки"""
        mock_service = setup_mocks.mock_service
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_service.TextGeneration.return_value = mock_response

        setup_mocks.mock_logger.log_error = MagicMock()

        result = setup_mocks.call_model_with_retry(mock_service, mock_request, max_retries=3, timeout=300)

        assert result == mock_response
        assert result.text == "Test response"
        mock_service.TextGeneration.assert_called_once_with(mock_request, timeout=300)
        setup_mocks.mock_logger.log_error.assert_not_called()

    def test_call_model_success_after_retry(self, setup_mocks):
        """Тест успешного вызова модели после повторной попытки"""
        mock_service = setup_mocks.mock_service
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"

        # Сначала исключение, потом успех
        mock_service.TextGeneration.side_effect = [Exception("First attempt failed"), mock_response]

        setup_mocks.mock_logger.log_error = MagicMock()

        result = setup_mocks.call_model_with_retry(mock_service, mock_request, max_retries=3, timeout=300)

        assert result == mock_response
        assert result.text == "Test response"
        assert mock_service.TextGeneration.call_count == 2
        assert setup_mocks.mock_logger.log_error.call_count == 1

    def test_call_model_all_retries_failed(self, setup_mocks):
        """Тест неудачи всех попыток вызова модели"""
        mock_service = setup_mocks.mock_service
        mock_request = MagicMock()

        # Всегда исключение
        mock_service.TextGeneration.side_effect = Exception("Always fails")

        setup_mocks.mock_logger.log_error = MagicMock()

        result = setup_mocks.call_model_with_retry(mock_service, mock_request, max_retries=3, timeout=300)

        assert result is None
        assert mock_service.TextGeneration.call_count == 3
        assert setup_mocks.mock_logger.log_error.call_count == 3

    def test_call_model_exponential_backoff(self, setup_mocks):
        """Тест экспоненциальной задержки между попытками"""
        mock_service = setup_mocks.mock_service
        mock_request = MagicMock()

        # Всегда исключение
        mock_service.TextGeneration.side_effect = Exception("Always fails")

        mock_time = MagicMock()
        setup_mocks.mock_logger.log_error = MagicMock()

        with patch("agents.cognitive_agent.src.api.reasoning_api.time", mock_time):
            result = setup_mocks.call_model_with_retry(mock_service, mock_request, max_retries=3, timeout=300)

        assert result is None
        # Проверяем, что sleep вызывался с правильными интервалами
        assert mock_time.sleep.call_count == 2
        mock_time.sleep.assert_any_call(1)  # 2^0 = 1
        mock_time.sleep.assert_any_call(2)  # 2^1 = 2


class TestChatHandler:
    """Тесты для chat_handler функции"""

    def test_chat_handler_success(self, setup_mocks):
        """Тест успешного обработки чат-запроса"""
        setup_mocks.mock_logger.log_analysis = MagicMock()
        setup_mocks.mock_logger.log_error = MagicMock()

        # Настройка моков
        mock_service = setup_mocks.mock_service
        mock_response = MagicMock()
        mock_response.text = "AI response"
        mock_service.TextGeneration.return_value = mock_response

        event = {"body": json.dumps({"message": "Hello AI"}), "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["message"] == "AI response"
        assert setup_mocks.mock_logger.log_analysis.called

    def test_chat_handler_missing_message(self, setup_mocks):
        """Тест обработки отсутствующего сообщения"""
        setup_mocks.mock_logger.log_error = MagicMock()

        event = {"body": json.dumps({}), "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body
        assert setup_mocks.mock_logger.log_error.called

    def test_chat_handler_missing_api_key(self, setup_mocks):
        """Тест обработки отсутствующего API ключа"""
        setup_mocks.mock_logger.log_error = MagicMock()

        # Только FOLDER_ID, нет API_KEY
        with patch.dict(os.environ, {"FOLDER_ID": "test_folder"}, clear=True):
            event = {
                "body": json.dumps({"message": "Hello"}),
                "path": "/chat",
                "httpMethod": "POST",
            }
            context = {}

            result = setup_mocks.chat_handler(event, context)

            assert result["statusCode"] == 500
            body = json.loads(result["body"])
            assert "error" in body
            assert setup_mocks.mock_logger.log_error.called

    def test_chat_handler_model_error(self, setup_mocks):
        """Тест обработки ошибки модели"""
        setup_mocks.mock_logger.log_error = MagicMock()

        # Настройка моков
        mock_service = setup_mocks.mock_service
        mock_service.TextGeneration.side_effect = Exception("Model error")

        event = {"body": json.dumps({"message": "Hello AI"}), "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body

    def test_chat_handler_invalid_body(self, setup_mocks):
        """Тест обработки невалидного тела запроса"""
        setup_mocks.mock_logger.log_error = MagicMock()

        event = {"body": "invalid json", "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body

    def test_chat_handler_exception_handling(self, setup_mocks):
        """Тест обработки исключения в chat_handler"""
        setup_mocks.mock_logger.log_error = MagicMock()

        # Исключение при обработке
        with patch(
            "agents.cognitive_agent.src.api.reasoning_api.json.loads",
            side_effect=Exception("Test error"),
        ):
            event = {
                "body": json.dumps({"message": "Hello"}),
                "path": "/chat",
                "httpMethod": "POST",
            }
            context = {}

            result = setup_mocks.chat_handler(event, context)

            assert result["statusCode"] == 500
            body = json.loads(result["body"])
            assert "error" in body


class TestHandler:
    """Тесты для основного handler функции"""

    def test_handler_health_endpoint(self, setup_mocks):
        """Тест обработки health endpoint"""
        setup_mocks.health_check = MagicMock(return_value={"statusCode": 200})

        event = {"path": "/health", "httpMethod": "GET"}
        context = {}

        result = setup_mocks.handler(event, context)

        assert result["statusCode"] == 200
        setup_mocks.health_check.assert_called_once()

    def test_handler_chat_endpoint(self, setup_mocks):
        """Тест обработки chat endpoint"""
        setup_mocks.chat_handler = MagicMock(return_value={"statusCode": 200})

        event = {"path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.handler(event, context)

        assert result["statusCode"] == 200
        setup_mocks.chat_handler.assert_called_once_with(event, context)

    def test_handler_unknown_endpoint(self, setup_mocks):
        """Тест обработки неизвестного endpoint"""
        event = {"path": "/unknown", "httpMethod": "GET"}
        context = {}

        result = setup_mocks.handler(event, context)

        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert body["error"] == "Endpoint not found"

    def test_handler_exception_handling(self, setup_mocks):
        """Тест обработки исключения в handler"""
        setup_mocks.mock_logger.log_error = MagicMock()

        # Исключение при обработке
        with patch(
            "agents.cognitive_agent.src.api.reasoning_api.json.loads",
            side_effect=Exception("Test error"),
        ):
            event = {"path": "/health", "httpMethod": "GET"}
            context = {}

            result = setup_mocks.handler(event, context)

            assert result["statusCode"] == 500
            body = json.loads(result["body"])
            assert "error" in body


class TestEdgeCases:
    """Тесты для edge cases"""

    def test_empty_message(self, setup_mocks):
        """Тест с пустым со��бщением"""
        setup_mocks.mock_logger.log_error = MagicMock()

        event = {"body": json.dumps({"message": ""}), "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 400

    def test_none_body(self, setup_mocks):
        """Тест с None body"""
        setup_mocks.mock_logger.log_error = MagicMock()

        event = {"body": None, "path": "/chat", "httpMethod": "POST"}
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 400

    def test_large_message(self, setup_mocks):
        """Тест с большим сообщением"""
        setup_mocks.mock_logger.log_analysis = MagicMock()

        mock_service = setup_mocks.mock_service
        mock_response = MagicMock()
        mock_response.text = "AI response"
        mock_service.TextGeneration.return_value = mock_response

        large_message = "A" * 10000  # 10KB сообщение
        event = {
            "body": json.dumps({"message": large_message}),
            "path": "/chat",
            "httpMethod": "POST",
        }
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 200

    def test_special_characters_in_message(self, setup_mocks):
        """Тест с специальными символами в сообщении"""
        setup_mocks.mock_logger.log_analysis = MagicMock()

        mock_service = setup_mocks.mock_service
        mock_response = MagicMock()
        mock_response.text = "AI response"
        mock_service.TextGeneration.return_value = mock_response

        special_message = "Привет! <script>alert('xss')</script> 🚀"
        event = {
            "body": json.dumps({"message": special_message}),
            "path": "/chat",
            "httpMethod": "POST",
        }
        context = {}

        result = setup_mocks.chat_handler(event, context)

        assert result["statusCode"] == 200
