import os

from langchain_core.language_models import FakeListLLM  # Fallback
from langchain_openai import ChatOpenAI

# LLM with env var (fallback mock)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.1)
else:
    llm = FakeListLLM(responses=["Mock response for dry-run"])

# Tools
def job_search(query: str) -> str:
    """Ищет вакансии на hh.ru."""
    return f"Найдено вакансии по '{query}' на hh.ru."

def generate_resume(job_title: str) -> str:
    """Генерирует резюме для указанной должности."""
    return f"Резюме для должности {job_title} сгенерировано."

async def analyze_career_progress(user_id: str) -> dict:
    """Анализирует карьерный прогресс пользователя."""
    return {"user_id": user_id, "progress": 0.0, "recommendations": []}



