"""
Job Automation Agent
Поиск вакансий и генерация резюме с помощью AI
"""

import os
import asyncio
from typing import Dict, Any, List, Optional

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.language_models import FakeListLLM

# Настройка LLM
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        api_key=api_key, 
        temperature=0.1,
        max_retries=2
    )
    USE_MOCK = False
else:
    llm = FakeListLLM(responses=[
        "Найдено 5 вакансий Python разработчика.",
        "Резюме успешно сгенерировано.",
        "Требования проанализированы."
    ])
    USE_MOCK = True
    print("⚠️ OpenAI API key not found. Using mock responses.")

def job_search(query: str) -> str:
    """Поиск вакансий на hh.ru."""
    # TODO: Интеграция с реальным API hh.ru
    if USE_MOCK:
        return f"🔍 Найдено вакансии по запросу '{query}' (mock).\nПример: Senior Python Developer в Москве"
    
    # Здесь будет реальная логика
    return f"Результаты поиска по '{query}': реализация в разработке"

def generate_resume(job_title: str, skills: Optional[List[str]] = None) -> str:
    """Генерация резюме под конкретную вакансию."""
    if not skills:
        skills = ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]
    
    if USE_MOCK:
        return f"""
📄 *Резюме для позиции: {job_title}*

**Ключевые навыки:**
{', '.join(skills)}

**Опыт работы:**
• Senior Python Developer (2022-н.в.) - Разработка высоконагруженных API
• Python Developer (2019-2022) - Поддержка микросервисной архитектуры

**Образование:** МГТУ им. Баумана, Прикладная информатика

*Это демо-версия. Для реальной генерации установите OPENAI_API_KEY*
"""
    
    prompt = f"""
    Создай профессиональное резюме для позиции {job_title}.
    Ключевые навыки: {', '.join(skills)}.
    Опыт работы: 5+ лет в разработке.
    Формат: структурированное, 200-300 слов.
    """
    
    response = llm.invoke(prompt)
    return response.content

def analyze_requirements(job_description: str) -> Dict[str, Any]:
    """Анализ требований вакансии."""
    if USE_MOCK:
        return {
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            "experience_years": 3,
            "responsibilities": [
                "Разработка REST API",
                "Оптимизация запросов к БД",
                "Написание unit-тестов"
            ],
            "salary_range": "200 000 - 250 000 ₽"
        }
    
    prompt = f"""
    Проанализируй требования вакансии и верни JSON:
    {job_description[:1000]}
    
    Выдели: skills, experience_years, responsibilities, salary_range
    """
    
    response = llm.invoke(prompt)
    return {"analysis": response.content}

# Инструменты для агента
tools = [
    Tool(
        name="JobSearch", 
        func=job_search, 
        description="Поиск вакансий по ключевым словам"
    ),
    Tool(
        name="GenerateResume", 
        func=generate_resume, 
        description="Генерация резюме под вакансию. Вход: название позиции"
    ),
    Tool(
        name="AnalyzeRequirements", 
        func=analyze_requirements, 
        description="Анализ требований вакансии. Вход: текст вакансии"
    ),
]

# Создание агента
prompt_template = PromptTemplate.from_template("""
Ты - AI ассистент по поиску работы. Используй инструменты для помощи пользователю.

Доступные инструменты: {tools}

Вопрос пользователя: {input}

Ответ:
""")

if not USE_MOCK:
    agent = create_react_agent(llm, tools, prompt_template)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True
    )
else:
    agent_executor = None

async def process_request(query: str) -> Dict[str, Any]:
    """Обработка запроса пользователя."""
    if USE_MOCK or not agent_executor:
        # Mock response
        if "ваканс" in query.lower() or "поиск" in query.lower():
            return {
                "success": True,
                "result": job_search(query),
                "mock": True
            }
        elif "резюме" in query.lower():
            return {
                "success": True,
                "result": generate_resume("Python Developer"),
                "mock": True
            }
        else:
            return {
                "success": True,
                "result": "Я могу помочь с поиском вакансий, генерацией резюме и анализом требований. Что вас интересует?",
                "mock": True
            }
    
    try:
        result = await agent_executor.ainvoke({"input": query})
        return {
            "success": True,
            "result": result["output"],
            "mock": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mock": USE_MOCK
        }

# Синхронная обёртка для совместимости
def process_request_sync(query: str) -> Dict[str, Any]:
    """Синхронная версия обработки запроса."""
    return asyncio.run(process_request(query))

if __name__ == "__main__":
    # Тестирование
    print("🧪 Тестирование Job Agent...")
    
    result = process_request_sync("Найди вакансии Python разработчика")
    print(f"Результат: {result}")
    
    result = process_request_sync("Создай резюме для Senior Backend Developer")
    print(f"Результат: {result}")
