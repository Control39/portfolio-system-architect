"""
Интеграция с ML Model Registry для Portfolio Organizer.
Предоставляет эндпоинты для взаимодействия с реестром моделей.
"""

from flask import Blueprint, jsonify, request
import requests
import os

bp = Blueprint('ml_model_registry', __name__, url_prefix='/api/ml-model-registry')

# Конфигурация
ML_MODEL_REGISTRY_URL = os.environ.get(
    'ML_MODEL_REGISTRY_URL',
    'http://localhost:8000'
)

@bp.route('/models', methods=['GET'])
def list_models():
    """Получение списка моделей из ML Model Registry"""
    try:
        response = requests.get(f'{ML_MODEL_REGISTRY_URL}/portfolio/models', timeout=60)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch models from ML Model Registry: {str(e)}'
        }), 500

@bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """Получение информации о конкретной модели"""
    try:
        response = requests.get(f'{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}', timeout=60)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch model {model_id}: {str(e)}'
        }), 500

@bp.route('/models/<model_id>/predict', methods=['POST'])
def predict(model_id):
    """Выполнение предсказания с использованием модели"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        response = requests.post(
            f'{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}/predict',
            json=data,
            timeout=60
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния интеграции с ML Model Registry"""
    try:
        response = requests.get(f'{ML_MODEL_REGISTRY_URL}/health', timeout=10)
        if response.status_code == 200:
            return jsonify({
                'status': 'healthy',
                'ml_model_registry': 'connected',
                'url': ML_MODEL_REGISTRY_URL
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'ml_model_registry': 'unreachable',
                'url': ML_MODEL_REGISTRY_URL,
                'error': f'Registry returned {response.status_code}'
            }), 503
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'unhealthy',
            'ml_model_registry': 'connection_failed',
            'url': ML_MODEL_REGISTRY_URL,
            'error': str(e)
        }), 503

@bp.route('/portfolio-analysis', methods=['POST'])
def portfolio_analysis_with_models():
    """
    Анализ портфолио с использованием моделей машинного обучения.
    Принимает данные проектов, применяет модели для оценки рисков и рекомендаций.
    """
    try:
        data = request.get_json()
        if not data or 'projects' not in data:
            return jsonify({'error': 'Missing projects data'}), 400

        # Отправляем данные в ML Model Registry для анализа
        response = requests.post(
            f'{ML_MODEL_REGISTRY_URL}/portfolio/analyze',
            json=data,
            timeout=60
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Portfolio analysis failed: {str(e)}'
        }), 500