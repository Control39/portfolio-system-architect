#!/usr/bin/env python3
"""
MCP Server for Career Autopilot

Сервер предоставляет инструменты для работы с:
- Файловой системой проекта
- Git и SourceCraft интеграцией
- IT-Compass маркерами компетенций
- ChromaDB (векторный поиск)
- Мониторингом (Prometheus, Grafana)
- Микросервисами (12 apps)
- Безопасностью (bandit, pip-audit)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Добавляем путь к корню проекта для импорта общих модулей
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Инициализация MCP сервера
mcp = FastMCP(
    "Career Autopilot MCP Server",
    description="MCP сервер для работы с экосистемой Career Autopilot и IT-Compass",
)

# Конфигурация
IT_COMPASS_MARKERS_PATH = (
    project_root / "apps" / "it-compass" / "src" / "data" / "markers"
)
PROJECT_ROOT = project_root
CHROMA_PATH = project_root / "chroma_data"
MONITORING_PATH = project_root / "monitoring"

print(f"🚀 Career Autopilot MCP Server")
print(f"   Project root: {PROJECT_ROOT}")
print(f"   IT-Compass path: {IT_COMPASS_MARKERS_PATH}")
print(f"   ChromaDB path: {CHROMA_PATH}")
print(f"   Monitoring path: {MONITORING_PATH}")


# ============================================================================
# ИНСТРУМЕНТЫ
# ============================================================================

# 1. File Tools
try:
    from src.tools.file_tools import init_file_tools

    init_file_tools(mcp, PROJECT_ROOT)
    print("✅ File tools initialized")
except Exception as e:
    print(f"⚠️  File tools error: {e}")

# 2. Git Tools
try:
    from src.tools.git_tools import init_git_tools

    init_git_tools(mcp, PROJECT_ROOT)
    print("✅ Git tools initialized")
except Exception as e:
    print(f"⚠️  Git tools error: {e}")

# 3. IT-Compass Tools
try:
    from src.tools.compass_tools import init_compass_tools

    init_compass_tools(mcp, PROJECT_ROOT)
    print("✅ IT-Compass tools initialized")
except Exception as e:
    print(f"⚠️  IT-Compass tools error: {e}")

# 4. ChromaDB Tools
try:
    from src.tools.chroma_tools import init_chroma_tools

    init_chroma_tools(mcp, PROJECT_ROOT)
    print("✅ ChromaDB tools initialized")
except Exception as e:
    print(f"⚠️  ChromaDB tools error: {e}")

# 5. Monitoring Tools
try:
    from src.tools.monitoring_tools import init_monitoring_tools

    init_monitoring_tools(mcp, PROJECT_ROOT)
    print("✅ Monitoring tools initialized")
except Exception as e:
    print(f"⚠️  Monitoring tools error: {e}")


# 6. App Management Tools (для 12 микросервисов)
@mcp.tool()
def list_apps() -> List[Dict[str, Any]]:
    """
    Получение списка всех микросервисов (apps)

    Возвращает:
        Список приложений с информацией
    """
    apps_path = PROJECT_ROOT / "apps"
    apps = []

    if apps_path.exists():
        for app_dir in apps_path.iterdir():
            if app_dir.is_dir() and not app_dir.name.startswith("."):
                app_info = {
                    "name": app_dir.name,
                    "path": str(app_dir.relative_to(PROJECT_ROOT)),
                    "has_dockerfile": (app_dir / "Dockerfile").exists(),
                    "has_tests": (app_dir / "tests").exists(),
                    "has_readme": (app_dir / "README.md").exists(),
                }
                apps.append(app_info)

    return sorted(apps, key=lambda x: x["name"])


@mcp.tool()
def get_app_info(app_name: str) -> Dict[str, Any]:
    """
    Получение информации о конкретном микросервисе

    Аргументы:
        app_name: Название приложения

    Возвращает:
        Подробная информация о приложении
    """
    app_path = PROJECT_ROOT / "apps" / app_name

    if not app_path.exists():
        return {"error": f"App '{app_name}' not found"}

    info = {
        "name": app_name,
        "path": str(app_path.relative_to(PROJECT_ROOT)),
        "structure": {},
    }

    # Проверяем ключевые файлы
    key_files = [
        "Dockerfile",
        "README.md",
        "pyproject.toml",
        "requirements.txt",
        "package.json",
        "docker-compose.yml",
    ]

    for file in key_files:
        file_path = app_path / file
        if file_path.exists():
            info["structure"][file] = "exists"

    # Проверяем директории
    key_dirs = ["src", "tests", "config", "scripts", "docs"]
    for dir_name in key_dirs:
        dir_path = app_path / dir_name
        if dir_path.exists():
            info["structure"][f"{dir_name}/"] = "exists"

    return info


@mcp.tool()
def restart_app(app_name: str) -> Dict[str, Any]:
    """
    Перезапуск микросервиса через Docker Compose

    Аргументы:
        app_name: Название приложения

    Возвращает:
        Статус операции
    """
    try:
        # Пробуем через docker-compose
        result = subprocess.run(
            ["docker-compose", "restart", app_name],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return {"status": "success", "message": f"App '{app_name}' restarted"}
        else:
            return {"status": "error", "message": result.stderr}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# 7. Security Tools
@mcp.tool()
def run_security_scan(scan_type: str = "bandit") -> Dict[str, Any]:
    """
    Запуск сканирования безопасности

    Аргументы:
        scan_type: Тип сканирования (bandit, pip-audit, safety)

    Возвращает:
        Результаты сканирования
    """
    try:
        if scan_type == "bandit":
            result = subprocess.run(
                ["bandit", "-r", "src/", "apps/", "-c", ".bandit.yml", "-f", "json"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"status": "clean", "results": json.loads(result.stdout)}
            else:
                try:
                    return {
                        "status": "issues_found",
                        "results": json.loads(result.stdout),
                    }
                except:
                    return {
                        "status": "error",
                        "output": result.stdout,
                        "error": result.stderr,
                    }

        elif scan_type == "pip-audit":
            result = subprocess.run(
                ["pip-audit", "-r", "requirements.txt"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if "No known vulnerabilities" in result.stdout:
                return {"status": "clean", "message": "No vulnerabilities found"}
            else:
                return {"status": "vulnerabilities_found", "output": result.stdout}

        else:
            return {"error": f"Unknown scan type: {scan_type}"}

    except FileNotFoundError:
        return {"error": f"Tool '{scan_type}' not installed"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# РЕСУРСЫ
# ============================================================================


@mcp.resource("navigate://{audience}")
def get_navigation_resource(audience: str = "tech_lead") -> str:
    """
    Навигация по репозиторию для разных аудиторий

    Аргументы:
        audience: Целевая аудитория (hr, tech_lead, grant, community, sourcecraft)
    """
    tours = {
        "hr": """
# Тур для HR и рекрутеров

## Ключевые компоненты:
1. **IT-Compass** (`apps/it-compass/`) - методология объективных маркеров компетенций
2. **Портфолио** (`docs/FOR-HR.md`) - адаптированная для HR документация
3. **Демо-видео** (`docs/screenshots/`) - скриншоты и демонстрации

## Что показывает:
- Системное мышление (1495 маркеров по 18 доменам)
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
1. **IT-Compass** - авторская методология с 1495 объективными маркерами
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
        "sourcecraft": """
# Тур для SourceCraft (грантовый комитет)

## Соответствие критериям SourceCraft:

### 1. Open Source
- ✅ Лицензия CC BY-ND 4.0
- ✅ Публичный репозиторий на GitHub
- ✅ Документация на русском языке
- ✅ Готовность к community contribution

### 2. Инновации
- ✅ IT-Compass - уникальная методология (1495 маркеров)
- ✅ Cognitive Automation Agent - когнитивная автоматизация
- ✅ MCP Server - интеграция с AI assistants

### 3. Техническое качество
- ✅ 12 микросервисов с Docker
- ✅ Полный CI/CD (GitHub Actions)
- ✅ Мониторинг (Prometheus + Grafana)
- ✅ Безопасность (bandit, pip-audit, .bandit.yml)

### 4. Экосистема
- ✅ SourceCraft интеграция (git sourcecraft)
- ✅ Koda AI assistant
- ✅ Skills system (teacher, task-planner, etc.)

## Ключевые файлы:
- `docs/FOR-GRANT.md` - заявка
- `docs/METHODOLOGY/` - методология
- `apps/mcp-server/` - MCP сервер
""",
    }

    return tours.get(audience, tours["tech_lead"])


@mcp.resource("it-compass://domain/{domain}")
def get_compass_domain_resource(domain: str = "system_thinking") -> str:
    """
    Получение информации о домене IT-Compass

    Аргументы:
        domain: Домен IT-Compass
    """
    domain_file = IT_COMPASS_MARKERS_PATH / f"{domain}.json"

    if not domain_file.exists():
        return f"Домен '{domain}' не найден в IT-Compass"

    try:
        with open(domain_file, "r", encoding="utf-8") as f:
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
        return f"Ошибка при чтении домена '{domain}': {str(e)}"


def _get_sample_markers(data: Dict) -> str:
    """Получение примеров маркеров из данных домена"""
    markers = []
    levels = data.get("levels", {})

    for level_num, level_markers in levels.items():
        if level_markers and len(level_markers) > 0:
            marker = level_markers[0]
            markers.append(
                f"- **Уровень {level_num}**: {marker.get('marker', 'Нет описания')}"
            )
            if len(markers) >= 3:
                break

    return "\n".join(markers) if markers else "Нет примеров маркеров"


@mcp.resource("it-compass://system-thinking")
def get_system_thinking_resource() -> str:
    """Специальный ресурс для системного мышления"""
    return get_compass_domain_resource("system_thinking")


# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("✅ Career Autopilot MCP Server Ready")
    print("=" * 60)

    # Проверяем доступность ключевых компонентов
    components = {
        "IT-Compass": IT_COMPASS_MARKERS_PATH.exists(),
        "ChromaDB": CHROMA_PATH.exists(),
        "Monitoring": MONITORING_PATH.exists(),
    }

    for component, status in components.items():
        icon = "✅" if status else "⚠️"
        print(f"{icon} {component}: {'Available' if status else 'Not found'}")

    print("=" * 60)

    # Запускаем сервер
    mcp.run()
