"""
Тесты для Infrastructure Orchestrator API
"""

import pytest
"""
Тесты для Infrastructure Orchestrator API
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импортируем напрямую
from src.api.app import (
    app, ServiceConfig, ServiceInstance,
    services_db, instances_db, deployment_history,
    ServiceStatus, ServiceType
)

client = TestClient(app)

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Очистка базы перед каждым тестом"""
    services_db.clear()
    instances_db.clear()
    deployment_history.clear()
    yield
    services_db.clear()
    instances_db.clear()
    deployment_history.clear()


class TestHealthEndpoints:
    """Тесты health check"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "infra-orchestrator"
    
    def test_readiness(self):
        response = client.get("/ready")
        assert response.status_code == 200
    
    def test_liveness(self):
        response = client.get("/live")
        assert response.status_code == 200


class TestServiceCRUD:
    """Тесты CRUD для конфигураций сервисов"""
    
    def test_register_service(self):
        config_data = {
            "service_id": "api-001",
            "name": "Main API",
            "service_type": "api",
            "image": "myapp/api:latest",
            "replicas": 2,
            "ports": {"http": 8000},
            "environment": {"ENV": "prod"}
        }
        response = client.post("/services", json=config_data)
        assert response.status_code == 200
        data = response.json()
        assert data["service_id"] == "api-001"
        assert data["replicas"] == 2
    
    def test_get_service(self):
        client.post("/services", json={
            "service_id": "api-002",
            "name": "Test API",
            "service_type": "api",
            "image": "test:latest"
        })
        response = client.get("/services/api-002")
        assert response.status_code == 200
        assert response.json()["name"] == "Test API"
    
    def test_get_service_not_found(self):
        response = client.get("/services/nonexistent")
        assert response.status_code == 404
    
    def test_update_service(self):
        client.post("/services", json={
            "service_id": "api-003",
            "name": "Original",
            "service_type": "api",
            "image": "test:latest"
        })
        update_data = {
            "service_id": "api-003",
            "name": "Updated",
            "service_type": "api",
            "image": "test:v2"
        }
        response = client.put("/services/api-003", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"
    
    def test_delete_service(self):
        client.post("/services", json={
            "service_id": "api-004",
            "name": "ToDelete",
            "service_type": "api",
            "image": "test:latest"
        })
        response = client.delete("/services/api-004")
        assert response.status_code == 200
        get_response = client.get("/services/api-004")
        assert get_response.status_code == 404
    
    def test_duplicate_service_id(self):
        client.post("/services", json={
            "service_id": "api-005",
            "name": "First",
            "service_type": "api",
            "image": "test:latest"
        })
        response = client.post("/services", json={
            "service_id": "api-005",
            "name": "Second",
            "service_type": "api",
            "image": "test:latest"
        })
        assert response.status_code == 400


class TestInstanceDeployment:
    """Тесты развёртывания экземпляров"""
    
    def test_deploy_service(self):
        # Регистрируем сервис
        client.post("/services", json={
            "service_id": "api-101",
            "name": "DeployTest",
            "service_type": "api",
            "image": "test:latest"
        })
        
        # Развёртываем
        response = client.post("/instances/api-101/deploy")
        assert response.status_code == 200
        data = response.json()
        assert data["service_id"] == "api-101"
        assert data["status"] == "running"
        assert data["health_status"] == "healthy"
        assert data["instance_id"].startswith("api-101-")
    
    def test_deploy_nonexistent_service(self):
        response = client.post("/instances/nonexistent/deploy")
        assert response.status_code == 404
    
    def test_deploy_to_cluster(self):
        client.post("/services", json={
            "service_id": "api-102",
            "name": "ClusterTest",
            "service_type": "api",
            "image": "test:latest"
        })
        
        response = client.post("/instances/api-102/deploy?cluster=production")
        assert response.status_code == 200
        assert response.json()["cluster"] == "production"


class TestInstanceLifecycle:
    """Тесты жизненного цикла экземпляров"""
    
    def test_start_instance(self):
        # Создаем и развёртываем
        client.post("/services", json={
            "service_id": "api-201",
            "name": "LifecycleTest",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-201/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        # Останавливаем
        client.post(f"/instances/{instance_id}/stop")
        
        # Запускаем
        response = client.post(f"/instances/{instance_id}/start")
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        assert response.json()["health_status"] == "healthy"
    
    def test_stop_instance(self):
        client.post("/services", json={
            "service_id": "api-202",
            "name": "StopTest",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-202/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        response = client.post(f"/instances/{instance_id}/stop")
        assert response.status_code == 200
        assert response.json()["status"] == "stopped"
    
    def test_delete_instance(self):
        client.post("/services", json={
            "service_id": "api-203",
            "name": "DeleteTest",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-203/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        response = client.delete(f"/instances/{instance_id}")
        assert response.status_code == 200
        
        # Проверяем удаление
        instances = client.get("/instances").json()
        assert len(instances) == 0
    
    def test_start_nonexistent_instance(self):
        response = client.post("/instances/nonexistent/start")
        assert response.status_code == 404


class TestScaling:
    """Тесты масштабирования"""
    
    def test_scale_instance(self):
        client.post("/services", json={
            "service_id": "api-301",
            "name": "ScaleTest",
            "service_type": "api",
            "image": "test:latest",
            "replicas": 1
        })
        deploy_resp = client.post("/instances/api-301/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        response = client.post(f"/instances/{instance_id}/scale?replicas=5")
        assert response.status_code == 200
        assert response.json()["config"]["replicas"] == 5
        assert response.json()["status"] == "running"
    
    def test_scale_to_invalid_replicas(self):
        client.post("/services", json={
            "service_id": "api-302",
            "name": "InvalidScale",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-302/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        response = client.post(f"/instances/{instance_id}/scale?replicas=0")
        assert response.status_code == 400
    
    def test_scale_nonexistent_instance(self):
        response = client.post("/instances/nonexistent/scale?replicas=3")
        assert response.status_code == 404


class TestInstanceList:
    """Тесты списка экземпляров"""
    
    def test_list_empty(self):
        response = client.get("/instances")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_with_status_filter(self):
        # Создаем несколько экземпляров
        for i in range(3):
            client.post("/services", json={
                "service_id": f"api-{i}",
                "name": f"Service{i}",
                "service_type": "api",
                "image": "test:latest"
            })
            client.post(f"/instances/api-{i}/deploy")
        
        # Останавливаем один
        instances = client.get("/instances").json()
        client.post(f"/instances/{instances[0]['instance_id']}/stop")
        
        # Фильтр по статусу
        response = client.get("/instances?status=running")
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_list_by_cluster(self):
        client.post("/services", json={
            "service_id": "api-401",
            "name": "Cluster1",
            "service_type": "api",
            "image": "test:latest"
        })
        client.post("/services", json={
            "service_id": "api-402",
            "name": "Cluster2",
            "service_type": "api",
            "image": "test:latest"
        })
        
        client.post("/instances/api-401/deploy?cluster=production")
        client.post("/instances/api-402/deploy?cluster=staging")
        
        response = client.get("/instances?cluster=production")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["cluster"] == "production"


class TestHealthChecks:
    """Тесты проверки здоровья"""
    
    def test_check_instance_health(self):
        client.post("/services", json={
            "service_id": "api-501",
            "name": "HealthTest",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-501/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        
        response = client.get(f"/instances/{instance_id}/health")
        assert response.status_code == 200
        assert response.json()["health_status"] == "healthy"
    
    def test_check_all_health(self):
        for i in range(2):
            client.post("/services", json={
                "service_id": f"api-{i}",
                "name": f"Health{i}",
                "service_type": "api",
                "image": "test:latest"
            })
            client.post(f"/instances/api-{i}/deploy")
        
        response = client.get("/health/all")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for instance_id, info in data.items():
            assert info["health_status"] == "healthy"


class TestStatistics:
    """Тесты статистики"""
    
    def test_statistics_empty(self):
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_instances"] == 0
        assert data["total_services"] == 0
    
    def test_statistics_with_data(self):
        # Создаем сервисы разных типов
        client.post("/services", json={
            "service_id": "api-601",
            "name": "API",
            "service_type": "api",
            "image": "test:latest"
        })
        client.post("/services", json={
            "service_id": "db-601",
            "name": "Database",
            "service_type": "database",
            "image": "postgres:latest"
        })
        client.post("/services", json={
            "service_id": "cache-601",
            "name": "Cache",
            "service_type": "cache",
            "image": "redis:latest"
        })
        
        # Развёртываем
        client.post("/instances/api-601/deploy?cluster=prod")
        client.post("/instances/db-601/deploy?cluster=prod")
        client.post("/instances/cache-601/deploy?cluster=staging")
        
        response = client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_instances"] == 3
        assert data["total_services"] == 3
        assert data["by_type"]["api"] == 1
        assert data["by_type"]["database"] == 1
        assert data["by_type"]["cache"] == 1
        assert data["by_cluster"]["prod"] == 2
        assert data["by_cluster"]["staging"] == 1


class TestHistory:
    """Тесты истории развёртываний"""
    
    def test_history_empty(self):
        response = client.get("/history")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_history_with_deployments(self):
        client.post("/services", json={
            "service_id": "api-701",
            "name": "HistoryTest",
            "service_type": "api",
            "image": "test:latest"
        })
        deploy_resp = client.post("/instances/api-701/deploy")
        instance_id = deploy_resp.json()["instance_id"]
        client.post(f"/instances/{instance_id}/scale?replicas=2")
        
        response = client.get("/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["action"] == "deploy"
        assert data[1]["action"] == "scale"
        assert data[1]["replicas"] == 2
    
    def test_history_limit(self):
        # Создаем 5 развёртываний
        for i in range(5):
            client.post("/services", json={
                "service_id": f"api-{i}",
                "name": f"Service{i}",
                "service_type": "api",
                "image": "test:latest"
            })
            client.post(f"/instances/api-{i}/deploy")
        
        response = client.get("/history?limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestGetByType:
    """Тесты фильтрации по типу"""
    
    def test_get_by_type(self):
        client.post("/services", json={
            "service_id": "api-801",
            "name": "API",
            "service_type": "api",
            "image": "test:latest"
        })
        client.post("/services", json={
            "service_id": "db-801",
            "name": "DB",
            "service_type": "database",
            "image": "postgres:latest"
        })
        
        client.post("/instances/api-801/deploy")
        client.post("/instances/db-801/deploy")
        
        response = client.get("/instances/by-type?service_type=api")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["config"]["service_type"] == "api"


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_unicode_in_fields(self):
        config_data = {
            "service_id": "api-unicode",
            "name": "Сервис на русском",
            "service_type": "api",
            "image": "тест:latest",
            "environment": {"НАЗВАНИЕ": "Значение 🚀"}
        }
        response = client.post("/services", json=config_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Сервис на русском"
        assert "🚀" in response.json()["environment"]["НАЗВАНИЕ"]
    
    def test_empty_environment(self):
        config_data = {
            "service_id": "api-empty",
            "name": "EmptyEnv",
            "service_type": "api",
            "image": "test:latest",
            "environment": {}
        }
        response = client.post("/services", json=config_data)
        assert response.status_code == 200
        assert response.json()["environment"] == {}
    
    def test_service_with_dependencies(self):
        config_data = {
            "service_id": "api-dep",
            "name": "WithDeps",
            "service_type": "api",
            "image": "test:latest",
            "depends_on": ["db-001", "cache-001"]
        }
        response = client.post("/services", json=config_data)
        assert response.status_code == 200
        assert response.json()["depends_on"] == ["db-001", "cache-001"]
