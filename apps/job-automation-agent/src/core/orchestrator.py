import asyncio
import os
from typing import Any, Dict

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
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


def generate_resume(job_title: str, skills: str = "") -> str:
    """Генерирует резюме под указанную должность."""
    return f"Сгенерировано резюме для '{job_title}' с навыками: {skills}"


tools = [
    Tool(name="job_search", func=job_search, description="Поиск вакансий на hh.ru по запросу"),
    Tool(
        name="generate_resume",
        func=generate_resume,
        description="Генерация резюме под указанную должность",
    ),
]

# Prompt template
prompt = PromptTemplate.from_template(
    """
Ты — агент автоматизации поиска работы. У тебя есть доступ к следующим инструментам:

{tools}

Используй инструменты, чтобы помочь пользователю найти вакансии и сгенерировать резюме.

Вопрос: {input}
"""
)

# Create agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


async def run_agent(task: str) -> Dict[str, Any]:
    """Запуск агента с задачей."""
    result = await agent_executor.ainvoke({"input": task})
    return result


if __name__ == "__main__":
    # Пример запуска
    sample_task = "Найди вакансии Python разработчика и сгенерируй резюме"
    result = asyncio.run(run_agent(sample_task))
    print(result)
