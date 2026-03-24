import asyncio
import os
from typing import Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.language_models import FakeListLLM  # Fallback

# LLM with env var (fallback mock)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.1)
else:
    llm = FakeListLLM(responses=["Mock response for dry-run"])

# Tools
def job_search(query: str) -> str:
    \"\"\"Ищет вакансии на hh.ru.\"\"\" 
    return f\"Найдено вакансии по '{query}' на hh.ru.\"

def generate_resume(job_title
