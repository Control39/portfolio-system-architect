import json
import os
import time
import yandexcloud
from yandex.cloud.ai.foundation_models.v1.text_common_pb2 import (
    TextGenerationRequest
)
from yandex.cloud.ai.foundation_models.v1.text_generation.text_generation_service_pb2_grpc import (
    TextGenerationServiceStub
)
from apps.cloud_reason.cloud_reason.utils.logger import PortfolioLogger

# Инициализация логгера
logger = PortfolioLogger()

def handler(event, context):
    """
    Обработчик запросов к Reasoning API
    Принимает { "message": "текст запроса" } и возвращает ответ модели
    """
    try:
        # Определение пути запроса
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        # Обработка health-check запроса
        if path == '/health' and method == 'GET':
            return health_check()
        
        # Обработка основного запроса к чату
        if path == '/chat' and method == 'POST':
            return chat_handler(event, context)
        
        # Если путь не распознан
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Endpoint not found'})
        }
        
    except Exception as e:
        error_msg = f"Ошибка при обработке запроса: {str(e)}"
        logger.log_error("api_error", error_msg, {"event": "exception", "exception": str(e)})
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': error_msg})
        }

def chat_handler(event, context):
    """
    Обработчик запросов к чату с AI
    """
    try:
        # Логирование входящего запроса
        logger.log_analysis("reasoning-api", 0, {"event": "request_received", "request": event})
        
        # Парсинг тела запроса
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        message = body.get('message')
        if not message:
            error_msg = "Поле 'message' обязательно"
            logger.log_error("validation_error", error_msg)
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': error_msg})
            }
        
        # Получение параметров из переменных окружения
        api_key = os.environ.get('API_KEY')
        folder_id = os.environ.get('FOLDER_ID')
        model_uri = os.environ.get('MODEL_URI', f"gpt://{folder_id}/yandexgpt/latest")
        
        if not api_key or not folder_id:
            error_msg = "Необходимо установить переменные окружения API_KEY и FOLDER_ID"
            logger.log_error("config_error", error_msg)
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': error_msg})
            }
        
        # Инициализация SDK Yandex Cloud
        sdk = yandexcloud.SDK(api_key=api_key)
        service = sdk.client(TextGenerationServiceStub)
        
        # Подготовка запроса к модели
        request = TextGenerationRequest(
            model_uri=model_uri,
            prompt=message,
            max_tokens=1000
        )
        
        # Вызов модели с обработкой таймаутов и повторами
        response = call_model_with_retry(service, request, max_retries=3, timeout=300)
        
        if response is None:
            error_msg = "Не удалось получить ответ от модели после нескольких попыток"
            logger.log_error("model_error", error_msg)
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': error_msg})
            }
        
        # Логирование успешного ответа
        logger.log_analysis("reasoning-api", 0, {"event": "response_sent", "response_length": len(response.text)})
        
        # Возврат результата
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': response.text
            })
        }
        
    except Exception as e:
        error_msg = f"Ошибка при обработке запроса чата: {str(e)}"
        logger.log_error("chat_api_error", error_msg, {"event": "exception", "exception": str(e)})
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': error_msg})
        }

def health_check():
    """
    Health check endpoint handler
    """
    try:
        # Здесь можно добавить проверки подключения к внешним сервисам
        # Например, проверку доступности Yandex Cloud API
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': time.time()
            })
        }
    except Exception as e:
        logger.log_error("health_check_error", f"Health check failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            })
        }

def call_model_with_retry(service, request, max_retries=3, timeout=300):
    """
    Вызов модели с повторными попытками и таймаутом
    """
    for attempt in range(max_retries):
        try:
            # Установка таймаута для вызова модели
            response = service.TextGeneration(request, timeout=timeout)
            return response
        except Exception as e:
            logger.log_error("model_call_error", f"Попытка {attempt + 1} не удалась: {str(e)}")
            if attempt < max_retries - 1:
                # Ждем перед повторной попыткой
                time.sleep(2 ** attempt)  # Экспоненциальная задержка
            else:
                # Все попытки исчерпаны
                logger.log_error("model_call_error", f"Все {max_retries} попытки вызова модели не удались")
                return None

