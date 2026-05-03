import asyncio
import os
from typing import Dict

from jinja2 import BaseLoader, Environment, FileSystemLoader

# Template dir with check
template_dir = os.path.join(os.path.dirname(__file__), "../../templates")
if os.path.exists(template_dir):
    env = Environment(
        loader=FileSystemLoader(template_dir), block_start_string="[%", block_end_string="%]"
    )
else:
    env = Environment(loader=BaseLoader())  # Fallback empty
    print("Warning: templates not found, using fallback.")


async def generate_resume(profile: Dict, job_description: Dict) -> str:
    """Генерирует резюме на основе профиля и описания вакансии."""
    try:
        template = env.get_template("resume.md.j2")
        rendered = template.render(
            profile=profile, job=job_description, generated_at=os.path.abspath(__file__)
        )
        return rendered
    except Exception as e:
        print(f"Ошибка генерации резюме: {e}")
        # Fallback simple resume
        return f"""# Резюме для {profile.get('name', 'Кандидат')}

## Навыки
{', '.join(profile.get('skills', []))}

## Опыт
{profile.get('experience', 'Не указан')}

## Подходит для вакансии
{job_description.get('title', 'Не указано')}
"""


async def generate_resume_from_job_title(job_title: str, skills: str = "") -> str:
    """Упрощённая генерация резюме по названию должности."""
    profile = {
        "name": "Кандидат",
        "skills": skills.split(",") if skills else ["Python", "FastAPI", "PostgreSQL"],
        "experience": "5+ лет разработки",
    }
    job = {"title": job_title, "description": "Требуется специалист."}
    return await generate_resume(profile, job)


if __name__ == "__main__":
    # Тестовый запуск
    test_profile = {
        "name": "Иван Иванов",
        "skills": ["Python", "Django", "Docker"],
        "experience": "3 года backend-разработки",
    }
    test_job = {"title": "Python разработчик", "description": "Разработка веб-приложений"}
    result = asyncio.run(generate_resume(test_profile, test_job))
    print(result[:200])
