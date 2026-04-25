


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
    async with get_db() as session:
        skills_df


