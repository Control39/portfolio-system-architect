"""
Tests for career_development db.py (ORM layer) - Fully mocked
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_db_dependencies():
    """Mock all SQLAlchemy dependencies before importing db"""
    # Mock SQLAlchemy modules
    mock_sqlalchemy = MagicMock()
    mock_sqlalchemy.DateTime = MagicMock()
    mock_sqlalchemy.Integer = MagicMock()
    mock_sqlalchemy.String = MagicMock()
    mock_sqlalchemy.func = MagicMock()

    mock_asyncio = MagicMock()
    mock_asyncio.AsyncSession = MagicMock()
    mock_asyncio.async_sessionmaker = MagicMock()
    mock_asyncio.create_async_engine = MagicMock(return_value=MagicMock())

    mock_orm = MagicMock()
    mock_orm.DeclarativeBase = MagicMock()
    mock_orm.Mapped = MagicMock()
    mock_orm.mapped_column = MagicMock()

    # Patch sys.modules temporarily
    original_modules = sys.modules.copy()

    with patch.dict(
        "sys.modules",
        {
            "sqlalchemy": mock_sqlalchemy,
            "sqlalchemy.ext": MagicMock(),
            "sqlalchemy.ext.asyncio": mock_asyncio,
            "sqlalchemy.orm": mock_orm,
        },
    ):
        # Force reimport
        modules_to_remove = [k for k in sys.modules if "career_development.src.core" in k]
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]

        from apps.career_development.src.core import db

        yield db

        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


class TestDBModels:
    """Tests for SQLAlchemy ORM models"""

    def test_base_class_exists(self, mock_db_dependencies):
        """Test that Base class exists in module"""
        assert hasattr(mock_db_dependencies, "Base")

    def test_competency_marker_orm_exists(self, mock_db_dependencies):
        """Test CompetencyMarkerORM table exists"""
        assert hasattr(mock_db_dependencies, "CompetencyMarkerORM")

    def test_skill_orm_exists(self, mock_db_dependencies):
        """Test SkillORM table exists"""
        assert hasattr(mock_db_dependencies, "SkillORM")

    def test_engine_exists(self, mock_db_dependencies):
        """Test that engine is defined"""
        assert hasattr(mock_db_dependencies, "engine")

    def test_get_db_function_exists(self, mock_db_dependencies):
        """Test get_db function exists"""
        assert hasattr(mock_db_dependencies, "get_db")
        assert callable(mock_db_dependencies.get_db)

    def test_pydantic_to_orm_function_exists(self, mock_db_dependencies):
        """Test pydantic_to_orm function exists"""
        assert hasattr(mock_db_dependencies, "pydantic_to_orm")
        assert callable(mock_db_dependencies.pydantic_to_orm)

    def test_init_db_function_exists(self, mock_db_dependencies):
        """Test init_db function exists"""
        assert hasattr(mock_db_dependencies, "init_db")
        assert callable(mock_db_dependencies.init_db)


class TestDBFunctions:
    """Tests for database functions - mocked"""

    def test_get_db_returns_generator(self, mock_db_dependencies):
        """Test get_db is an async generator function"""
        import inspect

        assert inspect.isasyncgenfunction(mock_db_dependencies.get_db)

    @pytest.mark.asyncio
    async def test_pydantic_to_orm_placeholder(self, mock_db_dependencies):
        """Test pydantic_to_orm is a placeholder"""
        mock_profile = MagicMock()
        mock_session = MagicMock()

        result = await mock_db_dependencies.pydantic_to_orm(mock_profile, mock_session)
        assert result is None  # Currently a placeholder
