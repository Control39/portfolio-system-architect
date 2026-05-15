"""Resume parsing and generation functionality."""

import asyncio
import os
import re
from dataclasses import dataclass

from jinja2 import BaseLoader, Environment, FileSystemLoader


@dataclass
class ParsedResume:
    """Результат парсинга резюме."""

    name: str | None = None
    position: str | None = None
    skills: list[str] | None = None
    experience: str | None = None
    email: str | None = None
    phone: str | None = None


class ResumeParser:
    """Парсер резюме."""

    def __init__(self):
        """Инициализация парсера."""
        self._common_skills = {
            "python",
            "javascript",
            "java",
            "go",
            "rust",
            "typescript",
            "fastapi",
            "django",
            "flask",
            "react",
            "vue",
            "angular",
            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "aws",
            "gcp",
            "azure",
            "git",
            "ci/cd",
            "linux",
        }

    def parse(self, text: str) -> ParsedResume:
        """Парсинг текста резюме."""
        if not text or not text.strip():
            return ParsedResume(skills=[])

        lines = text.strip().split("\n")
        name = lines[0].strip() if lines else None

        position = None
        skills = []
        experience = None

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Позиция (обычно после имени)
            if position is None and ("разработчик" in line.lower() or "developer" in line.lower()):
                position = line
                continue

            # Опыт
            if "опыт" in line.lower() or "experience" in line.lower():
                experience = line
                continue

            # Навыки (строки с запятыми)
            if "," in line:
                extracted = self.extract_skills(line)
                skills.extend(extracted)

        # Извлекаем навыки из текста
        if not skills:
            skills = self.extract_skills(text)

        return ParsedResume(
            name=name,
            position=position,
            skills=skills if skills else [],
            experience=experience,
        )

    def extract_skills(self, text: str) -> list[str]:
        """Извлечение навыков из текста."""
        text_lower = text.lower()
        found_skills = []

        for skill in self._common_skills:
            if skill in text_lower:
                # Сохраняем оригинальный регистр
                pattern = re.compile(re.escape(skill), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    found_skills.append(match.group())

        return found_skills

    def extract_skills_from_list(self, skills_list: list[str]) -> list[str]:
        """Извлечение навыков из списка."""
        result = []
        for skill in skills_list:
            skill_lower = skill.lower()
            if skill_lower in self._common_skills:
                result.append(skill)
        return result


# Template dir with check
template_dir = os.path.join(os.path.dirname(__file__), "../../templates")
if os.path.exists(template_dir):
    env = Environment(
        loader=FileSystemLoader(template_dir), block_start_string="[%", block_end_string="%]", autoescape=True
    )
else:
    env = Environment(loader=BaseLoader(), autoescape=True)  # Fallback empty
    print("Warning: templates not found, using fallback.")


async def generate_resume(profile: dict, job_description: dict) -> str:
    """Генерирует резюме на основе профиля и описания вакансии."""
    try:
        template = env.get_template("resume.md.j2")
        return template.render(profile=profile, job=job_description, generated_at=os.path.abspath(__file__))
    except Exception as e:
        print(f"Ошибка генерации резюме: {e}")
        # Fallback simple resume
        return f"""# Резюме для {profile.get("name", "Кандидат")}

## Навыки
{", ".join(profile.get("skills", []))}

## Опыт
{profile.get("experience", "Не указан")}

## Подходит для вакансии
{job_description.get("title", "Не указано")}
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
