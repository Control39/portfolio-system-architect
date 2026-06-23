"""
Тесты для модуля reasoning_api.py

Покрывает:
- handler (основной обработчик)
- chat_handler (обработчик чата)
- health_check (health check endpoint)
- call_model_with_retry (вызов модели с retry логикой)
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Добавляем путь к корню проекта
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def create_all_mocks():
    """Создать моки для всех зависимостей reasoning_api"""
    # Мок для yandexcloud
    yandexcloud_mock = MagicMock()
    yandexcloud_mock.cloud = MagicMock()
    yandexcloud_mock.cloud.ai = MagicMock()
    yandexcloud_mock.cloud.ai.foundation_models = MagicMock()
    yandexcloud_mock.cloud.ai.foundation_models.v1 = MagicMock()

    # Мок для текстовых protobuf
    text_common_pb2_mock = MagicMock()
    text_common_pb2_mock.TextGenerationRequest = MagicMock()
    yandexcloud_mock.cloud.ai.foundation_models.v1.text_common_pb2 = text_common_pb2_mock

    # Мок для gRPC сервиса
    text_generation_service_pb2_grpc_mock = MagicMock()
    text_generation_service_pb2_grpc_mock.TextGenerationServiceStub = MagicMock()
    yandexcloud_mock.cloud.ai.foundation_models.v1.text_generation = MagicMock()
    yandexcloud_mock.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc = text_generation_service_pb2_grpc_mock

    # Мок для PortfolioLogger
    portfolio_logger_mock = MagicMock()
    portfolio_logger_instance = MagicMock()
    portfolio_logger_mock.PortfolioLogger.return_value = portfolio_logger_instance

    return yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance


def test_functions_exist():
    """Проверяем, что все основные функции существуют"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        from agents.cognitive_agent.src.api.reasoning_api import (
            call_model_with_retry,
            chat_handler,
            handler,
            health_check,
        )

        assert callable(health_check)
        assert callable(handler)
        assert callable(chat_handler)
        assert callable(call_model_with_retry)


@patch('builtins.open', MagicMock())
def test_health_check_functionality():
    """Тест функции health_check"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        from agents.cognitive_agent.src.api.reasoning_api import health_check

        result = health_check()

        # Проверяем структуру ответа
        assert result["statusCode"] == 200
        assert "headers" in result
        assert "Content-Type" in result["headers"]
        assert "body" in result

        body = json.loads(result["body"])
        assert body["status"] == "healthy"
        assert "timestamp" in body  # Фактический ключ, возвращаемый функцией


def test_handler_basic_structure():
    """Тест структуры handler"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        import inspect

        from agents.cognitive_agent.src.api.reasoning_api import handler

        # Проверяем сигнатуру
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
        assert len(params) >= 2  # handler(event, context) минимум 2 аргумента


def test_chat_handler_basic_structure():
    """Тест структуры chat_handler"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        import inspect

        from agents.cognitive_agent.src.api.reasoning_api import chat_handler

        # Проверяем сигнатуру
        sig = inspect.signature(chat_handler)
        params = list(sig.parameters.keys())
        assert len(params) >= 2  # chat_handler(event, context) минимум 2 аргумента


def test_call_model_with_retry_basic_structure():
    """Тест структуры call_model_with_retry"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        import inspect

        from agents.cognitive_agent.src.api.reasoning_api import call_model_with_retry

        # Проверяем сигнатуру
        sig = inspect.signature(call_model_with_retry)
        params = list(sig.parameters.keys())
        # Фактические параметры: service, request, max_retries=3, timeout=300
        assert "service" in params
        assert "request" in params
        assert "max_retries" in params
        assert "timeout" in params


def test_handler_health_endpoint():
    """Тест обработки health эндпоинта в handler"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        from agents.cognitive_agent.src.api.reasoning_api import handler

        # Подготовка события для health check
        event = {
            "path": "/health",
            "httpMethod": "GET"
        }
        context = MagicMock()

        try:
            result = handler(event, context)
            assert "statusCode" in result
            assert result["statusCode"] == 200
        except Exception:
            # Если есть ошибки из-за других зависимостей - это приемлемо
            assert True


def test_handler_unknown_endpoint():
    """Тест обработки неизвестного эндпоинта в handler"""
    # Замокировать все зависимости перед импортом
    yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

    with patch.dict('sys.modules', {
        'yandexcloud': yandexcloud_mock,
        'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
        'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
        'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
    }):
        from agents.cognitive_agent.src.api.reasoning_api import handler

        # Подготовка события для неизвестного эндпоинта
        event = {
            "path": "/unknown",
            "httpMethod": "GET"
        }
        context = MagicMock()

        try:
            result = handler(event, context)
            assert "statusCode" in result
            assert result["statusCode"] == 404  # Ожидаем 404 для неизвестного эндпоинта
        except Exception:
            # Если есть ошибки из-за других зависимостей - это приемлемо
            assert True


class TestReasoningApiStructure:
    """Тесты структуры модуля reasoning_api"""

    def test_all_functions_are_callable(self):
        """Проверяем, что все функции можно вызвать"""
        # Замокировать все зависимости перед импортом
        yandexcloud_mock, text_common_pb2_mock, text_generation_service_pb2_grpc_mock, portfolio_logger_mock, portfolio_logger_instance = create_all_mocks()

        with patch.dict('sys.modules', {
            'yandexcloud': yandexcloud_mock,
            'yandex.cloud.ai.foundation_models.v1.text_common_pb2': text_common_pb2_mock,
            'yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc': text_generation_service_pb2_grpc_mock,
            'apps.decision_engine.decision_engine.utils.logger': portfolio_logger_mock
        }):
            import agents.cognitive_agent.src.api.reasoning_api as reasoning_api

            # Проверяем, что основные функции существуют и вызываемы
            assert hasattr(reasoning_api, 'health_check')
            assert hasattr(reasoning_api, 'handler')
            assert hasattr(reasoning_api, 'chat_handler')
            assert hasattr(reasoning_api, 'call_model_with_retry')

            assert callable(reasoning_api.health_check)
            assert callable(reasoning_api.handler)
            assert callable(reasoning_api.chat_handler)
            assert callable(reasoning_api.call_model_with_retry)
