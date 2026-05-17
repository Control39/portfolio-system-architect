#!/usr/bin/env python3
"""
MCP Server для Career Autopilot

Сервер предоставляет инструменты для работы с файловой системой,
Git, IT-Compass маркерами и мониторингом.
"""

import json
import sys
from pathlib import Path

from fastmcp import FastMCP


# Добавляем путь к корню проекта для импорта общих модулей
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Интеграция с AI Config Manager
try:
    from apps.mcp_server.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    server_config = config_manager.get_config()
    print("✅ MCP Server: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  MCP Server: AI Config Manager недоступен ({e}), используется локальный конфиг")
    server_config = {}

# Инициализация единого экземпляра MCP сервера
mcp = FastMCP("Career Autopilot MCP Server")

# Конфигурация (из AI Config Manager или fallback)
if server_config:
    paths_config = server_config.get("paths", {})
    IT_COMPASS_MARKERS_PATH = Path(paths_config.get("it_compass_markers", "apps/it_compass/src/data/markers"))
    PROJECT_ROOT = Path(paths_config.get("project_root", "."))
else:
    # Fallback на дефолтные пути
    IT_COMPASS_MARKERS_PATH = project_root / "apps" / "it_compass" / "src" / "data" / "markers"
    PROJECT_ROOT = project_root


# Ресурсы навигации
@mcp.resource("navigate://{audience}")
def get_navigation_resource(audience: str = "tech_lead") -> str:
    """
    Навигация по репозиторию для разных аудиторий

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
    """
    Получение информации о домене IT-Compass

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
{", ".join([f"Уровень {lvl}" for lvl in levels])}

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
    return get_compass_domain_resource("system_thinking")  # type: ignore[no-any-return]


def init_all_tools() -> None:
    """Инициализация всех инструментов сервера"""
    from .tools import (
        init_chroma_tools,
        init_compass_tools,
        init_file_tools,
        init_git_tools,
        init_monitoring_tools,
    )

    # Инициализация инструментов в правильном порядке
    init_file_tools(mcp, PROJECT_ROOT)
    init_git_tools(mcp, PROJECT_ROOT)
    init_chroma_tools(mcp, PROJECT_ROOT)
    init_compass_tools(mcp, PROJECT_ROOT)
    init_monitoring_tools(mcp, PROJECT_ROOT)


def main() -> None:
    """Основная функция запуска сервера"""
    print("=" * 60)
    print("Career Autopilot MCP Server")
    print(f"IT-Compass markers path: {IT_COMPASS_MARKERS_PATH}")
    print(f"Project root: {PROJECT_ROOT}")
    print("=" * 60)

    # Проверяем доступность IT-Compass
    if not IT_COMPASS_MARKERS_PATH.exists():
        print(f"Warning: IT-Compass markers path not found: {IT_COMPASS_MARKERS_PATH}")
        print("Some features may not work correctly.")

    # Инициализируем все инструменты
    print("Initializing tools...")
    init_all_tools()
    print("All tools initialized successfully.")

    # Запускаем сервер
    mcp.run()


def main_dev() -> None:
    """Функция запуска в режиме разработки"""
    print("[DEV MODE] Career Autopilot MCP Server")
    print("Running with debug output enabled...")
    main()


if __name__ == "__main__":
    main()
