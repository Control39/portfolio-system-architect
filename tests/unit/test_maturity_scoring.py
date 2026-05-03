"""Unit tests for maturity scoring."""

from src.assistant_orchestrator.core.maturity_scoring import MaturityScorer


def test_maturity_scorer_empty():
    """Test scoring with empty analysis."""
    analysis = {
        "microservices": {"services": []},
        "skill_markers": {"total_count": 0, "categories": []},
        "architecture_docs": [],
        "git_stats": {
            "total_commits": 0,
            "recent_activity_days": 0,
            "contributors": [],
        },
        "dependencies": {},
    }

    scorer = MaturityScorer(analysis)
    score = scorer.calculate_score()

    assert score == 0.0
    assert isinstance(score, float)


def test_maturity_scorer_basic():
    """Test scoring with basic project metrics."""
    analysis = {
        "microservices": {
            "services": [
                {
                    "name": "api",
                    "is_production_ready": True,
                    "has_tests": True,
                    "has_docker": True,
                },
                {
                    "name": "worker",
                    "is_production_ready": False,
                    "has_tests": False,
                    "has_docker": True,
                },
            ],
            "has_docker_compose": True,
            "has_kubernetes": False,
        },
        "skill_markers": {
            "total_count": 25,
            "categories": ["Python", "DevOps", "Cloud"],
        },
        "architecture_docs": ["docs/architecture.md", "docs/design.md"],
        "git_stats": {
            "total_commits": 150,
            "recent_activity_days": 15,
            "contributors": ["user1", "user2", "user3"],
        },
        "dependencies": {
            "api": ["postgres", "redis"],
            "worker": ["redis"],
        },
    }

    scorer = MaturityScorer(analysis)
    score = scorer.calculate_score()

    # Score should be between 0 and 5
    assert 0.0 <= score <= 5.0
    # With these metrics, score should be > 0
    assert score > 0.0


def test_maturity_scorer_recommendations():
    """Test that recommendations are generated."""
    analysis = {
        "microservices": {
            "services": [
                {
                    "name": "api",
                    "is_production_ready": False,
                    "has_tests": False,
                    "has_docker": False,
                },
            ],
            "has_docker_compose": False,
            "has_kubernetes": False,
        },
        "skill_markers": {
            "total_count": 5,
            "categories": ["Python"],
        },
        "architecture_docs": [],
        "git_stats": {
            "total_commits": 10,
            "recent_activity_days": 2,
            "contributors": ["user1"],
        },
        "dependencies": {},
    }

    scorer = MaturityScorer(analysis)
    recommendations = scorer.get_recommendations()

    # Should have at least one recommendation for low maturity
    assert len(recommendations) > 0
    assert all("category" in rec for rec in recommendations)
    assert all("title" in rec for rec in recommendations)
    assert all("potential_gain" in rec for rec in recommendations)


def test_score_microservices():
    """Test microservices scoring in isolation."""
    analysis = {
        "microservices": {
            "services": [
                {"is_production_ready": True, "has_tests": True, "has_docker": True},
                {"is_production_ready": True, "has_tests": True, "has_docker": True},
                {"is_production_ready": False, "has_tests": False, "has_docker": False},
            ],
        },
        "skill_markers": {"total_count": 0, "categories": []},
        "architecture_docs": [],
        "git_stats": {
            "total_commits": 0,
            "recent_activity_days": 0,
            "contributors": [],
        },
        "dependencies": {},
    }

    scorer = MaturityScorer(analysis)
    # Access private method via name mangling (not ideal, but for testing)
    # Instead we'll test through public calculate_score
    score = scorer.calculate_score()
    assert score > 0.0


def test_score_cap():
    """Test that score is capped at 5.0."""
    analysis = {
        "microservices": {
            "services": [
                {"is_production_ready": True, "has_tests": True, "has_docker": True}
                for _ in range(10)
            ],
            "has_docker_compose": True,
            "has_kubernetes": True,
        },
        "skill_markers": {
            "total_count": 200,
            "categories": [f"Category{i}" for i in range(30)],
        },
        "architecture_docs": [f"doc{i}.md" for i in range(20)],
        "git_stats": {
            "total_commits": 1000,
            "recent_activity_days": 100,
            "contributors": [f"user{i}" for i in range(20)],
        },
        "dependencies": {f"service{i}": [] for i in range(10)},
    }

    scorer = MaturityScorer(analysis)
    score = scorer.calculate_score()

    assert score <= 5.0
    # With these perfect metrics, score should be close to 5.0
    assert score >= 4.0
