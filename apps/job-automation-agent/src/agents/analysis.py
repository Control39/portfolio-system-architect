

# Mock DB import (no crash)
class MockDBSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

def get_db():
    return MockDBSession()

async def analyze_career_progress(user_id: str) -> dict:
    """Analysis Agent."""
    # Используем мок-сессию напрямую
    session = MockDBSession()
    # Здесь будет логика анализа прогресса
    return {
        "user_id": user_id,
        "progress": 0.0,
        "recommendations": [],
    }

