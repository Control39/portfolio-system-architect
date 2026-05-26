"""
Тесты для Thought Architecture API
"""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импортируем напрямую
from src.api.app import (
    app, decisions_db, records_db
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Очистка базы перед каждым тестом"""
    decisions_db.clear()
    records_db.clear()
    yield
    decisions_db.clear()
    records_db.clear()


class TestHealthEndpoints:
    """Тесты health check"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "thought-architecture"
    
    def test_readiness(self):
        response = client.get("/ready")
        assert response.status_code == 200
    
    def test_liveness(self):
        response = client.get("/live")
        assert response.status_code == 200


class TestDecisionCRUD:
    """Тесты CRUD для решений"""
    
    def test_create_decision(self):
        decision_data = {
            "decision_id": "dec-001",
            "title": "Выбор базы данных",
            "description": "Выбираем PostgreSQL для хранения данных",
            "status": "proposed",
            "level": "high",
            "tags": ["database", "infrastructure"]
        }
        response = client.post("/decisions", json=decision_data)
        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == "dec-001"
        assert data["level"] == "high"
    
    def test_get_decision(self):
        # Создаем
        client.post("/decisions", json={
            "decision_id": "dec-002",
            "title": "Test",
            "description": "Desc"
        })
        # Получаем
        response = client.get("/decisions/dec-002")
        assert response.status_code == 200
        assert response.json()["title"] == "Test"
    
    def test_get_decision_not_found(self):
        response = client.get("/decisions/nonexistent")
        assert response.status_code == 404
    
    def test_update_decision(self):
        # Создаем
        client.post("/decisions", json={
            "decision_id": "dec-003",
            "title": "Original",
            "description": "Desc"
        })
        # Обновляем
        update_data = {
            "decision_id": "dec-003",
            "title": "Updated",
            "description": "Desc",
            "status": "proposed",
            "level": "medium"
        }
        response = client.put("/decisions/dec-003", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    def test_delete_decision(self):
        client.post("/decisions", json={
            "decision_id": "dec-004",
            "title": "ToDelete",
            "description": "Desc"
        })
        response = client.delete("/decisions/dec-004")
        assert response.status_code == 200
        get_response = client.get("/decisions/dec-004")
        assert get_response.status_code == 404


class TestDecisionLifecycle:
    """Тесты жизненного цикла решений"""
    
    def test_approve_decision(self):
        # Создаем proposed решение
        client.post("/decisions", json={
            "decision_id": "dec-101",
            "title": "Approve Test",
            "description": "Desc",
            "status": "proposed"
        })
        
        # Одобр
        response = client.put("/decisions/dec-101/approve?approver=architect")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["approved_by"] == "architect"
        assert data["approved_at"] is not None
    
    def test_approve_non_proposed(self):
        # Создаем accepted решение
        client.post("/decisions", json={
            "decision_id": "dec-102",
            "title": "Test",
            "description": "Desc",
            "status": "accepted"
        })
        
        response = client.put("/decisions/dec-102/approve?approver=architect")
        assert response.status_code == 400
    
    def test_reject_decision(self):
        client.post("/decisions", json={
            "decision_id": "dec-103",
            "title": "Reject Test",
            "description": "Desc",
            "status": "proposed"
        })
        
        response = client.put("/decisions/dec-103/reject?reason=Too expensive")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert "Too expensive" in data["consequences"]
    
    def test_supersede_decision(self):
        # Создаем два решения
        client.post("/decisions", json={
            "decision_id": "dec-201",
            "title": "Old",
            "description": "Old approach",
            "status": "accepted"
        })
        client.post("/decisions", json={
            "decision_id": "dec-202",
            "title": "New",
            "description": "New approach",
            "status": "proposed"
        })
        
        # Заменяем
        response = client.put("/decisions/dec-201/supersede?new_decision_id=dec-202")
        assert response.status_code == 200
        data = response.json()
        assert data["superseded"]["status"] == "superseded"
        assert data["replaced_by"]["decision_id"] == "dec-202"


class TestDecisionList:
    """Тесты списка решений"""
    
    def test_list_empty(self):
        response = client.get("/decisions")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_with_filter_by_status(self):
        # Создаем решения разных статусов
        for status in ["proposed", "accepted", "rejected"]:
            client.post("/decisions", json={
                "decision_id": f"dec-30{status[0]}",
                "title": "Test",
                "description": "Desc",
                "status": status
            })
        
        response = client.get("/decisions?status=accepted")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["status"] == "accepted"
    
    def test_list_with_filter_by_level(self):
        client.post("/decisions", json={
            "decision_id": "dec-401",
            "title": "Test",
            "description": "Desc",
            "level": "critical"
        })
        client.post("/decisions", json={
            "decision_id": "dec-402",
            "title": "Test",
            "description": "Desc",
            "level": "low"
        })
        
        response = client.get("/decisions?level=critical")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_list_with_filter_by_tag(self):
        client.post("/decisions", json={
            "decision_id": "dec-501",
            "title": "Test",
            "description": "Desc",
            "tags": ["database", "infrastructure"]
        })
        client.post("/decisions", json={
            "decision_id": "dec-502",
            "title": "Test",
            "description": "Desc",
            "tags": ["frontend", "ui"]
        })
        
        response = client.get("/decisions?tag=database")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert "database" in response.json()[0]["tags"]


class TestSearch:
    """Тесты поиска решений"""
    
    def test_search_by_title(self):
        client.post("/decisions", json={
            "decision_id": "dec-601",
            "title": "Выбор PostgreSQL",
            "description": "Desc"
        })
        client.post("/decisions", json={
            "decision_id": "dec-602",
            "title": "Выбор React",
            "description": "Desc"
        })
        
        response = client.get("/decisions/search?query=PostgreSQL")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert "PostgreSQL" in response.json()[0]["title"]
    
    def test_search_by_tag(self):
        client.post("/decisions", json={
            "decision_id": "dec-603",
            "title": "Test",
            "description": "Desc",
            "tags": ["database", "postgresql"]
        })
        
        response = client.get("/decisions/search?query=database")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_search_not_found(self):
        client.post("/decisions", json={
            "decision_id": "dec-604",
            "title": "Test",
            "description": "Desc"
        })
        
        response = client.get("/decisions/search?query=nonexistent")
        assert response.status_code == 200
        assert response.json() == []


class TestStatistics:
    """Тесты статистики"""
    
    def test_statistics_empty(self):
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_statistics_with_data(self):
        # Создаем решения разных статусов и уровней
        client.post("/decisions", json={
            "decision_id": "dec-701",
            "title": "Test",
            "description": "Desc",
            "status": "accepted",
            "level": "critical",
            "tags": ["database"]
        })
        client.post("/decisions", json={
            "decision_id": "dec-702",
            "title": "Test",
            "description": "Desc",
            "status": "proposed",
            "level": "high",
            "tags": ["database", "frontend"]
        })
        client.post("/decisions", json={
            "decision_id": "dec-703",
            "title": "Test",
            "description": "Desc",
            "status": "accepted",
            "level": "medium",
            "tags": ["frontend"]
        })
        
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["by_status"]["accepted"] == 2
        assert data["by_status"]["proposed"] == 1
        assert data["by_level"]["critical"] == 1
        assert data["by_level"]["high"] == 1
        assert data["by_tag"]["database"] == 2
        assert data["by_tag"]["frontend"] == 2


class TestArchitectureRecord:
    """Тесты записей архитектуры"""
    
    def test_create_record(self):
        record_data = {
            "record_id": "record-001",
            "title": "Microservices Architecture",
            "description": "Архитектура микросервисов",
            "decisions": []
        }
        response = client.post("/records", json=record_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Microservices Architecture"
    
    def test_add_decision_to_record(self):
        # Создаем решение и запись
        client.post("/decisions", json={
            "decision_id": "dec-801",
            "title": "Test",
            "description": "Desc"
        })
        client.post("/records", json={
            "record_id": "record-801",
            "title": "Test Record",
            "description": "Desc",
            "decisions": []
        })
        
        # Добавляем решение
        response = client.put("/records/record-801/add_decision?decision_id=dec-801")
        assert response.status_code == 200
        assert len(response.json()["decisions"]) == 1
    
    def test_add_decision_not_found(self):
        client.post("/records", json={
            "record_id": "record-802",
            "title": "Test",
            "description": "Desc",
            "decisions": []
        })
        
        response = client.put("/records/record-802/add_decision?decision_id=nonexistent")
        assert response.status_code == 404
    
    def test_delete_record(self):
        client.post("/records", json={
            "record_id": "record-803",
            "title": "ToDelete",
            "description": "Desc",
            "decisions": []
        })
        
        response = client.delete("/records/record-803")
        assert response.status_code == 200
        # Проверяем что запись удалена
        get_response = client.get("/records/record-803")
        assert get_response.status_code == 404


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_duplicate_decision_id(self):
        client.post("/decisions", json={
            "decision_id": "dec-901",
            "title": "First",
            "description": "Desc"
        })
        
        response = client.post("/decisions", json={
            "decision_id": "dec-901",
            "title": "Second",
            "description": "Desc"
        })
        assert response.status_code == 400
    
    def test_unicode_in_fields(self):
        decision_data = {
            "decision_id": "dec-902",
            "title": "Выбор технологий",
            "description": "Описание с эмодзи 🚀",
            "context": "Контекст на русском",
            "tags": ["базы данных", "микросервисы"]
        }
        response = client.post("/decisions", json=decision_data)
        assert response.status_code == 200
        assert "Выбор" in response.json()["title"]
        assert "🚀" in response.json()["description"]
    
    def test_empty_tags(self):
        decision_data = {
            "decision_id": "dec-903",
            "title": "Test",
            "description": "Desc",
            "tags": []
        }
        response = client.post("/decisions", json=decision_data)
        assert response.status_code == 200
        assert response.json()["tags"] == []
