import asyncio
from typing import Dict

import pandas as pd


# Mock DB import (no crash)
class MockDBSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


async def get_db():
    yield MockDBSession()


async def analyze_career_progress(user_id: str) -> Dict:
    """Analysis Agent."""
    async with get_db() as session:
        # Placeholder analysis
        skills_df = pd.DataFrame({"skill": ["Python", "FastAPI"], "level": [5, 4]})
        return {
            "user_id": user_id,
            "skill_count": len(skills_df),
            "avg_level": skills_df["level"].mean(),
        }