"""
Synchronous database configuration for Alembic migrations
"""

import os

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://architect:arch_pass_2024@localhost:5432/portfolio_db",
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class CompetencyMarkerORM(Base):
    __tablename__ = "competency_markers"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    evidence_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class SkillORM(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class UserProfilesORM(Base):
    __tablename__ = "user_profiles"

    username = Column(String, primary_key=True)
    skills = Column(JSON, default=list, nullable=False)
    goals = Column(JSON, default=list, nullable=False)
    achievements = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class ProgressRecordORM(Base):
    __tablename__ = "progress_records"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.username"), nullable=False)
    skill_name = Column(String, nullable=False)
    level_before = Column(Integer, nullable=False)
    level_after = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=text("now()"))
    notes = Column(String, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Для Alembic
__all__ = [
    "Base",
    "engine",
    "CompetencyMarkerORM",
    "SkillORM",
    "UserProfilesORM",
    "ProgressRecordORM",
]
