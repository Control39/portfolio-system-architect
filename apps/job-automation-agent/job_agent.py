"""
Job Automation Agent
Поиск вакансий и генерация резюме с помощью AI
"""

import asyncio
import os
from typing import Any, Dict, List, Optional, Set

from langchain_core.language_models import FakeListLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# LangChain imports
from langchainapps.cognitive_agent.factory import create_agent

# Импорт компонентов для интеграции с системой отслеживания карьеры
from apps.it_compass.src.core.tracker import CareerTracker
from apps.it_compass.src.utils.marker_export import MarkerExporter

# Настройка LLM
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.1, max_retries=2)
    USE_MOCK = False
else:
    llm = FakeListLLM(
        responses=[
            "Найдено 5 вакансий Python разработчика.",
            "Резюме успешно сгенерировано.",
            "Требования проанализированы.",
        ]
    )
    USE_MOCK = True
    print("⚠️ OpenAI API key not found. Using mock responses.")

# Инициализация компонентов отслеживания карьеры
try:
    career_tracker = CareerTracker()
    marker_exporter = MarkerExporter(career_tracker)
    INTEGRATION_ENABLED = True
    print("✅ Интеграция с системой отслеживания карьеры активирована")
except Exception as e:
    print(f"❌ Ошибка инициализации системы отслеживания карьеры: {e}")
    INTEGRATION_ENABLED = False
    career_tracker = None
    marker_exporter = None


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
{", ".join(skills)}

**Опыт работы:**
• Senior Python Developer (2022-н.в.) - Разработка высоконагруженных API
• Python Developer (2019-2022) - Поддержка микросервисной архитектуры

**Образование:** МГТУ им. Баумана, Прикладная информатика

*Это демо-версия. Для реальной генерации установите OPENAI_API_KEY*
"""

    prompt = f"""
    Создай профессиональное резюме для позиции {job_title}.
    Ключевые навыки: {", ".join(skills)}.
    Опыт работы: 5+ лет в разработке.
    Формат: структурированное, 200-300 слов.
    """

    response = llm.invoke(prompt)
    return response.content


def _find_matching_markers(skills: List[str]) -> Set[str]:
    """Поиск маркеров компетенций, соответствующих указанным навыкам.

    Args:
        skills: Список навыков из анализа вакансии

    Returns:
        Множество ID найденных маркеров
    """
    if not INTEGRATION_ENABLED:
        return set()

    matching_markers = set()
    skill_lower = [skill.lower() for skill in skills]

    try:
        # Поиск маркеров, соответствующих навыкам
        for skill_name, skill_data in career_tracker.markers.items():
            for _level_name, level_markers in skill_data.levels.items():
                for marker in level_markers:
                    # Проверяем соответствие по навыку
                    if skill_name.lower() in skill_lower:
                        matching_markers.add(marker.id)
                        continue

                    # Проверяем соответствие по ресурсам маркера
                    for resource in marker.resources:
                        for skill in skills:
                            if skill.lower() in resource.lower():
                                matching_markers.add(marker.id)
                                break
                        if marker.id in matching_markers:
                            break

                    # Проверяем соответствие по описанию маркера
                    if marker.id not in matching_markers:  # Избегаем дубликатов
                        marker_text = f"{marker.marker} {marker.validation}".lower()
                        for skill in skills:
                            if skill.lower() in marker_text:
                                matching_markers.add(marker.id)
                                break
    except Exception as e:
        print(f"Ошибка при поиске соответствующих маркеров: {e}")

    return matching_markers


def _auto_mark_completed(marker_ids: Set[str]) -> Dict[str, Any]:
    """Автоматически отмечает найденные маркеры как выполненные.

    Args:
        marker_ids: Множество ID маркеров для отметки

    Returns:
        Статистика по проставленным маркерам
    """
    if not INTEGRATION_ENABLED or not marker_ids:
        return {"marked": 0, "failed": 0, "total": 0}

    results = {"marked": 0, "failed": 0, "total": len(marker_ids)}

    for marker_id in marker_ids:
        try:
            success = career_tracker.mark_completed(marker_id)
            if success:
                results["marked"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"Ошибка при проставлении маркера {marker_id}: {e}")
            results["failed"] += 1

    return results


def analyze_requirements(job_description: str) -> Dict[str, Any]:
    """Анализ требований вакансии с интеграцией системы отслеживания карьеры."""
    if USE_MOCK:
        analysis_result = {
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            "experience_years": 3,
            "responsibilities": [
                "Разработка REST API",
                "Оптимизация запросов к БД",
                "Написание unit-тестов",
            ],
            "salary_range": "200 000 - 250 000 ₽",
        }
    else:
        prompt = f"""
        Проанализируй требования вакансии и верни JSON:
        {job_description[:1000]}

        Выдели: skills, experience_years, responsibilities, salary_range
        """

        response = llm.invoke(prompt)
        try:
            analysis_result = json.loads(response.content)
        except:
            analysis_result = {
                "skills": [],
                "experience_years": 0,
                "responsibilities": [],
                "salary_range": "Не указано",
            }

    # Интеграция с системой отслеживания карьеры
    if INTEGRATION_ENABLED and analysis_result.get("skills"):
        print(
            f"🔍 Поиск соответствующих маркеров для навыков: {', '.join(analysis_result['skills'])}"
        )

        # Поиск маркеров, соответствующих требованиям вакансии
        matching_markers = _find_matching_markers(analysis_result["skills"])

        if matching_markers:
            print(f"🎯 Найдено {len(matching_markers)} соответствующих маркеров компетенций")

            # Автоматическое проставление отметок о выполнении
            mark_results = _auto_mark_completed(matching_markers)

            print(f"✅ Автоматически отмечено {mark_results['marked']} маркеров как выполненные")
            if mark_results["failed"] > 0:
                print(f"⚠️ Не удалось отметить {mark_results['failed']} маркеров")

            # Добавляем информацию об интеграции в результат
            analysis_result["career_integration"] = {
                "matched_markers_count": len(matching_markers),
                "marked_as_completed": mark_results["marked"],
                "failed_to_mark": mark_results["failed"],
                "matched_marker_ids": list(matching_markers),
            }
        else:
            print("ℹ️ Соответствующие маркеры компетенций не найдены")

    return analysis_result


# Инструменты для агента
tools = [
    Tool(
        name="JobSearch",
        func=job_search,
        description="Поиск вакансий по ключевым словам",
    ),
    Tool(
        name="GenerateResume",
        func=generate_resume,
        description="Генерация резюме под вакансию. Вход: название позиции",
    ),
    Tool(
        name="AnalyzeRequirements",
        func=analyze_requirements,
        description="Анализ требований вакансии. Вход: текст вакансии",
    ),
]

# Создание агента
prompt_template = PromptTemplate.from_template(
    """
Ты - AI ассистент по поиску работы. Используй инструменты для помощи пользователю.

Доступные инструменты: {tools}

Вопрос пользователя: {input}

Ответ:
"""
)

if not USE_MOCK:
    agent = create_agent(llm=llm, tools=tools, prompt=prompt_template)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True,
    )
else:
    agent_executor = None


async def process_request(query: str) -> Dict[str, Any]:
    """Обработка запроса пользователя."""
    if USE_MOCK or not agent_executor:
        # Mock response
        if "ваканс" in query.lower() or "поиск" in query.lower():
            return {"success": True, "result": job_search(query), "mock": True}
        elif "резюме" in query.lower():
            return {
                "success": True,
                "result": generate_resume("Python Developer"),
                "mock": True,
            }
        else:
            return {
                "success": True,
                "result": "Я могу помочь с поиском вакансий, генерацией резюме и анализом требований. Что вас интересует?",
                "mock": True,
            }

    try:
        result = await agent_executor.ainvoke({"input": query})
        return {"success": True, "result": result["output"], "mock": False}
    except Exception as e:
        return {"success": False, "error": str(e), "mock": USE_MOCK}


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
