"""
Tests for career_development db.py (ORM layer)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent.parent / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestDBModels:
    """Tests for SQLAlchemy ORM models"""

    @patch("apps.career_development.src.core.db.create_async_engine")
    def test_engine_creation(self, mock_engine):
        """Test that async engine is created correctly"""
        mock_engine.return_value = MagicMock()
        from apps.career_development.src.core import db
        assert db.engine is not None
        mock_engine.assert_called_once()

    def test_base_class(self):
        """Test that Base is a DeclarativeBase"""
        from apps.career_development.src.core.db import Base
        from sqlalchemy.orm import DeclarativeBase
        assert issubclass(Base, DeclarativeBase)

    def test_competency_marker_orm(self):
        """Test CompetencyMarkerORM table structure"""
        from apps.career_development.src.core.db import CompetencyMarkerORM
        assert CompetencyMarkerORM.__tablename__ == "competency_markers"
        assert hasattr(CompetencyMarkerORM, "id")
        assert hasattr(CompetencyMarkerORM, "title")
        assert hasattr(CompetencyMarkerORM, "status")
        assert hasattr(CompetencyMarkerORM, "evidence_url")
        assert hasattr(CompetencyMarkerORM, "created_at")

    def test_skill_orm(self):
        """Test SkillORM table structure"""
        from apps.career_development.src.core.db import SkillORM
        assert SkillORM.__tablename__ == "skills"
        assert hasattr(SkillORM, "id")
        assert hasattr(SkillORM, "name")
        assert hasattr(SkillORM, "level")
        assert hasattr(SkillORM, "created_at")


class TestDBFunctions:
    """Tests for database functions"""

    @patch("apps.career_development.src.core.db.AsyncSessionLocal")
    def test_get_db(self, mock_session_maker):
        """Test get_db dependency"""
        from apps.career_development.src.core.db import get_db

        mock_session = AsyncMock()
        mock_session_maker.return_value = mock_session

        gen = get_db()
        session = next(gen)

        assert session == mock_session
        mock_session.commit.assert_called_once()

    def test_get_db_rollback_on_error(self):
        """Test that get_db rolls back on error"""
        from apps.career_development.src.core.db import get_db
        from unittest.mock import AsyncMock

        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("DB error")

        with patch("apps.career_development.src.core.db.AsyncSessionLocal", return_value=mock_session):
            gen = get_db()
            with pytest.raises(Exception):
                next(gen)
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    @patch("apps.career_development.src.core.db.AsyncSessionLocal")
    def test_pydantic_to_orm(self, mock_session_maker):
        """Test pydantic_to_orm conversion"""
        from apps.career_development.src.core.db import pydantic_to_orm
        from src.shared.pydantic.career import UserProfile, Skill

        # Create mock profile
        profile = UserProfile(
            username="test_user",
            email="test@example.com",
            skills=[Skill(name="Python", level=5)],
            experience_years=5,
        )

        mock_session = AsyncMock()

        result = pydantic_to_orm(profile, mock_session)
        assert result is None  # Function returns None currently

    @patch("apps.career_development.src.core.db.engine")
    @patch("apps.career_development.src.core.db.Base.metadata")
    def test_init_db(self, mock_metadata, mock_engine):
        """Test init_db function"""
        from apps.career_development.src.core.db import init_db
        import asyncio

        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn

        asyncio.run(init_db())
        mock_conn.run_sync.assert_called_once_with(mock_metadata.create_all)
