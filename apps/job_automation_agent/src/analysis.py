"""Job analysis and matching functionality."""

from dataclasses import dataclass
from typing import Any


@dataclass
class JobAnalysis:
    """Результат анализа вакансии."""

    job_id: str | None = None
    position: str | None = None
    employer: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    url: str | None = None


@dataclass
class MatchScore:
    """Результат оценки совпадения резюме и вакансии."""

    match_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    experience_match: bool


class JobAnalyzer:
    """Анализатор вакансий и резюме."""

    def __init__(self):
        """Инициализация анализатора."""
        self._job_cache: dict[str, dict[str, Any]] = {}

    def analyze_job(self, job: dict[str, Any]) -> "JobAnalysis":
        """Анализ вакансии."""
        if not job:
            return JobAnalysis()

        return JobAnalysis(
            job_id=job.get("id"),
            position=job.get("name"),
            employer=job.get("employer"),
            salary_from=job.get("salary", {}).get("from") if job.get("salary") else None,
            salary_to=job.get("salary", {}).get("to") if job.get("salary") else None,
            url=job.get("url"),
        )

    def match_resume_to_job(self, resume: dict[str, Any], job: dict[str, Any]) -> MatchScore:
        """Сопоставление резюме и вакансии."""
        resume_skills = set(resume.get("skills", []))
        required_skills = set(job.get("required_skills", []))

        if not required_skills:
            return MatchScore(
                match_percentage=100.0,
                matched_skills=list(resume_skills),
                missing_skills=[],
                experience_match=True,
            )

        matched = resume_skills & required_skills
        missing = required_skills - resume_skills

        match_percentage = (len(matched) / len(required_skills)) * 100

        return MatchScore(
            match_percentage=match_percentage,
            matched_skills=list(matched),
            missing_skills=list(missing),
            experience_match=resume.get("experience_years", 0) >= 1,
        )

    def analyze_market_trends(self, jobs: list[dict[str, Any]]) -> dict[str, Any]:
        """Анализ рыночных трендов."""
        if not jobs:
            return {"average_salary": None, "total_jobs": 0}

        salaries = [
            j.get("salary", {}).get("from", 0)
            for j in jobs
            if j.get("salary") and j.get("salary", {}).get("from")
        ]

        avg_salary = sum(salaries) / len(salaries) if salaries else None

        return {
            "average_salary": avg_salary,
            "total_jobs": len(jobs),
            "max_salary": max(salaries) if salaries else None,
            "min_salary": min(salaries) if salaries else None,
        }


def compute_match_score(resume_skills: set[str], required_skills: set[str]) -> float:
    """Вычисление балла совпадения навыков."""
    if not required_skills:
        return 100.0

    matched = resume_skills & required_skills
    return (len(matched) / len(required_skills)) * 100


# Mock DB import (no crash)
class MockDBSession:
    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        pass


async def get_db():
    yield MockDBSession()


async def analyze_career_progress(user_id: str) -> dict:
    """Analysis Agent."""
    async with get_db():
        import pandas as pd

        pd.DataFrame()
        return {"status": "ok", "user_id": user_id}
