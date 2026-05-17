"""
Тесты для Knowledge Graph API
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from apps.knowledge_graph.src.api.main import (
    app, Entity, Relationship, 
    entities_db, relationships_db
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Очистка базы перед каждым тестом"""
    entities_db.clear()
    relationships_db.clear()
    yield
    entities_db.clear()
    relationships_db.clear()


class TestHealthEndpoints:
    """Тесты health check"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "knowledge-graph"
    
    def test_readiness(self):
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
    
    def test_liveness(self):
        response = client.get("/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"


class TestEntityCRUD:
    """Тесты CRUD для сущностей"""
    
    def test_create_entity(self):
        entity_data = {
            "entity_id": "user-001",
            "entity_type": "person",
            "properties": {"name": "Alice", "age": 30}
        }
        response = client.post("/entities", json=entity_data)
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == "user-001"
        assert data["entity_type"] == "person"
    
    def test_get_entity(self):
        # Создаем
        client.post("/entities", json={
            "entity_id": "user-002",
            "entity_type": "person",
            "properties": {"name": "Bob"}
        })
        # Получаем
        response = client.get("/entities/user-002")
        assert response.status_code == 200
        assert response.json()["entity_id"] == "user-002"
    
    def test_get_entity_not_found(self):
        response = client.get("/entities/nonexistent")
        assert response.status_code == 404
    
    def test_update_entity(self):
        # Создаем
        client.post("/entities", json={
            "entity_id": "user-003",
            "entity_type": "person",
            "properties": {"name": "Charlie"}
        })
        # Обновляем
        update_data = {
            "entity_id": "user-003",
            "entity_type": "person",
            "properties": {"name": "Charlie Jr.", "age": 5}
        }
        response = client.put("/entities/user-003", json=update_data)
        assert response.status_code == 200
        assert response.json()["properties"]["name"] == "Charlie Jr."
    
    def test_delete_entity(self):
        # Создаем
        client.post("/entities", json={
            "entity_id": "user-004",
            "entity_type": "person",
            "properties": {}
        })
        # Удаляем
        response = client.delete("/entities/user-004")
        assert response.status_code == 200
        # Проверяем удаление
        get_response = client.get("/entities/user-004")
        assert get_response.status_code == 404
    
    def test_duplicate_entity_id(self):
        entity_data = {
            "entity_id": "user-005",
            "entity_type": "person",
            "properties": {}
        }
        client.post("/entities", json=entity_data)
        response = client.post("/entities", json=entity_data)
        assert response.status_code == 400


class TestRelationshipCRUD:
    """Тесты CRUD для отношений"""
    
    def test_create_relationship(self):
        # Создаем сущности
        client.post("/entities", json={
            "entity_id": "user-010",
            "entity_type": "person",
            "properties": {}
        })
        client.post("/entities", json={
            "entity_id": "company-001",
            "entity_type": "organization",
            "properties": {}
        })
        
        # Создаем отношение
        rel_data = {
            "relationship_id": "rel-001",
            "source_entity": "user-010",
            "target_entity": "company-001",
            "relationship_type": "works_at",
            "properties": {"since": "2020"}
        }
        response = client.post("/relationships", json=rel_data)
        assert response.status_code == 200
        assert response.json()["relationship_type"] == "works_at"
    
    def test_create_relationship_missing_source(self):
        rel_data = {
            "relationship_id": "rel-002",
            "source_entity": "nonexistent",
            "target_entity": "company-001",
            "relationship_type": "works_at",
            "properties": {}
        }
        response = client.post("/relationships", json=rel_data)
        assert response.status_code == 404
    
    def test_get_relationship(self):
        # Создаем сущности и отношение
        client.post("/entities", json={"entity_id": "u1", "entity_type": "p", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "p", "properties": {}})
        client.post("/relationships", json={
            "relationship_id": "rel-003",
            "source_entity": "u1",
            "target_entity": "u2",
            "relationship_type": "knows",
            "properties": {}
        })
        
        response = client.get("/relationships/rel-003")
        assert response.status_code == 200
        assert response.json()["relationship_type"] == "knows"
    
    def test_delete_relationship(self):
        # Создаем
        client.post("/entities", json={"entity_id": "u1", "entity_type": "p", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "p", "properties": {}})
        client.post("/relationships", json={
            "relationship_id": "rel-004",
            "source_entity": "u1",
            "target_entity": "u2",
            "relationship_type": "knows",
            "properties": {}
        })
        
        response = client.delete("/relationships/rel-004")
        assert response.status_code == 200
        get_response = client.get("/relationships/rel-004")
        assert get_response.status_code == 404


class TestEntityList:
    """Тесты списка сущностей"""
    
    def test_list_empty(self):
        response = client.get("/entities")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_with_filter(self):
        # Создаем сущности разных типов
        client.post("/entities", json={"entity_id": "u1", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "c1", "entity_type": "company", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "person", "properties": {}})
        
        # Фильтр по типу
        response = client.get("/entities?entity_type=person")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert all(e["entity_type"] == "person" for e in response.json())


class TestRelationshipList:
    """Тесты списка отношений"""
    
    def test_list_with_filters(self):
        # Создаем сущности
        for i in range(1, 5):
            client.post("/entities", json={"entity_id": f"u{i}", "entity_type": "p", "properties": {}})
        
        # Создаем отношения
        client.post("/relationships", json={
            "relationship_id": "r1", "source_entity": "u1", "target_entity": "u2",
            "relationship_type": "knows", "properties": {}
        })
        client.post("/relationships", json={
            "relationship_id": "r2", "source_entity": "u2", "target_entity": "u3",
            "relationship_type": "knows", "properties": {}
        })
        client.post("/relationships", json={
            "relationship_id": "r3", "source_entity": "u1", "target_entity": "u4",
            "relationship_type": "manages", "properties": {}
        })
        
        # Фильтр по типу
        response = client.get("/relationships?relationship_type=knows")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Фильтр по source
        response = client.get("/relationships?source=u1")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestNeighbors:
    """Тесты соседей сущности"""
    
    def test_get_neighbors(self):
        # Создаем граф: u1 -knows-> u2, u1 -works_at-> c1
        client.post("/entities", json={"entity_id": "u1", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "c1", "entity_type": "company", "properties": {}})
        
        client.post("/relationships", json={
            "relationship_id": "r1", "source_entity": "u1", "target_entity": "u2",
            "relationship_type": "knows", "properties": {}
        })
        client.post("/relationships", json={
            "relationship_id": "r2", "source_entity": "u1", "target_entity": "c1",
            "relationship_type": "works_at", "properties": {}
        })
        
        response = client.get("/entities/u1/neighbors")
        assert response.status_code == 200
        assert response.json()["count"] == 2
        neighbor_ids = [n["entity_id"] for n in response.json()["neighbors"]]
        assert "u2" in neighbor_ids
        assert "c1" in neighbor_ids
    
    def test_neighbors_not_found(self):
        response = client.get("/entities/nonexistent/neighbors")
        assert response.status_code == 404


class TestQuery:
    """Тесты графовых запросов"""
    
    def test_execute_query(self):
        # Создаем данные
        client.post("/entities", json={"entity_id": "u1", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "c1", "entity_type": "company", "properties": {}})
        client.post("/relationships", json={
            "relationship_id": "r1", "source_entity": "u1", "target_entity": "c1",
            "relationship_type": "works_at", "properties": {}
        })
        
        # Запрос всех
        response = client.get("/query")
        assert response.status_code == 200
        assert len(response.json()["entities"]) == 2
        assert len(response.json()["relationships"]) == 1
        
        # Запрос по типу сущности
        response = client.get("/query?entity_type=person")
        assert response.status_code == 200
        assert len(response.json()["entities"]) == 1
        
        # Запрос по типу отношения
        response = client.get("/query?relationship_type=works_at")
        assert response.status_code == 200
        assert len(response.json()["relationships"]) == 1


class TestStatistics:
    """Тесты статистики"""
    
    def test_statistics_empty(self):
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_entities"] == 0
        assert data["total_relationships"] == 0
    
    def test_statistics_with_data(self):
        # Создаем данные
        client.post("/entities", json={"entity_id": "u1", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "person", "properties": {}})
        client.post("/entities", json={"entity_id": "c1", "entity_type": "company", "properties": {}})
        client.post("/relationships", json={
            "relationship_id": "r1", "source_entity": "u1", "target_entity": "c1",
            "relationship_type": "works_at", "properties": {}
        })
        client.post("/relationships", json={
            "relationship_id": "r2", "source_entity": "u1", "target_entity": "u2",
            "relationship_type": "knows", "properties": {}
        })
        
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_entities"] == 3
        assert data["total_relationships"] == 2
        assert data["entity_types"]["person"] == 2
        assert data["entity_types"]["company"] == 1
        assert data["relationship_types"]["works_at"] == 1
        assert data["relationship_types"]["knows"] == 1


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_delete_entity_cascades_relationships(self):
        # Создаем граф
        client.post("/entities", json={"entity_id": "u1", "entity_type": "p", "properties": {}})
        client.post("/entities", json={"entity_id": "u2", "entity_type": "p", "properties": {}})
        client.post("/relationships", json={
            "relationship_id": "r1", "source_entity": "u1", "target_entity": "u2",
            "relationship_type": "knows", "properties": {}
        })
        
        # Удаляем u1
        client.delete("/entities/u1")
        
        # Проверяем, что отношение удалено
        rel_response = client.get("/relationships/r1")
        assert rel_response.status_code == 404
    
    def test_unicode_in_properties(self):
        entity_data = {
            "entity_id": "user-unicode",
            "entity_type": "персона",
            "properties": {"имя": "Катя", "описание": "Разработчик 🚀"}
        }
        response = client.post("/entities", json=entity_data)
        assert response.status_code == 200
        assert response.json()["properties"]["имя"] == "Катя"
        assert "🚀" in response.json()["properties"]["описание"]
    
    def test_empty_properties(self):
        entity_data = {
            "entity_id": "user-empty",
            "entity_type": "person",
            "properties": {}
        }
        response = client.post("/entities", json=entity_data)
        assert response.status_code == 200
        assert response.json()["properties"] == {}
