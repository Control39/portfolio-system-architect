from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    # Отношения
    skills = relationship("Skill", back_populates="user")
    progress_records = relationship("ProgressRecord", back_populates="user")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Отношения
    user = relationship("User", back_populates="skills")
    skill_markers = relationship("SkillMarker", back_populates="skill")


class CompetencyMarker(Base):
    __tablename__ = "competency_markers"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    required_level = Column(Integer, default=1)

    # Отношения
    skill_markers = relationship("SkillMarker", back_populates="marker")


class SkillMarker(Base):
    __tablename__ = "skill_markers"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    marker_id = Column(Integer, ForeignKey("competency_markers.id"), nullable=False)

    # Отношения
    skill = relationship("Skill", back_populates="skill_markers")
    marker = relationship("CompetencyMarker", back_populates="skill_markers")


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    date = Column(String(50))  # Формат: YYYY-MM-DD
    level_before = Column(Integer)
    level_after = Column(Integer)
    notes = Column(Text)

    # Отношения
    user = relationship("User", back_populates="progress_records")
    skill = relationship("Skill")
