"""
E2E тест: Интеграция между сервисами

Сценарий:
1. Проверить health endpoints всех сервисов
2. Проверить интеграцию с ML Model Registry (опционально)
3. Проверить создание доказательств в system_proof
"""

import sys
from pathlib import Path

import pytest


# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Flask тестовый клиент для portfolio_organizer
# Примечание: используется FastAPI app из endpoints/routes.py
from apps.portfolio_organizer.endpoints.routes import app as portfolio_fastapi_app

from fastapi.testclient import TestClient

portfolio_client = TestClient(portfolio_fastapi_app)

# FastAPI тестовый клиент для system_proof
from fastapi.testclient import TestClient  # noqa: E402

from apps.system_proof.src.app import app as proof_app  # noqa: E402


proof_client = TestClient(proof_app)


class TestCrossServiceIntegrationE2E:
    """E2E тесты интеграции между сервисами"""

    def test_health_endpoints_all_services(self):
        """
        E2E: Проверка health endpoints всех сервисов

        Шаги:
        1. Проверяем health portfolio_organizer
        2. Проверяем health system_proof
        """
        # Portfolio Organizer (Flask)
        response = portfolio_client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"

        # System Proof (FastAPI)
        response = proof_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_ml_model_registry_integration(self):
        """
        E2E: Проверка интеграции с ML Model Registry через portfolio_organizer

        Примечание: Тест пропускается, если ML Model Registry не запущен.
        """
        # Health check ML Model Registry через portfolio_organizer
        response = portfolio_client.get("/api/ml-model-registry/health")

        # Если сервис недоступен (503), пропускаем тест
        if response.status_code == 503:
            pytest.skip("ML Model Registry не запущен")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"

        # List models (должен вернуть пустой список или список моделей)
        response = portfolio_client.get("/api/ml-model-registry/models")
        assert response.status_code == 200
        models = response.get_json()
        assert isinstance(models, list)

    def test_system_proof_workflow(self):
        """
        E2E: Полный workflow создания доказательств в system_proof

        Шаги:
        1. Создаём доказательство
        2. Добавляем шаг
        3. Верифицируем
        4. Проверяем статистику
        """
        # Создаём доказательство
        proof_data = {
            "proof_id": "e2e-proof-integration-001",
            "architecture": "microservices",
            "chain_id": "e2e-chain-integration-001",
            "title": "E2E Integration Proof",
            "description": "Доказательство для E2E тестирования",
            "steps": [],
        }

        response = proof_client.post("/proofs", json=proof_data)
        assert response.status_code == 200, f"Failed: {response.text}"
        proof = response.json()
        assert proof["proof_id"] == "e2e-proof-integration-001"

        # Добавляем шаг
        step_data = {
            "step_id": "step-e2e-001",
            "description": "Создано E2E доказательство",
            "evidence": "Test evidence",
        }

        response = proof_client.post("/proofs/e2e-proof-integration-001/steps", json=step_data)
        assert response.status_code == 200

        # Верифицируем
        response = proof_client.post("/proofs/e2e-proof-integration-001/verify", json={})
        assert response.status_code == 200
        verification = response.json()
        # Проверяем, что proof стал verified
        assert verification["status"] == "verified"
        assert len(verification["steps"]) == 1
        assert verification["steps"][0]["verified"] is True

        # Проверяем статистику
        response = proof_client.get("/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total"] >= 1

    def test_cross_service_data_flow(self):
        """
        E2E: Проверка потока данных между сервисами

        Шаги:
        1. Создаём доказательство в system_proof
        2. Проверяем, что данные доступны через API
        3. Проверяем health обоих сервисов
        """
        # Создаём доказательство
        proof_data = {
            "proof_id": "e2e-flow-001",
            "architecture": "kubernetes",
            "chain_id": "e2e-flow-chain-001",
            "title": "Cross-Service Flow Test",
            "description": "Тест потока данных",
            "steps": [],
        }

        response = proof_client.post("/proofs", json=proof_data)
        assert response.status_code == 200

        # Получаем доказательство
        response = proof_client.get("/proofs/e2e-flow-001")
        assert response.status_code == 200
        proof = response.json()
        assert proof["architecture"] == "kubernetes"

        # Проверяем, что portfolio_organizer тоже доступен
        response = portfolio_client.get("/health")
        assert response.status_code == 200
