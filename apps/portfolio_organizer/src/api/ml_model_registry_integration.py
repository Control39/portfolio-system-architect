"""
Интеграция с ML Model Registry для Portfolio Organizer.
Предоставляет эндпоинты для взаимодействия с реестром моделей.
"""

import os

import requests
from flask import Blueprint, jsonify, request


bp = Blueprint("ml_model_registry", __name__, url_prefix="/api/ml-model-registry")

# Конфигурация
ML_MODEL_REGISTRY_URL = os.environ.get("ML_MODEL_REGISTRY_URL", "http://localhost:8000")


@bp.route("/models", methods=["GET"])
def list_models():
    """Получение списка моделей из ML Model Registry"""
    try:
        import urllib.parse

        ALLOWED_HOSTS = {"api.trusted-domain.com", "ml-registry.internal", "localhost", "127.0.0.1"}
        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models"
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"SSRF protection: host '{parsed.hostname}' not allowed")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to fetch models from ML Model Registry"}), 500


@bp.route("/models/<model_id>", methods=["GET"])
def get_model(model_id):
    """Получение информации о конкретной модели"""
    try:
        import urllib.parse

        ALLOWED_HOSTS = {"api.trusted-domain.com", "ml-registry.internal", "localhost", "127.0.0.1"}
        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}"
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"SSRF protection: host '{parsed.hostname}' not allowed")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Failed to fetch model information"}), 500


@bp.route("/models/<model_id>/predict", methods=["POST"])
def predict(model_id):
    """Выполнение предсказания с использованием модели"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        import urllib.parse

        ALLOWED_HOSTS = {"api.trusted-domain.com", "ml-registry.internal", "localhost", "127.0.0.1"}
        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/models/{model_id}/predict"
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"SSRF protection: host '{parsed.hostname}' not allowed")
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Prediction failed"}), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Проверка состояния интеграции с ML Model Registry"""
    try:
        import urllib.parse

        ALLOWED_HOSTS = {"api.trusted-domain.com", "ml-registry.internal", "localhost", "127.0.0.1"}
        url = f"{ML_MODEL_REGISTRY_URL}/health"
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"SSRF protection: host '{parsed.hostname}' not allowed")
        response = requests.get(url, timeout=30)
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
    except requests.exceptions.RequestException:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "ml_model_registry": "connection_failed",
                    "url": ML_MODEL_REGISTRY_URL,
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

        import urllib.parse

        ALLOWED_HOSTS = {"api.trusted-domain.com", "ml-registry.internal", "localhost", "127.0.0.1"}
        url = f"{ML_MODEL_REGISTRY_URL}/portfolio/analyze"
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"SSRF protection: host '{parsed.hostname}' not allowed")
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Portfolio analysis failed"}), 500
