"""
Интеграция с ML Model Registry для Portfolio Organizer.
Предоставляет эндпоинты для взаимодействия с реестром моделей.
"""

import os
import re

import requests
from flask import Blueprint, jsonify, request

from ...utils.security import is_safe_url, sanitize_error_message


bp = Blueprint("ml_model_registry", __name__, url_prefix="/api/ml-model-registry")

# Конфигурация
ML_MODEL_REGISTRY_URL = os.environ.get("ML_MODEL_REGISTRY_URL", "http://localhost:8000")

ALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "ml-registry.internal",
    "api.trusted-domain.com",
}

# Регулярное выражение для валидации model_id
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _make_request(method: str, url: str, **kwargs) -> requests.Response:
    """Выполняет HTTP-запрос с SSRF-защитой."""
    # SSRF защита: валидация URL через is_safe_url
    try:
        is_safe_url(url, ALLOWED_HOSTS)
    except ValueError as e:
        raise ValueError(f"Небезопасный URL: {e}") from e

    # URL валидирован и безопасен — выполняем запрос
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response


@bp.route("/models", methods=["GET"])
def list_models():
    """Получение списка моделей из ML Model Registry"""
    try:
        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models"
        response = _make_request("GET", url, timeout=30)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        safe_msg = sanitize_error_message(e, ML_MODEL_REGISTRY_URL)
        return jsonify({"error": "Failed to fetch models from ML Model Registry", "details": safe_msg}), 500


@bp.route("/models/<model_id>", methods=["GET"])
def get_model(model_id):
    """Получение информации о конкретной модели"""
    try:
        if not MODEL_ID_PATTERN.fullmatch(model_id):
            return jsonify({"error": "Invalid model_id format"}), 400

        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}"
        response = _make_request("GET", url, timeout=30)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        safe_msg = sanitize_error_message(e, ML_MODEL_REGISTRY_URL)
        return jsonify({"error": "Failed to fetch model information", "details": safe_msg}), 500


@bp.route("/models/<model_id>/predict", methods=["POST"])
def predict(model_id):
    """Выполнение предсказания с использованием модели"""
    try:
        if not MODEL_ID_PATTERN.fullmatch(model_id):
            return jsonify({"error": "Invalid model_id format"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}/predict"
        response = _make_request("POST", url, json=data, timeout=30)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        safe_msg = sanitize_error_message(e, ML_MODEL_REGISTRY_URL)
        return jsonify({"error": "Prediction failed", "details": safe_msg}), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Проверка состояния интеграции с ML Model Registry"""
    try:
        url = f"{ML_MODEL_REGISTRY_URL}/health"
        response = _make_request("GET", url, timeout=30)
        if response.status_code == 200:
            return jsonify(
                {
                    "status": "healthy",
                    "ml_model_registry": "connected",
                    "url": ML_MODEL_REGISTRY_URL,
                }
            )
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "ml_model_registry": "unreachable",
                    "url": ML_MODEL_REGISTRY_URL,
                }
            ),
            503,
        )
    except requests.exceptions.RequestException as e:
        safe_msg = sanitize_error_message(e, ML_MODEL_REGISTRY_URL)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "ml_model_registry": "connection_failed",
                    "url": ML_MODEL_REGISTRY_URL,
                    "details": safe_msg,
                }
            ),
            503,
        )


@bp.route("/portfolio-analysis", methods=["POST"])
def portfolio_analysis_with_models():
    """
    Анализ портфолио с использованием моделей машинного обучения.
    Принимает данные проектов, применяет модели для оценки рисков и рекомендаций.
    """
    try:
        data = request.get_json()
        if not data or "projects" not in data:
            return jsonify({"error": "Missing projects data"}), 400

        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/analyze"
        response = _make_request("POST", url, json=data, timeout=30)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        safe_msg = sanitize_error_message(e, ML_MODEL_REGISTRY_URL)
        return jsonify({"error": "Portfolio analysis failed", "details": safe_msg}), 500
