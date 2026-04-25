import asyncio
import os
from typing import Any

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

def generate_resume(job_title: str, profile: dict[str, Any], job_description: str) -> str:
    """Generates a resume for a given job title."""
    # Call the async resume generator
    return asyncio.run(resume_agent.generate_resume(profile, job_description))


