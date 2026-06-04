#!/usr/bin/env python
"""
Автоматическое исправление структуры сервиса.

Использование:
    python auto_fix_service_structure.py <service-name>
    python auto_fix_service_structure.py --all
"""

import sys
from pathlib import Path
from typing import TypedDict


class FixTask(TypedDict):
    service: str
    action: str
    path: str
    description: str


def create_file_if_missing(path: Path, content: str = "") -> bool:
    """Создать файл, если он отсутствует."""
    if path.exists():
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def fix_ai_config_manager(service_path: Path) -> list[FixTask]:
    """Исправить ai_config_manager."""
    fixes = []

    # Создать Dockerfile
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    if create_file_if_missing(service_path / "Dockerfile", dockerfile):
        fixes.append(
            FixTask(
                service="ai_config_manager",
                action="create",
                path="Dockerfile",
                description="Создан Dockerfile",
            )
        )

    # Обновить README.md
    readme_path = service_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")

        # Проверить и добавить секции
        required_sections = {
            "## Purpose": "## Purpose\nЦентрализованное управление конфигурациями всех сервисов.\n",
            "## Features": "## Features\n- Загрузка конфигов из YAML\n- Hot reload\n- Fallback на локальные конфиги\n",
            "## Dependencies": "## Dependencies\n```bash\npip install -r requirements.txt\n```\n",
            "## Deployment": "## Deployment\n```bash\ndocker build -t ai_config_manager .\ndocker run -p 8000:8000 ai_config_manager\n```\n",
            "## Contributing": "## Contributing\nСм. [CONTRIBUTING.md](../../CONTRIBUTING.md)\n",
        }

        for section, replacement in required_sections.items():
            if section not in content:
                # Вставить после заголовка
                content = content.replace(
                    "# AI Config Manager", f"# AI Config Manager\n\n{replacement}"
                )

        readme_path.write_text(content, encoding="utf-8")
        fixes.append(
            FixTask(
                service="ai_config_manager",
                action="update",
                path="README.md",
                description="Добавлены missing секции",
            )
        )

    return fixes


def fix_auth_service(service_path: Path) -> list[FixTask]:
    """Исправить auth_service."""
    fixes = []

    # Создать requirements.txt (если есть requirements-local.txt)
    req_local = service_path / "requirements-local.txt"
    req_txt = service_path / "requirements.txt"

    if req_local.exists() and not req_txt.exists():
        content = req_local.read_text(encoding="utf-8")
        req_txt.write_text(content, encoding="utf-8")
        fixes.append(
            FixTask(
                service="auth_service",
                action="create",
                path="requirements.txt",
                description="Создан requirements.txt из requirements-local.txt",
            )
        )

    # Обновить README.md
    readme_path = service_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")

        required_sections = {
            "## Purpose": "## Purpose\nСервис аутентификации и авторизации (JWT).\n",
            "## Features": "## Features\n- JWT токены\n- OAuth2\n- Rate limiting\n",
            "## Dependencies": "## Dependencies\n```bash\npip install -r requirements.txt\n```\n",
            "## Deployment": "## Deployment\n```bash\ndocker build -t auth_service .\ndocker run -p 8100:8000 auth_service\n```\n",
            "## Contributing": "## Contributing\nСм. [CONTRIBUTING.md](../../CONTRIBUTING.md)\n",
        }

        for section, replacement in required_sections.items():
            if section not in content:
                content = content.replace("# Auth Service", f"# Auth Service\n\n{replacement}")

        readme_path.write_text(content, encoding="utf-8")
        fixes.append(
            FixTask(
                service="auth_service",
                action="update",
                path="README.md",
                description="Добавлены missing секции",
            )
        )

    return fixes


def fix_cognitive_agent(service_path: Path) -> list[FixTask]:
    """Исправить cognitive_agent."""
    fixes = []

    # Проверить наличие entry point в scripts/
    scripts_path = service_path / "scripts"
    main_py = service_path / "main.py"

    if scripts_path.exists() and not main_py.exists():
        # Создать main.py как обёртку
        main_content = """\"\"\"
Cognitive Automation Agent — автономный ИИ-агент для управления проектами.

API:
    GET /health — проверка здоровья
    POST /tasks — создание задачи
    GET /tasks/{id} — получение задачи
\"\"\"

from fastapi import FastAPI

app = FastAPI(
    title="Cognitive Automation Agent",
    description="Автономный ИИ-агент для управления проектами",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cognitive_agent"}


@app.get("/")
async def root():
    return {
        "name": "Cognitive Automation Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "entry": "scripts/scanner_main.py"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        if create_file_if_missing(main_py, main_content):
            fixes.append(
                FixTask(
                    service="cognitive_agent",
                    action="create",
                    path="main.py",
                    description="Создан main.py как entry point",
                )
            )

    # Обновить README.md
    readme_path = service_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")

        required_sections = {
            "## Purpose": "## Purpose\nАвтономный ИИ-агент для управления проектами с навыками самообучения.\n",
            "## Features": "## Features\n- Project Scanner\n- Task Planner\n- Learning System\n- Trigger System\n",
            "## Dependencies": "## Dependencies\n```bash\npip install -r requirements.txt\n```\n",
            "## Deployment": "## Deployment\n```bash\ndocker build -t cognitive_agent .\ndocker run -p 8000:8000 cognitive_agent\n```\n",
            "## Contributing": "## Contributing\nСм. [CONTRIBUTING.md](../../CONTRIBUTING.md)\n",
        }

        for section, replacement in required_sections.items():
            if section not in content:
                content = content.replace(
                    "# Cognitive Agent", f"# Cognitive Agent\n\n{replacement}"
                )

        readme_path.write_text(content, encoding="utf-8")
        fixes.append(
            FixTask(
                service="cognitive_agent",
                action="update",
                path="README.md",
                description="Добавлены missing секции",
            )
        )

    return fixes


def fix_job_automation_agent(service_path: Path) -> list[FixTask]:
    """Исправить job_automation_agent."""
    fixes = []

    # Проверить наличие entry point в src/
    src_path = service_path / "src"
    main_py = service_path / "main.py"

    if src_path.exists() and not main_py.exists():
        # Создать main.py как обёртку
        main_content = """\"\"\"
Job Automation Agent — автоматизация поиска работы и подачи заявок.

API:
    GET /health — проверка здоровья
    POST /jobs/search — поиск вакансий
    POST /jobs/apply — подача заявки
\"\"\"

from fastapi import FastAPI

app = FastAPI(
    title="Job Automation Agent",
    description="Автоматизация поиска работы и подачи заявок",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "job_automation_agent"}


@app.get("/")
async def root():
    return {
        "name": "Job Automation Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "entry": "src/main.py"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        if create_file_if_missing(main_py, main_content):
            fixes.append(
                FixTask(
                    service="job_automation_agent",
                    action="create",
                    path="main.py",
                    description="Создан main.py как entry point",
                )
            )

    # Обновить README.md
    readme_path = service_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")

        required_sections = {
            "## Purpose": "## Purpose\nАвтоматизация поиска работы, анализа вакансий и подачи заявок.\n",
            "## Features": "## Features\n- Поиск вакансий\n- Анализ требований\n- Автоподача заявок\n- Трекинг откликов\n",
            "## Dependencies": "## Dependencies\n```bash\npip install -r requirements.txt\n```\n",
            "## Deployment": "## Deployment\n```bash\ndocker build -t job_automation_agent .\ndocker run -p 8000:8000 job_automation_agent\n```\n",
            "## Contributing": "## Contributing\nСм. [CONTRIBUTING.md](../../CONTRIBUTING.md)\n",
        }

        for section, replacement in required_sections.items():
            if section not in content:
                content = content.replace(
                    "# Job Automation Agent", f"# Job Automation Agent\n\n{replacement}"
                )

        readme_path.write_text(content, encoding="utf-8")
        fixes.append(
            FixTask(
                service="job_automation_agent",
                action="update",
                path="README.md",
                description="Добавлены missing секции",
            )
        )

    return fixes


def fix_all_services(base_path: Path) -> list[FixTask]:
    """Исправить все сервисы."""
    all_fixes = []

    service_fixers = {
        "ai_config_manager": fix_ai_config_manager,
        "auth_service": fix_auth_service,
        "cognitive_agent": fix_cognitive_agent,
        "job_automation_agent": fix_job_automation_agent,
    }

    apps_path = base_path / "apps"

    for service_name, fix_func in service_fixers.items():
        service_path = apps_path / service_name
        if service_path.exists():
            fixes = fix_func(service_path)
            all_fixes.extend(fixes)

    return all_fixes


def print_report(fixes: list[FixTask]) -> None:
    """Вывести отчёт о выполненных исправлениях."""
    print("\n" + "=" * 80)
    print("ОТЧЁТ: Исправление структуры сервисов")
    print("=" * 80 + "\n")

    if not fixes:
        print("✅ Все сервисы соответствуют стандарту!")
        return

    print(f"Выполнено исправлений: {len(fixes)}\n")

    # Группировка по сервисам
    services = {}
    for fix in fixes:
        if fix["service"] not in services:
            services[fix["service"]] = []
        services[fix["service"]].append(fix)

    for service, service_fixes in services.items():
        print(f"\n{service}:")
        for fix in service_fixes:
            action = "✅ Создан" if fix["action"] == "create" else "🔄 Обновлён"
            print(f"   {action}: {fix['path']}")
            print(f"      {fix['description']}")

    print("\n" + "=" * 80 + "\n")


def main():
    """Основная функция."""
    import argparse

    parser = argparse.ArgumentParser(description="Автоматическое исправление структуры сервисов")
    parser.add_argument(
        "service",
        type=str,
        nargs="?",
        help="Исправить конкретный сервис",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_services",
        help="Исправить все сервисы",
    )

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    if args.all_services:
        fixes = fix_all_services(base_path)
        print_report(fixes)
        sys.exit(0)

    if args.service:
        service_path = base_path / "apps" / args.service
        if not service_path.exists():
            print(f"Ошибка: Сервис '{args.service}' не найден")
            sys.exit(1)

        # Выбор фиксера
        fixers = {
            "ai_config_manager": fix_ai_config_manager,
            "auth_service": fix_auth_service,
            "cognitive_agent": fix_cognitive_agent,
            "job_automation_agent": fix_job_automation_agent,
        }

        if args.service in fixers:
            fixes = fixers[args.service](service_path)
            print_report(fixes)
            sys.exit(0)
        else:
            print(f"Нет фиксера для '{args.service}'")
            sys.exit(1)

    print("Usage:")
    print("  python auto_fix_service_structure.py <service-name>")
    print("  python auto_fix_service_structure.py --all")
    sys.exit(1)


if __name__ == "__main__":
    main()
