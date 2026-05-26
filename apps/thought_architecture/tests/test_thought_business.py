"""Business logic tests for thought-architecture service.

Service Tier: BUSINESS
Purpose: Comprehensive testing of core architecture decision functionality

Test Coverage:
- Decision creation and management
- Status transitions (approve, reject, supersede)
- Filtering and search
- Statistics and reporting
- Edge cases and error handling
"""

import pytest

from src.core import (
    DecisionStatus,
    DecisionLevel,
    ArchitectureRecord,
    ThoughtArchitect,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def architect():
    """Create a fresh ThoughtArchitect instance."""
    return ThoughtArchitect(project_name="TestProject")


@pytest.fixture
def sample_decision(architect):
    """Create a sample decision for testing."""
    return architect.create_decision(
        title="Use PostgreSQL for data storage",
        description="PostgreSQL selected for its robustness and JSON support",
        level=DecisionLevel.HIGH,
        context="Need reliable relational database with JSON capabilities",
        tags=["database", "storage", "backend"],
    )


@pytest.fixture
def sample_record(sample_decision):
    """Create a sample architecture record."""
    return ArchitectureRecord(decision=sample_decision)


# ============================================================================
# DECISION CREATION TESTS
# ============================================================================


class TestDecisionCreation:
    """Tests for decision creation functionality."""

    def test_create_decision_basic(self, architect):
        """Test basic decision creation."""
        decision = architect.create_decision(
            title="Test Decision",
            description="Test description",
        )

        assert decision is not None
        assert decision.title == "Test Decision"
        assert decision.description == "Test description"
        assert decision.status == DecisionStatus.PROPOSED
        assert decision.level == DecisionLevel.MEDIUM
        assert decision.id.startswith("testproject-")

    def test_create_decision_with_all_params(self, architect):
        """Test decision creation with all parameters."""
        decision = architect.create_decision(
            title="Full Decision",
            description="Full description",
            level=DecisionLevel.CRITICAL,
            context="Important context",
            tags=["tag1", "tag2"],
        )

        assert decision.level == DecisionLevel.CRITICAL
        assert decision.context == "Important context"
        assert "tag1" in decision.tags
        assert "tag2" in decision.tags

    def test_create_decision_unique_ids(self, architect):
        """Test that each decision gets a unique ID."""
        d1 = architect.create_decision(title="First", description="Desc")
        d2 = architect.create_decision(title="Second", description="Desc")
        d3 = architect.create_decision(title="Third", description="Desc")

        assert d1.id != d2.id
        assert d2.id != d3.id
        assert d1.id != d3.id

    def test_create_decision_stored_in_registry(self, architect):
        """Test that decisions are stored in the architect."""
        decision = architect.create_decision(title="Test", description="Desc")

        assert decision.id in architect.decisions
        assert architect.decisions[decision.id] == decision

    def test_create_decision_record_created(self, architect):
        """Test that architecture record is created with decision."""
        decision = architect.create_decision(title="Test", description="Desc")

        assert decision.id in architect.records
        record = architect.records[decision.id]
        assert record.decision == decision
        assert record.evidence == []
        assert record.reviews == []


# ============================================================================
# DECISION RETRIEVAL TESTS
# ============================================================================


class TestDecisionRetrieval:
    """Tests for decision retrieval functionality."""

    def test_get_decision_exists(self, architect, sample_decision):
        """Test retrieving an existing decision."""
        retrieved = architect.get_decision(sample_decision.id)

        assert retrieved is not None
        assert retrieved.id == sample_decision.id
        assert retrieved.title == sample_decision.title

    def test_get_decision_not_exists(self, architect):
        """Test retrieving non-existent decision."""
        retrieved = architect.get_decision("non-existent-id")

        assert retrieved is None

    def test_list_all_decisions(self, architect, sample_decision):
        """Test listing all decisions."""
        architect.create_decision(title="Second", description="Desc")
        architect.create_decision(title="Third", description="Desc")

        all_decisions = architect.list_decisions()

        assert len(all_decisions) == 3
        assert sample_decision in all_decisions

    def test_list_decisions_by_status(self, architect, sample_decision):
        """Test filtering decisions by status."""
        approved = architect.create_decision(title="Approved", description="Desc")
        approved.approve()

        rejected = architect.create_decision(title="Rejected", description="Desc")
        rejected.reject("Not needed")

        proposed = architect.list_decisions(status=DecisionStatus.PROPOSED)
        accepted = architect.list_decisions(status=DecisionStatus.ACCEPTED)
        rejected_list = architect.list_decisions(status=DecisionStatus.REJECTED)

        assert sample_decision in proposed
        assert approved in accepted
        assert rejected in rejected_list
        assert approved not in proposed
        assert rejected not in proposed

    def test_list_decisions_by_level(self, architect):
        """Test filtering decisions by level."""
        critical = architect.create_decision(
            title="Critical", description="Desc", level=DecisionLevel.CRITICAL
        )
        low = architect.create_decision(
            title="Low", description="Desc", level=DecisionLevel.LOW
        )

        critical_list = architect.list_decisions(level=DecisionLevel.CRITICAL)
        low_list = architect.list_decisions(level=DecisionLevel.LOW)

        assert critical in critical_list
        assert low in low_list
        assert low not in critical_list
        assert critical not in low_list

    def test_list_decisions_by_tag(self, architect, sample_decision):
        """Test filtering decisions by tag."""
        tagged = architect.create_decision(
            title="Tagged", description="Desc", tags=["database", "important"]
        )
        untagged = architect.create_decision(title="Untagged", description="Desc")

        db_decisions = architect.list_decisions(tag="database")
        important_decisions = architect.list_decisions(tag="important")

        assert sample_decision in db_decisions
        assert tagged in db_decisions
        assert tagged in important_decisions
        assert untagged not in db_decisions
        assert untagged not in important_decisions


# ============================================================================
# DECISION STATUS TRANSITION TESTS
# ============================================================================


class TestDecisionStatusTransitions:
    """Tests for decision status transitions."""

    def test_approve_decision(self, architect, sample_decision):
        """Test approving a decision."""
        import time
        time.sleep(0.001)  # Ensure time difference
        result = architect.approve_decision(sample_decision.id)

        assert result is True
        assert sample_decision.status == DecisionStatus.ACCEPTED
        assert sample_decision.updated_at >= sample_decision.created_at

    def test_approve_nonexistent_decision(self, architect):
        """Test approving non-existent decision."""
        result = architect.approve_decision("non-existent")

        assert result is False

    def test_reject_decision(self, architect, sample_decision):
        """Test rejecting a decision."""
        result = architect.reject_decision(sample_decision.id, "Insufficient analysis")

        assert result is True
        assert sample_decision.status == DecisionStatus.REJECTED
        assert sample_decision.metadata.get("rejection_reason") == "Insufficient analysis"

    def test_reject_decision_without_reason(self, architect, sample_decision):
        """Test rejecting a decision without reason."""
        result = architect.reject_decision(sample_decision.id)

        assert result is True
        assert sample_decision.status == DecisionStatus.REJECTED
        assert "rejection_reason" not in sample_decision.metadata or sample_decision.metadata.get("rejection_reason") == ""

    def test_reject_nonexistent_decision(self, architect):
        """Test rejecting non-existent decision."""
        result = architect.reject_decision("non-existent")

        assert result is False

    def test_supersede_decision(self, architect, sample_decision):
        """Test superseding a decision."""
        replacement = architect.create_decision(title="Replacement", description="New approach")
        
        sample_decision.supersede(replacement.id)

        assert sample_decision.status == DecisionStatus.SUPERSEDED
        assert sample_decision.metadata.get("replacement_id") == replacement.id

    def test_multiple_status_changes(self, architect):
        """Test multiple status changes on same decision."""
        decision = architect.create_decision(title="Test", description="Desc")

        assert decision.status == DecisionStatus.PROPOSED

        decision.approve()
        assert decision.status == DecisionStatus.ACCEPTED

        # Can still be superseded even if accepted
        replacement = architect.create_decision(title="Replacement", description="New")
        decision.supersede(replacement.id)
        assert decision.status == DecisionStatus.SUPERSEDED


# ============================================================================
# ARCHITECTURE RECORD TESTS
# ============================================================================


class TestArchitectureRecord:
    """Tests for architecture record functionality."""

    def test_add_evidence(self, sample_record):
        """Test adding evidence to record."""
        sample_record.add_evidence("https://example.com/proof1")
        sample_record.add_evidence("https://example.com/proof2")

        assert len(sample_record.evidence) == 2
        assert "https://example.com/proof1" in sample_record.evidence
        assert "https://example.com/proof2" in sample_record.evidence

    def test_add_review(self, sample_record):
        """Test adding review to record."""
        sample_record.add_review(
            reviewer="John Doe",
            comments="Looks good, approved",
            approved=True,
        )

        assert len(sample_record.reviews) == 1
        review = sample_record.reviews[0]
        assert review["reviewer"] == "John Doe"
        assert review["comments"] == "Looks good, approved"
        assert review["approved"] is True
        assert "timestamp" in review

    def test_multiple_reviews(self, sample_record):
        """Test adding multiple reviews."""
        sample_record.add_review("Reviewer1", "Approved", True)
        sample_record.add_review("Reviewer2", "Needs changes", False)
        sample_record.add_review("Reviewer3", "Final approval", True)

        assert len(sample_record.reviews) == 3
        assert sample_record.reviews[0]["reviewer"] == "Reviewer1"
        assert sample_record.reviews[1]["approved"] is False
        assert sample_record.reviews[2]["approved"] is True


# ============================================================================
# STATISTICS AND REPORTING TESTS
# ============================================================================


class TestStatistics:
    """Tests for statistics and reporting functionality."""

    def test_get_statistics_empty(self, architect):
        """Test statistics with no decisions."""
        stats = architect.get_statistics()

        assert stats["total"] == 0
        assert stats["by_status"] == {}
        assert stats["by_level"] == {}
        assert stats["recent"] == []

    def test_get_statistics_with_decisions(self, architect, sample_decision):
        """Test statistics with decisions."""
        architect.create_decision(title="Approved", description="Desc")
        approved = architect.decisions[list(architect.decisions.keys())[-1]]
        approved.approve()

        stats = architect.get_statistics()

        assert stats["total"] == 2
        assert stats["by_status"]["proposed"] == 1
        assert stats["by_status"]["accepted"] == 1
        assert stats["by_level"]["high"] == 1
        assert stats["by_level"]["medium"] == 1
        assert len(stats["recent"]) <= 5

    def test_get_statistics_by_level(self, architect):
        """Test statistics grouped by level."""
        architect.create_decision(title="Critical", description="Desc", level=DecisionLevel.CRITICAL)
        architect.create_decision(title="High", description="Desc", level=DecisionLevel.HIGH)
        architect.create_decision(title="High2", description="Desc", level=DecisionLevel.HIGH)
        architect.create_decision(title="Low", description="Desc", level=DecisionLevel.LOW)

        stats = architect.get_statistics()

        assert stats["by_level"]["critical"] == 1
        assert stats["by_level"]["high"] == 2
        assert stats["by_level"]["low"] == 1

    def test_get_pending_decisions(self, architect, sample_decision):
        """Test getting pending decisions."""
        approved = architect.create_decision(title="Approved", description="Desc")
        approved.approve()

        pending = architect.get_pending_decisions()

        assert sample_decision in pending
        assert approved not in pending
        assert all(d.status == DecisionStatus.PROPOSED for d in pending)

    def test_find_by_tag(self, architect, sample_decision):
        """Test finding decisions by tag."""
        tagged = architect.create_decision(title="Tagged", description="Desc", tags=["database"])
        untagged = architect.create_decision(title="Untagged", description="Desc")

        db_decisions = architect.find_by_tag("database")

        assert sample_decision in db_decisions
        assert tagged in db_decisions
        assert untagged not in db_decisions
        assert len(db_decisions) == 2


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    """Edge cases and error handling tests."""

    def test_empty_title(self, architect):
        """Test decision with empty title."""
        decision = architect.create_decision(title="", description="Desc")

        assert decision.title == ""
        assert decision.id is not None

    def test_very_long_description(self, architect):
        """Test decision with very long description."""
        long_desc = "A" * 10000
        decision = architect.create_decision(title="Test", description=long_desc)

        assert len(decision.description) == 10000

    def test_special_characters_in_title(self, architect):
        """Test decision with special characters."""
        decision = architect.create_decision(
            title="Test: Special @#$% Characters!",
            description="Desc",
        )

        assert "Special" in decision.title
        assert "@" in decision.title

    def test_unicode_in_fields(self, architect):
        """Test decision with Unicode characters."""
        decision = architect.create_decision(
            title="Тест на русском",
            description="Описание с эмодзи: 🚀",
            tags=["тест", "русский"],
        )

        assert "Тест" in decision.title
        assert "🚀" in decision.description
        assert "тест" in decision.tags

    def test_duplicate_tags(self, architect):
        """Test decision with duplicate tags."""
        decision = architect.create_decision(
            title="Test",
            description="Desc",
            tags=["tag1", "tag1", "tag2"],
        )

        # Tags are stored as provided (duplicates allowed)
        assert "tag1" in decision.tags
        assert len(decision.tags) >= 2

    def test_many_decisions(self, architect):
        """Test creating many decisions."""
        for i in range(100):
            architect.create_decision(title=f"Decision {i}", description="Desc")

        assert len(architect.decisions) == 100
        stats = architect.get_statistics()
        assert stats["total"] == 100

    def test_empty_tags_list(self, architect):
        """Test decision with empty tags list."""
        decision = architect.create_decision(title="Test", description="Desc", tags=[])

        assert decision.tags == []

    def test_none_tags(self, architect):
        """Test decision with None tags."""
        decision = architect.create_decision(title="Test", description="Desc", tags=None)

        assert decision.tags == []


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_decision_lifecycle(self, architect):
        """Test complete decision lifecycle."""
        # Create
        decision = architect.create_decision(
            title="Initial Decision",
            description="First version",
            level=DecisionLevel.MEDIUM,
            tags=["initial"],
        )
        assert decision.status == DecisionStatus.PROPOSED

        # Review and approve
        record = architect.records[decision.id]
        record.add_review("TechLead", "Approved after review", True)
        architect.approve_decision(decision.id)
        assert decision.status == DecisionStatus.ACCEPTED

        # Add evidence
        record.add_evidence("https://example.com/analysis")
        assert len(record.evidence) == 1

        # Later superseded
        new_decision = architect.create_decision(
            title="Updated Decision",
            description="New approach",
            tags=["updated"],
        )
        decision.supersede(new_decision.id)
        assert decision.status == DecisionStatus.SUPERSEDED

        # Verify statistics
        stats = architect.get_statistics()
        assert stats["total"] == 2
        assert stats["by_status"].get("accepted", 0) == 0  # Was superseded
        assert stats["by_status"]["superseded"] == 1

    def test_tag_based_filtering_workflow(self, architect):
        """Test workflow with tag-based filtering."""
        # Create decisions with various tags
        db_decision = architect.create_decision(
            title="Database Choice",
            description="PostgreSQL",
            tags=["database", "backend", "critical"],
        )
        api_decision = architect.create_decision(
            title="API Design",
            description="REST vs GraphQL",
            tags=["api", "backend"],
        )
        frontend_decision = architect.create_decision(
            title="Frontend Framework",
            description="React",
            tags=["frontend"],
        )

        # Filter by backend tag
        backend_decisions = architect.list_decisions(tag="backend")
        assert len(backend_decisions) == 2
        assert db_decision in backend_decisions
        assert api_decision in backend_decisions
        assert frontend_decision not in backend_decisions

        # Filter by database tag
        db_only = architect.list_decisions(tag="database")
        assert len(db_only) == 1
        assert db_decision in db_only

    def test_priority_based_review_workflow(self, architect):
        """Test workflow for prioritizing reviews."""
        # Create decisions with different priorities
        architect.create_decision(title="Critical", description="Desc", level=DecisionLevel.CRITICAL)
        architect.create_decision(title="High", description="Desc", level=DecisionLevel.HIGH)
        architect.create_decision(title="Medium", description="Desc", level=DecisionLevel.MEDIUM)
        architect.create_decision(title="Low", description="Desc", level=DecisionLevel.LOW)

        # Get critical decisions for immediate review
        critical = architect.list_decisions(level=DecisionLevel.CRITICAL)
        assert len(critical) == 1

        # Get all pending high/critical
        high_critical = [
            d for d in architect.get_pending_decisions()
            if d.level in [DecisionLevel.CRITICAL, DecisionLevel.HIGH]
        ]
        assert len(high_critical) == 2
