"""
Unit tests for assistant_orchestrator models.
"""


from src.assistant_orchestrator.models.types import (
    AnalysisResult,
    GitStats,
    MicroserviceInfo,
    SkillMarker,
)


def test_microservice_info_creation():
    """Test creation of MicroserviceInfo."""
    service = MicroserviceInfo(
        name="api-service",
        path="./services/api",
        is_production_ready=True,
        has_tests=True,
        has_docker=True,
        has_kubernetes=True,
        language="python",
        dependencies=["auth-service", "db-service"],
    )

    assert service.name == "api-service"
    assert service.path == "./services/api"
    assert service.is_production_ready is True
    assert service.has_tests is True
    assert service.has_docker is True
    assert service.has_kubernetes is True
    assert service.language == "python"
    assert "auth-service" in service.dependencies
    assert "db-service" in service.dependencies


def test_microservice_info_defaults():
    """Test default values in MicroserviceInfo."""
    service = MicroserviceInfo(name="simple-service", path="./services/simple")

    assert service.is_production_ready is False
    assert service.has_tests is False
    assert service.has_docker is False
    assert service.has_kubernetes is False
    assert service.language == "unknown"
    assert len(service.dependencies) == 0


def test_skill_marker_creation():
    """Test creation of SkillMarker."""
    marker = SkillMarker(
        id="devops.01",
        category="devops",
        level=3,
        description="Знание Docker и Kubernetes",
        evidence=["docker-compose.yml", "k8s/deployment.yaml"],
    )

    assert marker.id == "devops.01"
    assert marker.category == "devops"
    assert marker.level == 3
    assert marker.description == "Знание Docker и Kubernetes"
    assert "docker-compose.yml" in marker.evidence
    assert "k8s/deployment.yaml" in marker.evidence


def test_skill_marker_defaults():
    """Test default values in SkillMarker."""
    marker = SkillMarker(id="basic.01", category="basic", level=1, description="Базовое знание")

    assert len(marker.evidence) == 0


def test_git_stats_creation():
    """Test creation of GitStats."""
    stats = GitStats(
        total_commits=150,
        recent_activity_days=25,
        contributors=["alice", "bob", "charlie"],
        branches=["main", "develop", "feature/new-ui"],
    )

    assert stats.total_commits == 150
    assert stats.recent_activity_days == 25
    assert "alice" in stats.contributors
    assert "main" in stats.branches


def test_git_stats_defaults():
    """Test default values in GitStats."""
    stats = GitStats()

    assert stats.total_commits == 0
    assert stats.recent_activity_days == 0
    assert len(stats.contributors) == 0
    assert len(stats.branches) == 0


def test_analysis_result_creation():
    """Test creation of AnalysisResult."""
    result = AnalysisResult(
        timestamp="2026-05-01T12:00:00",
        microservices={"services": []},
        skill_markers={"total_count": 5},
        architecture_docs=["ARCHITECTURE.md"],
        git_stats={"total_commits": 100},
        dependencies={"api": ["auth"]},
    )

    assert result.timestamp == "2026-05-01T12:00:00"
    assert len(result.microservices) > 0
    assert len(result.skill_markers) > 0
    assert len(result.architecture_docs) == 1
    assert len(result.git_stats) > 0
    assert len(result.dependencies) > 0


def test_analysis_result_defaults():
    """Test default values in AnalysisResult."""
    result = AnalysisResult(timestamp="2026-05-01T12:00:00")

    assert len(result.microservices) == 0
    assert len(result.skill_markers) == 0
    assert len(result.architecture_docs) == 0
    assert len(result.git_stats) == 0
    assert len(result.dependencies) == 0


def test_analysis_result_dict_method():
    """Test the dict() method of AnalysisResult."""
    result = AnalysisResult(
        timestamp="2026-05-01T12:00:00",
        microservices={"services": []},
        skill_markers={"total_count": 5},
        architecture_docs=["ARCHITECTURE.md"],
        git_stats={"total_commits": 100},
        dependencies={"api": ["auth"]},
    )

    result_dict = result.dict()
    assert isinstance(result_dict, dict)
    assert result_dict["timestamp"] == "2026-05-01T12:00:00"
    assert "microservices" in result_dict
    assert "skill_markers" in result_dict
    assert "architecture_docs" in result_dict
    assert "git_stats" in result_dict
    assert "dependencies" in result_dict
