"""
Async SQLAlchemy ORM for Career Development System
Connects shared Pydantic schemas → PostgreSQL
"""
import asyncio
import os
from typing import List
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, JSON
from src.shared.pydantic.career import (
    CompetencyMarker, Skill, UserProfile
)

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://architect:arch_pass_2024@localhost:5432/portfolio_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    __abstract__ = True
    metadata = None

class CompetencyMarkerORM(Base):
    __tablename__ = "competency_markers"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    evidence_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class SkillORM(Base):
    __tablename__ = "skills"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def pydantic_to_orm(profile: UserProfile, session: AsyncSession):
    """Convert Pydantic → ORM + save"""
    # Simplified - full impl in service layer
    orm_profile = {
        "username": profile.username,
        "skills": [skill.dict() for skill in profile.skills],
        # ... persist JSONB
    }
    # session.add(...)
    pass

# Init tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())

