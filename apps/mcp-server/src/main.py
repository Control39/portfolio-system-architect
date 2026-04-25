#!/usr/bin/env python3
"""MCP Server for Career Autopilot

Сервер предоставляет инструменты для работы с файловой системой,
Git, IT-Compass маркерами и выполнения команд.
"""

import json
import sys
from pathlib import Path

from fastmcp import FastMCP

# Добавляем путь к корню проекта для импорта общих модулей
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Инициализация MCP сервера
mcp = FastMCP("Career Autopilot MCP Server")

# Конфигурация
IT_COMPASS_MARKERS_PATH = project_root / "apps" / "it-compass" / "src" / "data" / "markers"
PROJECT_ROOT = project_root

# Импорт инструментов
try:
    from src.resources.navigation import generate_tour_tool, search_repo_tool
    from src.tools.command_tools import execute_command_tool, run_python_script_tool
    from src.tools.compass_tools import (
        auto_detect_markers_from_code_tool,
        evaluate_by_compass_tool,
        get_markers_by_domain_tool,
    )
    from src.tools.file_tools import (
        list_files_tool,
        read_file_tool,
        search_files_tool,
        write_file_tool,
    )
    from src.tools.git_tools import (
        get_git_history_tool,
        get_git_status_tool,
        scan_last_commits_for_markers_tool,
    )
except ImportError:
    # Если модули не найдены, создадим заглушки
    print("Warning: Tool modules not found. Using stub implementations.")

    # Заглушки будут заменены при создании реальных модулей
    @mcp.tool()
    def read_file_tool(path: str) -> str:
        """Чтение файла"""
        return f"Stub: read_file({path})"

    @mcp.tool()
    def write_file_tool(path: str, content: str) -> bool:
        """Запись файла"""
        return True

    @mcp.tool()
    def list_files_tool(path: str, recursive: bool = False) -> list[str]:
        """Список файлов"""
        return []

    @mcp.tool()
    def search_files_tool(query: str, file_pattern: str = "*.py") -> list[str]:
        """Поиск файлов"""
        return []

# Ресурсы навигации
@mcp.resource("navigate://{audience}")
def get_navigation_resource(audience: str = "tech_lead") -> str:
    """Навигация по репозиторию для разных аудиторий

    Аргументы:
        audience: Целевая аудитория (hr, tech_lead, grant, community)
    """
    tours = {
        "hr": """
# Тур для HR и рекрутеров

## Ключевые компоненты:
1. **IT-Compass** (`apps/it-compass/`) - методология объективных маркеров компетенций
2. **Портфолио** (`docs/FOR-HR.md`) - адаптированная для HR документация
3. **Демо-видео** (`docs/screenshots/`) - скриншоты и демонстрации

## Что показывает:
- Системное мышление (83 маркера по 19 доменам)
- Управление сложными проектами (12 микросервисов)
- Полный CI/CD и мониторинг
- Способность создавать методологии и инструменты

## Рекомендуемые файлы:
- `docs/FOR-HR.md` - объяснение для HR
- `PERSONAL-README.md` - личное введение
- `project-config.yaml` - структура проекта
""",
        "tech_lead": """
# Тур для технических лидов

## Архитектура:
1. **Микросервисы** (`apps/`) - 12 независимых компонентов
2. **API Gateway** (`gateway/`) - единая точка входа
3. **Мониторинг** (`monitoring/`) - Prometheus, Grafana, алертинг
4. **DevOps** (`deployment/`, `.github/workflows/`) - полный CI/CD

## Технологический стек:
- Python, FastAPI, Docker, Kubernetes
- PostgreSQL, ChromaDB (векторная БД)
- GitHub Actions, ArgoCD (GitOps)
- Prometheus, Grafana, Alertmanager

## Ключевые решения:
- `docs/architecture/decisions/` - ADR (Architectural Decision Records)
- `docker-compose.yml` - локальное развертывание
- `deployment/k8s/` - Kubernetes манифесты
""",
        "grant": """
# Тур для грантовых комитетов (SourceCraft Open Source)

## Инновации:
1. **IT-Compass** - авторская методология с 83 объективными маркерами
2. **Cognitive Systems Architecture** - архитектура когнитивных систем
3. **Career Autopilot** - автоматическое обнаружение маркеров и генерация портфолио

## Open Source вклад:
- Полная документация на русском и английском
- Готовые Docker образы и Helm charts
- Интеграция с популярными инструментами (GitHub, VS Code)
- Сообщество поддержки и примеры использования

## Файлы для гранта:
- `docs/FOR-GRANT.md` - заявка на грант
- `LICENSE` - лицензия CC BY-ND 4.0
- `CONTRIBUTING.md` - руководство для контрибьюторов
""",
        "community": """
# Тур для сообщества разработчиков

## Для обучения:
1. **Шаблоны** (`templates/`) - готовые шаблоны проектов
2. **Примеры** (`samples/`) - примеры использования
3. **Документация** (`docs/`) - подробные руководства

## Для использования:
- `QUICKSTART.md` - быстрый старт за 5 минут
- `docker-compose.yml` - запуск всей экосистемы
- `Makefile` - удобные команды

## Для развития:
- `.github/workflows/` - готовые CI/CD пайплайны
- `pre-commit-config.yaml` - автоматические проверки
- `tests/` - примеры тестирования
""",
    }

    return tours.get(audience, tours["tech_lead"])

# Ресурсы IT-Compass
@mcp.resource("it-compass://domain/{domain}")
def get_compass_domain_resource(domain: str = "system_thinking") -> str:
    """Получение информации о домене IT-Compass

    Аргументы:
        domain: Домен IT-Compass (system_thinking, python, docker, devops и т.д.)
    """
    domain_file = IT_COMPASS_MARKERS_PATH / f"{domain}.json"

    if not domain_file.exists():
        return f"Домен '{domain}' не найден в IT-Compass"

    try:
        with open(domain_file, encoding="utf-8") as f:
            data = json.load(f)

        skill_name = data.get("skill_name", domain)
        description = data.get("description", "Нет описания")
        levels = list(data.get("levels", {}).keys())

        return f"""
# IT-Compass: {skill_name}

## Описание
{description}

## Уровни: {len(levels)}
{', '.join([f'Уровень {lvl}' for lvl in levels])}

## Примеры маркеров:
{_get_sample_markers(data)}

## Расположение файла:
{domain_file.relative_to(PROJECT_ROOT)}
"""
    except Exception as e:
        return f"Ошибка при чтении домена '{domain}': {e!s}"

def _get_sample_markers(data: dict) -> str:
    """Получение примеров маркеров из данных домена"""
    markers = []
    levels = data.get("levels", {})

    for level_num, level_markers in levels.items():
        if level_markers and len(level_markers) > 0:
            marker = level_markers[0]
            markers.append(f"- **Уровень {level_num}**: {marker.get('marker', 'Нет описания')}")
            if len(markers) >= 3:
                break

    return "\n".join(markers) if markers else "Нет примеров маркеров"

@mcp.resource("it-compass://system-thinking")
def get_system_thinking_resource() -> str:
    """Специальный ресурс для системного мышления"""
    return get_compass_domain_resource("system_thinking")

# Инструменты (будут импортированы из модулей или определены как заглушки)
# Здесь мы регистрируем инструменты, если они были импортированы
# В противном случае заглушки уже зарегистрированы

# Основная функция
if __name__ == "__main__":
    print("=" * 60)
    print("Career Autopilot MCP Server")
    print(f"IT-Compass markers path: {IT_COMPASS_MARKERS_PATH}")
    print(f"Project root: {PROJECT_ROOT}")
    print("=" * 60)

    # Проверяем доступность IT-Compass
    if not IT_COMPASS_MARKERS_PATH.exists():
        print(f"Warning: IT-Compass markers path not found: {IT_COMPASS_MARKERS_PATH}")
        print("Some features may not work correctly.")

    # Запускаем сервер
    mcp.run()

