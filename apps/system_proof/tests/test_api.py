"""
Тесты для System Proof API
"""

import pytest
from fastapi.testclient import TestClient

from apps.system_proof.src.app import app, proofs_db

# Очистка базы перед тестами
@pytest.fixture(autouse=True)
def cleanup():
    proofs_db.clear()
    yield
    proofs_db.clear()

client = TestClient(app)


class TestHealthEndpoints:
    """Тесты health check endpoints"""
    
    def test_health_check(self):
        """Проверка health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "system-proof"
        assert "ai_config_available" in data
    
    def test_readiness_check(self):
        """Проверка readiness endpoint"""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
    
    def test_liveness_check(self):
        """Проверка liveness endpoint"""
        response = client.get("/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"


class TestProofCRUD:
    """Тесты CRUD операций с доказательствами"""
    
    def test_create_proof(self):
        """Создание доказательства"""
        proof_data = {
            "proof_id": "proof-001",
            "architecture": "microservices",
            "chain_id": "chain-001",
            "title": "Test Proof",
            "description": "Test description",
            "steps": []
        }
        
        response = client.post("/proofs", json=proof_data)
        assert response.status_code == 200
        data = response.json()
        assert data["proof_id"] == "proof-001"
        assert data["status"] == "draft"
        assert data["title"] == "Test Proof"
    
    def test_get_proof(self):
        """Получение доказательства"""
        # Создаем доказательство
        proof_data = {
            "proof_id": "proof-002",
            "architecture": "serverless",
            "chain_id": "chain-002",
            "title": "Get Test",
            "description": "Test for get"
        }
        client.post("/proofs", json=proof_data)
        
        # Получаем доказательство
        response = client.get("/proofs/proof-002")
        assert response.status_code == 200
        assert response.json()["proof_id"] == "proof-002"
    
    def test_get_proof_not_found(self):
        """Получение несуществующего доказательства"""
        response = client.get("/proofs/nonexistent")
        assert response.status_code == 404
    
    def test_update_proof(self):
        """Обновление доказательства"""
        proof_data = {
            "proof_id": "proof-003",
            "architecture": "monolith",
            "chain_id": "chain-003",
            "title": "Original",
            "description": "Original description"
        }
        client.post("/proofs", json=proof_data)
        
        # Обновляем
        update_data = {
            "proof_id": "proof-003",
            "architecture": "monolith",
            "chain_id": "chain-003",
            "title": "Updated",
            "description": "Updated description",
            "status": "in_progress"
        }
        response = client.put("/proofs/proof-003", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    def test_delete_proof(self):
        """Удаление доказательства"""
        proof_data = {
            "proof_id": "proof-004",
            "architecture": "microservices",
            "chain_id": "chain-004",
            "title": "Delete Test",
            "description": "To be deleted"
        }
        client.post("/proofs", json=proof_data)
        
        response = client.delete("/proofs/proof-004")
        assert response.status_code == 200
        
        # Проверяем удаление
        get_response = client.get("/proofs/proof-004")
        assert get_response.status_code == 404


class TestProofSteps:
    """Тесты работы со шагами доказательств"""
    
    def test_add_step(self):
        """Добавление шага к доказательству"""
        # Создаем доказательство
        proof_data = {
            "proof_id": "proof-005",
            "architecture": "event-driven",
            "chain_id": "chain-005",
            "title": "Steps Test",
            "description": "Test steps"
        }
        client.post("/proofs", json=proof_data)
        
        # Добавляем шаг
        step_data = {
            "step_id": "step-001",
            "description": "First step",
            "evidence": "Evidence for step 1"
        }
        response = client.post("/proofs/proof-005/steps", json=step_data)
        assert response.status_code == 200
        assert len(response.json()["steps"]) == 1
        assert response.json()["steps"][0]["step_id"] == "step-001"
    
    def test_add_step_to_nonexistent_proof(self):
        """Добавление шага к несуществующему доказательству"""
        step_data = {
            "step_id": "step-999",
            "description": "Test",
            "evidence": "Evidence"
        }
        response = client.post("/proofs/nonexistent/steps", json=step_data)
        assert response.status_code == 404


class TestProofVerification:
    """Тесты верификации доказательств"""
    
    def test_verify_proof(self):
        """Верификация доказательства"""
        # Создаем доказательство с шагами
        proof_data = {
            "proof_id": "proof-006",
            "architecture": "microservices",
            "chain_id": "chain-006",
            "title": "Verify Test",
            "description": "Test verification",
            "steps": [
                {
                    "step_id": "step-001",
                    "description": "Step 1",
                    "evidence": "Evidence 1",
                    "verified": False
                }
            ]
        }
        client.post("/proofs", json=proof_data)
        
        # Верифицируем
        response = client.post("/proofs/proof-006/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "verified"
        assert data["steps"][0]["verified"] is True
        assert data["steps"][0]["verified_at"] is not None


class TestProofList:
    """Тесты списка доказательств"""
    
    def test_list_empty(self):
        """Пустой список"""
        response = client.get("/proofs")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_multiple(self):
        """Список с несколькими доказательствами"""
        for i in range(3):
            proof_data = {
                "proof_id": f"proof-10{i}",
                "architecture": "microservices",
                "chain_id": f"chain-10{i}",
                "title": f"Proof {i}",
                "description": f"Description {i}"
            }
            client.post("/proofs", json=proof_data)
        
        response = client.get("/proofs")
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_list_filter_by_architecture(self):
        """Фильтрация по архитектуре"""
        # Создаем доказательства разных архитектур
        client.post("/proofs", json={
            "proof_id": "proof-201",
            "architecture": "microservices",
            "chain_id": "chain-201",
            "title": "Micro",
            "description": "Desc"
        })
        client.post("/proofs", json={
            "proof_id": "proof-202",
            "architecture": "serverless",
            "chain_id": "chain-202",
            "title": "Serverless",
            "description": "Desc"
        })
        
        response = client.get("/proofs?architecture=microservices")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["architecture"] == "microservices"
    
    def test_list_filter_by_status(self):
        """Фильтрация по статусу"""
        # Создаем доказательства с разными статусами
        for i, status in enumerate(["draft", "in_progress", "verified"]):
            proof_data = {
                "proof_id": f"proof-30{i}",
                "architecture": "microservices",
                "chain_id": f"chain-30{i}",
                "title": f"Proof {i}",
                "description": "Desc",
                "status": status
            }
            client.post("/proofs", json=proof_data)
        
        response = client.get("/proofs?status=verified")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["status"] == "verified"


class TestStatistics:
    """Тесты статистики"""
    
    def test_statistics_empty(self):
        """Пустая статистика"""
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["verified"] == 0
    
    def test_statistics_with_data(self):
        """Статистика с данными"""
        # Создаем доказательства разных статусов
        client.post("/proofs", json={
            "proof_id": "proof-401",
            "architecture": "microservices",
            "chain_id": "chain-401",
            "title": "Draft",
            "description": "Desc",
            "status": "draft"
        })
        client.post("/proofs", json={
            "proof_id": "proof-402",
            "architecture": "microservices",
            "chain_id": "chain-402",
            "title": "In Progress",
            "description": "Desc",
            "status": "in_progress"
        })
        client.post("/proofs", json={
            "proof_id": "proof-403",
            "architecture": "microservices",
            "chain_id": "chain-403",
            "title": "Verified",
            "description": "Desc",
            "status": "verified"
        })
        
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["draft"] == 1
        assert data["in_progress"] == 1
        assert data["verified"] == 1


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_duplicate_proof_id(self):
        """Дубликат proof_id"""
        proof_data = {
            "proof_id": "proof-500",
            "architecture": "microservices",
            "chain_id": "chain-500",
            "title": "First",
            "description": "Desc"
        }
        client.post("/proofs", json=proof_data)
        
        # Пытаемся создать с тем же ID
        response = client.post("/proofs", json=proof_data)
        assert response.status_code == 400
    
    def test_unicode_in_fields(self):
        """Unicode символы в полях"""
        proof_data = {
            "proof_id": "proof-501",
            "architecture": "微服务",
            "chain_id": "chain-501",
            "title": "Тест доказательства",
            "description": "Описание с эмодзи 🚀"
        }
        response = client.post("/proofs", json=proof_data)
        assert response.status_code == 200
        assert response.json()["architecture"] == "微服务"
        assert "🚀" in response.json()["description"]
