from typing import Dict

import pandas as pd


# Mock DB import (no crash)
class MockDBSession:
    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        pass


async def get_db():
    yield MockDBSession()


async def analyze_career_progress(user_id: str) -> Dict:
    """Analysis Agent."""
    async with get_db():
        pd.DataFrame()
        return {"status": "ok", "user_id": user_id}
