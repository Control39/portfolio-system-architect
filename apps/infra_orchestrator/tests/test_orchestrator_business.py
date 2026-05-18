"""Business logic tests for infra-orchestrator service.

Service Tier: BUSINESS
Purpose: Comprehensive testing of infrastructure orchestration functionality

Test Coverage:
- Service registration and configuration
- Deployment and lifecycle management
- Scaling operations
- Health checks and monitoring
- Filtering and statistics
- Error handling and edge cases
- Deployment history tracking
"""

import pytest

from src.core.orchestrator import (
    ServiceConfig,
    ServiceInstance,
    InfrastructureOrchestrator,
    ServiceStatus,
    ServiceType,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def orchestrator():
    """Create a fresh InfrastructureOrchestrator instance."""
    return InfrastructureOrchestrator(cluster_name="test-cluster")


@pytest.fixture
def api_service_config():
    """Create an API service configuration."""
    return ServiceConfig(
        name="api-gateway",
        service_type=ServiceType.API,
        image="myapp/api:v1.0",
        replicas=3,
        cpu_limit="1000m",
        memory_limit="1Gi",
        environment={"LOG_LEVEL": "info"},
        ports={8080: 80},
    )


@pytest.fixture
def worker_service_config():
    """Create a worker service configuration."""
    return ServiceConfig(
        name="background-worker",
        service_type=ServiceType.WORKER,
        image="myapp/worker:v1.0",
        replicas=2,
        environment={"QUEUE": "default"},
    )


@pytest.fixture
def service_instance(api_service_config):
    """Create a service instance for testing."""
    return ServiceInstance(config=api_service_config)


# ============================================================================
# SERVICE CONFIGURATION TESTS
# ============================================================================


class TestServiceConfig:
    """Tests for service configuration."""

    def test_create_basic_config(self):
        """Test creating a basic service configuration."""
        config = ServiceConfig(
            name="simple-service",
            service_type=ServiceType.API,
            image="simple:latest",
        )

        assert config.name == "simple-service"
        assert config.service_type == ServiceType.API
        assert config.image == "simple:latest"
        assert config.replicas == 1
        assert config.cpu_limit == "500m"
        assert config.memory_limit == "512Mi"
        assert config.environment == {}
        assert config.ports == {}
        assert config.dependencies == []

    def test_create_full_config(self):
        """Test creating a full service configuration."""
        config = ServiceConfig(
            name="full-service",
            service_type=ServiceType.DATABASE,
            image="postgres:15",
            replicas=1,
            cpu_limit="2000m",
            memory_limit="4Gi",
            environment={"POSTGRES_DB": "test", "POSTGRES_USER": "admin"},
            ports={5432: 5432},
            dependencies=["network-setup"],
            health_check_path="/pg-health",
            restart_policy="on-failure",
        )

        assert config.name == "full-service"
        assert config.service_type == ServiceType.DATABASE
        assert config.cpu_limit == "2000m"
        assert config.memory_limit == "4Gi"
        assert config.environment["POSTGRES_DB"] == "test"
        assert config.ports[5432] == 5432
        assert "network-setup" in config.dependencies
        assert config.health_check_path == "/pg-health"

    def test_config_different_service_types(self):
        """Test configurations for different service types."""
        types = [
            ServiceType.API,
            ServiceType.WORKER,
            ServiceType.SCHEDULER,
            ServiceType.DATABASE,
            ServiceType.CACHE,
            ServiceType.GATEWAY,
        ]

        for service_type in types:
            config = ServiceConfig(
                name=f"{service_type.value}-service",
                service_type=service_type,
                image=f"image:{service_type.value}",
            )
            assert config.service_type == service_type


# ============================================================================
# SERVICE INSTANCE LIFECYCLE TESTS
# ============================================================================


class TestServiceInstanceLifecycle:
    """Tests for service instance lifecycle management."""

    def test_instance_created_pending(self, api_service_config):
        """Test that instance starts in pending state."""
        instance = ServiceInstance(config=api_service_config)

        assert instance.status == ServiceStatus.PENDING
        assert instance.deployed_at is None
        assert instance.stopped_at is None
        assert instance.current_replicas == 0
        assert instance.health_status == "unknown"

    def test_deploy_starts_deployment(self, service_instance):
        """Test deploy transitions to deploying state."""
        service_instance.deploy()

        assert service_instance.status == ServiceStatus.DEPLOYING
        assert len(service_instance.logs) == 1
        assert "Starting deployment" in service_instance.logs[0]

    def test_start_from_pending(self, service_instance):
        """Test starting a service from pending state."""
        service_instance.start()

        assert service_instance.status == ServiceStatus.RUNNING
        assert service_instance.deployed_at is not None
        assert service_instance.current_replicas == service_instance.config.replicas
        assert len(service_instance.logs) == 1
        assert "started" in service_instance.logs[0].lower()

    def test_start_from_stopped(self, service_instance):
        """Test starting a stopped service."""
        service_instance.start()
        service_instance.stop()
        service_instance.start()

        assert service_instance.status == ServiceStatus.RUNNING
        assert service_instance.stopped_at is not None

    def test_stop_running_service(self, service_instance):
        """Test stopping a running service."""
        service_instance.start()
        service_instance.stop()

        assert service_instance.status == ServiceStatus.STOPPED
        assert service_instance.stopped_at is not None

    def test_stop_non_running_service(self, service_instance):
        """Test stopping a non-running service."""
        # Service is in PENDING state
        service_instance.stop()

        assert service_instance.status == ServiceStatus.PENDING
        assert service_instance.stopped_at is None

    def test_fail_service(self, service_instance):
        """Test marking a service as failed."""
        service_instance.fail("Connection timeout")

        assert service_instance.status == ServiceStatus.FAILED
        assert len(service_instance.logs) == 1
        assert "ERROR" in service_instance.logs[0]
        assert "Connection timeout" in service_instance.logs[0]

    def test_scale_running_service(self, service_instance):
        """Test scaling a running service."""
        service_instance.start()
        service_instance.scale(5)

        assert service_instance.status == ServiceStatus.RUNNING
        assert service_instance.current_replicas == 5
        assert len(service_instance.logs) >= 2
        assert any("Scaling to 5 replicas" in log for log in service_instance.logs)

    def test_scale_non_running_service(self, service_instance):
        """Test scaling a non-running service."""
        # Service is in PENDING state
        service_instance.scale(5)

        assert service_instance.current_replicas == 0
        assert service_instance.status == ServiceStatus.PENDING

    def test_check_health_running(self, service_instance):
        """Test health check for running service."""
        service_instance.start()
        is_healthy = service_instance.check_health()

        assert is_healthy is True
        assert service_instance.health_status == "healthy"

    def test_check_health_failed(self, service_instance):
        """Test health check for failed service."""
        service_instance.fail("Error")
        is_healthy = service_instance.check_health()

        assert is_healthy is False
        assert service_instance.health_status == "unhealthy"

    def test_check_health_pending(self, service_instance):
        """Test health check for pending service."""
        is_healthy = service_instance.check_health()

        assert is_healthy is False
        assert service_instance.health_status == "unknown"


# ============================================================================
# ORCHESTRATOR REGISTRATION TESTS
# ============================================================================


class TestOrchestratorRegistration:
    """Tests for service registration."""

    def test_register_service_basic(self, orchestrator):
        """Test basic service registration."""
        service = orchestrator.register_service(
            name="test-api",
            service_type=ServiceType.API,
            image="test:latest",
        )

        assert service is not None
        assert service.config.name == "test-api"
        assert service.config.service_type == ServiceType.API
        assert service.config.image == "test:latest"
        assert "test-api" in orchestrator.services

    def test_register_service_with_options(self, orchestrator):
        """Test service registration with options."""
        service = orchestrator.register_service(
            name="db-service",
            service_type=ServiceType.DATABASE,
            image="postgres:15",
            replicas=1,
            cpu_limit="2000m",
            memory_limit="4Gi",
            environment={"POSTGRES_DB": "app"},
            ports={5432: 5432},
        )

        assert service.config.replicas == 1
        assert service.config.cpu_limit == "2000m"
        assert service.config.memory_limit == "4Gi"
        assert service.config.environment["POSTGRES_DB"] == "app"
        assert 5432 in service.config.ports

    def test_register_multiple_services(self, orchestrator):
        """Test registering multiple services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.register_service("db", ServiceType.DATABASE, "db:latest")

        assert len(orchestrator.services) == 3
        assert "api" in orchestrator.services
        assert "worker" in orchestrator.services
        assert "db" in orchestrator.services

    def test_register_service_adds_to_history(self, orchestrator):
        """Test that registration is logged in history."""
        orchestrator.register_service("test", ServiceType.API, "test:latest")

        history = orchestrator.get_deployment_history("test")
        assert len(history) == 1
        assert history[0]["action"] == "registered"


# ============================================================================
# ORCHESTRATOR DEPLOYMENT TESTS
# ============================================================================


class TestOrchestratorDeployment:
    """Tests for deployment operations."""

    def test_deploy_existing_service(self, orchestrator):
        """Test deploying a registered service."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")

        result = orchestrator.deploy_service("api")
        service = orchestrator.get_service("api")

        assert result is True
        assert service is not None
        assert service.status == ServiceStatus.RUNNING

    def test_deploy_nonexistent_service(self, orchestrator):
        """Test deploying a non-existent service."""
        result = orchestrator.deploy_service("nonexistent")

        assert result is False

    def test_stop_existing_service(self, orchestrator):
        """Test stopping a deployed service."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")

        result = orchestrator.stop_service("api")
        service = orchestrator.get_service("api")

        assert result is True
        assert service.status == ServiceStatus.STOPPED

    def test_stop_nonexistent_service(self, orchestrator):
        """Test stopping a non-existent service."""
        result = orchestrator.stop_service("nonexistent")

        assert result is False

    def test_deploy_all(self, orchestrator):
        """Test deploying all registered services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")

        results = orchestrator.deploy_all()

        assert results["api"] is True
        assert results["worker"] is True
        assert len([s for s in orchestrator.services.values() if s.status == ServiceStatus.RUNNING]) == 2

    def test_stop_all(self, orchestrator):
        """Test stopping all services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_all()

        results = orchestrator.stop_all()

        assert results["api"] is True
        assert results["worker"] is True
        assert all(s.status == ServiceStatus.STOPPED for s in orchestrator.services.values())


# ============================================================================
# ORCHESTRATOR SCALING TESTS
# ============================================================================


class TestOrchestratorScaling:
    """Tests for scaling operations."""

    def test_scale_service(self, orchestrator):
        """Test scaling a service."""
        orchestrator.register_service("api", ServiceType.API, "api:latest", replicas=1)
        orchestrator.deploy_service("api")

        result = orchestrator.scale_service("api", 5)
        service = orchestrator.get_service("api")

        assert result is True
        assert service.current_replicas == 5

    def test_scale_nonexistent_service(self, orchestrator):
        """Test scaling a non-existent service."""
        result = orchestrator.scale_service("nonexistent", 5)

        assert result is False

    def test_scale_down(self, orchestrator):
        """Test scaling down a service."""
        orchestrator.register_service("api", ServiceType.API, "api:latest", replicas=5)
        orchestrator.deploy_service("api")

        orchestrator.scale_service("api", 1)
        service = orchestrator.get_service("api")

        assert service.current_replicas == 1


# ============================================================================
# ORCHESTRATOR RETRIEVAL AND FILTERING TESTS
# ============================================================================


class TestOrchestratorRetrieval:
    """Tests for service retrieval and filtering."""

    def test_get_service(self, orchestrator):
        """Test getting a service by name."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")

        service = orchestrator.get_service("api")

        assert service is not None
        assert service.config.name == "api"

    def test_get_nonexistent_service(self, orchestrator):
        """Test getting a non-existent service."""
        service = orchestrator.get_service("nonexistent")

        assert service is None

    def test_list_all_services(self, orchestrator):
        """Test listing all services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")

        services = orchestrator.list_services()

        assert len(services) == 2

    def test_list_by_status(self, orchestrator):
        """Test filtering services by status."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_service("api")

        running = orchestrator.list_services(status=ServiceStatus.RUNNING)
        pending = orchestrator.list_services(status=ServiceStatus.PENDING)

        assert len(running) == 1
        assert running[0].config.name == "api"
        assert len(pending) == 1
        assert pending[0].config.name == "worker"

    def test_list_by_type(self, orchestrator):
        """Test filtering services by type."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.register_service("db", ServiceType.DATABASE, "db:latest")

        api_services = orchestrator.list_services(service_type=ServiceType.API)
        db_services = orchestrator.list_services(service_type=ServiceType.DATABASE)

        assert len(api_services) == 1
        assert len(db_services) == 1
        assert len(orchestrator.list_services(service_type=ServiceType.WORKER)) == 1

    def test_get_running_services(self, orchestrator):
        """Test getting running services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_service("api")

        running = orchestrator.get_running_services()

        assert len(running) == 1
        assert running[0].config.name == "api"

    def test_get_failed_services(self, orchestrator):
        """Test getting failed services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        api_service = orchestrator.get_service("api")
        api_service.fail("Test error")

        failed = orchestrator.get_failed_services()

        assert len(failed) == 1
        assert failed[0].config.name == "api"


# ============================================================================
# ORCHESTRATOR HEALTH CHECK TESTS
# ============================================================================


class TestOrchestratorHealth:
    """Tests for health checking."""

    def test_check_all_health_all_running(self, orchestrator):
        """Test health check when all services are running."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_all()

        health = orchestrator.check_all_health()

        assert all(health.values()) is True
        assert len(health) == 2

    def test_check_all_health_mixed(self, orchestrator):
        """Test health check with mixed service states."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_service("api")

        worker = orchestrator.get_service("worker")
        worker.fail("Error")

        health = orchestrator.check_all_health()

        assert health["api"] is True
        assert health["worker"] is False


# ============================================================================
# ORCHESTRATOR STATISTICS TESTS
# ============================================================================


class TestOrchestratorStatistics:
    """Tests for statistics and reporting."""

    def test_statistics_empty(self, orchestrator):
        """Test statistics with no services."""
        stats = orchestrator.get_statistics()

        assert stats["total_services"] == 0
        assert stats["by_status"] == {}
        assert stats["by_type"] == {}
        assert stats["total_replicas"] == 0
        assert stats["running_count"] == 0

    def test_statistics_with_services(self, orchestrator):
        """Test statistics with deployed services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest", replicas=3)
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest", replicas=2)
        orchestrator.deploy_all()

        stats = orchestrator.get_statistics()

        assert stats["total_services"] == 2
        assert stats["by_status"]["running"] == 2
        assert stats["by_type"]["api"] == 1
        assert stats["by_type"]["worker"] == 1
        assert stats["total_replicas"] == 5
        assert stats["running_count"] == 2

    def test_statistics_with_failed_services(self, orchestrator):
        """Test statistics including failed services."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_service("api")

        worker = orchestrator.get_service("worker")
        worker.fail("Error")

        stats = orchestrator.get_statistics()

        assert stats["by_status"]["running"] == 1
        assert stats["by_status"]["failed"] == 1


# ============================================================================
# DEPLOYMENT HISTORY TESTS
# ============================================================================


class TestDeploymentHistory:
    """Tests for deployment history tracking."""

    def test_empty_history(self, orchestrator):
        """Test empty deployment history."""
        history = orchestrator.get_deployment_history()

        assert history == []

    def test_history_after_registration(self, orchestrator):
        """Test history after service registration."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")

        history = orchestrator.get_deployment_history()

        assert len(history) == 1
        assert history[0]["service"] == "api"
        assert history[0]["action"] == "registered"
        assert history[0]["cluster"] == "test-cluster"

    def test_history_after_deployment(self, orchestrator):
        """Test history after service deployment."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")

        history = orchestrator.get_deployment_history("api")

        assert len(history) == 2
        assert history[0]["action"] == "registered"
        assert history[1]["action"] == "deployed"

    def test_history_after_scaling(self, orchestrator):
        """Test history after scaling."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")
        orchestrator.scale_service("api", 5)

        history = orchestrator.get_deployment_history("api")

        assert len(history) == 3
        assert history[2]["action"] == "scaled to 5"

    def test_filter_history_by_service(self, orchestrator):
        """Test filtering history by service name."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.register_service("worker", ServiceType.WORKER, "worker:latest")
        orchestrator.deploy_service("api")
        orchestrator.deploy_service("worker")

        api_history = orchestrator.get_deployment_history("api")
        worker_history = orchestrator.get_deployment_history("worker")

        assert len(api_history) == 2
        assert len(worker_history) == 2
        assert all(h["service"] == "api" for h in api_history)
        assert all(h["service"] == "worker" for h in worker_history)


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    """Edge cases and error handling tests."""

    def test_duplicate_service_names(self, orchestrator):
        """Test registering services with same name."""
        orchestrator.register_service("api", ServiceType.API, "api:v1")
        orchestrator.register_service("api", ServiceType.API, "api:v2")

        # Second registration overwrites first
        assert len(orchestrator.services) == 1
        assert orchestrator.services["api"].config.image == "api:v2"

    def test_scale_to_zero(self, orchestrator):
        """Test scaling to zero replicas."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")
        orchestrator.scale_service("api", 0)

        service = orchestrator.get_service("api")
        assert service.current_replicas == 0

    def test_scale_to_large_number(self, orchestrator):
        """Test scaling to a large number."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")
        orchestrator.scale_service("api", 1000)

        service = orchestrator.get_service("api")
        assert service.current_replicas == 1000

    def test_multiple_failures(self, orchestrator):
        """Test multiple failure events."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        api_service = orchestrator.get_service("api")

        api_service.fail("Error 1")
        api_service.fail("Error 2")

        assert len(api_service.logs) == 2
        assert "Error 1" in api_service.logs[0]
        assert "Error 2" in api_service.logs[1]

    def test_deploy_stopped_service(self, orchestrator):
        """Test redeploying a stopped service."""
        orchestrator.register_service("api", ServiceType.API, "api:latest")
        orchestrator.deploy_service("api")
        orchestrator.stop_service("api")
        orchestrator.deploy_service("api")

        service = orchestrator.get_service("api")
        assert service.status == ServiceStatus.RUNNING

    def test_empty_cluster_name(self):
        """Test orchestrator with empty cluster name."""
        orchestrator = InfrastructureOrchestrator(cluster_name="")

        orchestrator.register_service("api", ServiceType.API, "api:latest")

        history = orchestrator.get_deployment_history()
        assert history[0]["cluster"] == ""

    def test_special_characters_in_service_name(self, orchestrator):
        """Test service names with special characters."""
        orchestrator.register_service("api-gateway_v2", ServiceType.API, "api:latest")
        orchestrator.register_service("worker.service", ServiceType.WORKER, "worker:latest")

        assert "api-gateway_v2" in orchestrator.services
        assert "worker.service" in orchestrator.services


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_deployment_workflow(self, orchestrator):
        """Test complete deployment workflow."""
        # Register services
        orchestrator.register_service(
            "api",
            ServiceType.API,
            "api:v1.0",
            replicas=3,
            environment={"ENV": "prod"},
        )
        orchestrator.register_service(
            "worker",
            ServiceType.WORKER,
            "worker:v1.0",
            replicas=2,
            dependencies=["api"],
        )
        orchestrator.register_service(
            "db",
            ServiceType.DATABASE,
            "postgres:15",
            replicas=1,
        )

        # Deploy all
        results = orchestrator.deploy_all()
        assert all(results.values())

        # Verify all running
        running = orchestrator.get_running_services()
        assert len(running) == 3

        # Scale api
        orchestrator.scale_service("api", 5)
        assert orchestrator.get_service("api").current_replicas == 5

        # Check health
        health = orchestrator.check_all_health()
        assert all(health.values())

        # Get statistics
        stats = orchestrator.get_statistics()
        assert stats["total_services"] == 3
        assert stats["running_count"] == 3
        assert stats["total_replicas"] == 8

        # Stop worker
        orchestrator.stop_service("worker")
        assert orchestrator.get_service("worker").status == ServiceStatus.STOPPED

        # Verify statistics updated
        stats = orchestrator.get_statistics()
        assert stats["running_count"] == 2
        assert stats["by_status"]["stopped"] == 1

    def test_multi_cluster_deployment(self):
        """Test deployments across multiple clusters."""
        cluster1 = InfrastructureOrchestrator(cluster_name="prod-us")
        cluster2 = InfrastructureOrchestrator(cluster_name="prod-eu")

        cluster1.register_service("api", ServiceType.API, "api:latest")
        cluster2.register_service("api", ServiceType.API, "api:latest")

        cluster1.deploy_service("api")
        cluster2.deploy_service("api")

        # Verify cluster-specific history
        history1 = cluster1.get_deployment_history()
        history2 = cluster2.get_deployment_history()

        assert history1[0]["cluster"] == "prod-us"
        assert history2[0]["cluster"] == "prod-eu"

    def test_rollback_workflow(self, orchestrator):
        """Test rollback workflow."""
        orchestrator.register_service("api", ServiceType.API, "api:v1")
        orchestrator.deploy_service("api")

        # Simulate failure
        api_service = orchestrator.get_service("api")
        api_service.fail("Version 1 failed")

        # "Rollback" by stopping and redeploying with new version
        orchestrator.stop_service("api")
        orchestrator.register_service("api", ServiceType.API, "api:v2")
        orchestrator.deploy_service("api")

        # Verify new version is running
        service = orchestrator.get_service("api")
        assert service.config.image == "api:v2"
        assert service.status == ServiceStatus.RUNNING
