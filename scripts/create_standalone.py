#!/usr/bin/env python3
"""
Скрипт для автоматического вынесения микросервисов в standalone-репозитории.

Использование:
    python scripts/create_standalone.py it_compass
    python scripts/create_standalone.py cognitive-agent
    python scripts/create_standalone.py --list  # Показать все доступные сервисы
"""

import shutil
import sys
from pathlib import Path


# Ключевые сервисы для вынесения (приоритет по порядку)
SERVICE_PRIORITY = [
    "it_compass",
    "ai-config-manager",
    "cognitive-agent",
    "portfolio_organizer",
    "system_proof",
    "decision_engine",
    "ml_model_registry",
    "mcp_server",
    "career_development",
    "knowledge_graph",
    "infra-orchestrator",
    "job-automation-agent",
    "thought-architecture",
    "template-service",
]

# Файлы/папки, которые нужно исключить
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "*.egg-info",
]

# Файлы, которые нужно обновить в standalone-версии
FILES_TO_UPDATE = [
    "README.md",
    "pyproject.toml",
    ".gitignore",
]


def get_available_services() -> list[str]:
    """Получить список доступных сервисов в apps/"""
    apps_dir = Path("apps")
    if not apps_dir.exists():
        return []

    services = []
    for item in apps_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            services.append(item.name)

    return services


def create_standalone(service_name: str, dry_run: bool = False) -> Path | None:
    """
    Создать standalone-версию сервиса.

    Args:
        service_name: Название сервиса (например, "it_compass")
        dry_run: Если True, только показать, что будет сделано

    Returns:
        Путь к созданной папке или None
    """
    apps_dir = Path("apps")
    service_dir = apps_dir / service_name

    if not service_dir.exists():
        print(f"❌ Сервис '{service_name}' не найден в apps/")
        print(f"Доступные сервисы: {', '.join(get_available_services())}")
        return None

    # Определяем имя для standalone-версии
    standalone_name = f"{service_name}-standalone"
    standalone_dir = Path(standalone_name)

    if standalone_dir.exists():
        print(f"⚠️  Папка '{standalone_name}' уже существует!")
        response = input("Переписать? (y/n): ")
        if response.lower() != "y":
            return None
        shutil.rmtree(standalone_dir)

    print(f"📦 Создание standalone-версии: {service_name} → {standalone_name}")

    if dry_run:
        print("🔍 [DRY RUN] Будет скопировано:")
        for item in service_dir.rglob("*"):
            if item.is_file() and not any(pattern in str(item) for pattern in EXCLUDE_PATTERNS):
                rel_path = item.relative_to(service_dir)
                print(f"  - {rel_path}")
        return None

    # Копируем сервис, исключая лишнее
    print("📋 Копирование файлов...")
    shutil.copytree(service_dir, standalone_dir, ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS))

    # Обновляем README.md
    readme_file = standalone_dir / "README.md"
    if readme_file.exists():
        print("✏️  Обновление README.md...")
        update_readme(readme_file, service_name)

    # Обновляем pyproject.toml
    pyproject_file = standalone_dir / "pyproject.toml"
    if pyproject_file.exists():
        print("✏️  Обновление pyproject.toml...")
        update_pyproject(pyproject_file, service_name)

    # Создаём .gitignore, если нет
    gitignore_file = standalone_dir / ".gitignore"
    if not gitignore_file.exists():
        print("📝 Создание .gitignore...")
        create_gitignore(gitignore_file)

    # Создаём инструкцию по публикации
    publish_file = standalone_dir / "PUBLISH_INSTRUCTIONS.md"
    if not publish_file.exists():
        print("📝 Создание PUBLISH_INSTRUCTIONS.md...")
        create_publish_instructions(publish_file, service_name)

    print(f"✅ Готово! Standalone-версия создана: {standalone_name}/")
    print("\n📋 Следующие шаги:")
    print(f"1. cd {standalone_name}")
    print("2. git init && git add . && git commit -m 'Initial standalone release'")
    print("3. Создайте репозиторий на GitHub и запушьте")
    print("4. python -m build && twine upload dist/*")

    return standalone_dir


def update_readme(readme_path: Path, service_name: str) -> None:
    """Добавить секции в README.md для standalone-версии"""
    content = readme_path.read_text(encoding="utf-8")

    # Добавляем секцию "Экосистема"
    ecosystem_section = f"""
---

## 🌍 Экосистема

Этот проект — часть **Portfolio System Architect** (15 микросервисов).

- **Полная история:** [STORY.md](https://github.com/Control39/portfolio-system-architect/blob/main/STORY.md)
- **Архитектура:** [ARCHITECTURE.md](https://github.com/Control39/portfolio-system-architect/blob/main/ARCHITECTURE.md)
- **Другие проекты:**
  - [it-compass](https://github.com/Control39/it-compass) •
  - [ai-config-manager](https://github.com/Control39/ai-config-manager) •
  - [cognitive-agent](https://github.com/Control39/cognitive-agent)

---

## 🚀 Quick Start (5 минут)

```bash
# Установка через pip
pip install {service_name.replace("_", "-")}

# Или из исходного кода
git clone https://github.com/Control39/{service_name.replace("_", "-")}.git
cd {service_name.replace("_", "-")}
pip install -e .

# Запуск
```
"""

    # Добавляем секцию перед последним разделом
    if "## " in content:
        # Находим последний раздел
        last_section = content.rsplit("## ", 1)[0]
        content = last_section + "## " + content.rsplit("## ", 1)[1]

    # Добавляем секцию "Экосистема" перед "## Лицензия" или в конец
    if "## Лицензия" in content:
        content = content.replace("## Лицензия", ecosystem_section + "\n## Лицензия")
    else:
        content += ecosystem_section

    readme_path.write_text(content, encoding="utf-8")


def update_pyproject(pyproject_path: Path, service_name: str) -> None:
    """Уточнить pyproject.toml для standalone-версии"""
    content = pyproject_path.read_text(encoding="utf-8")

    # Проверяем, есть ли уже метаданные для публикации
    if "author" not in content.lower():
        # Добавляем автора
        content = content.replace(
            "[project]",
            '[project]\nauthors = [\n    {name = "Ekaterina Kudelya", email = "leadarchitect@yandex.ru"}\n]',
        )

    # Добавляем репозиторий, если нет
    if "repository" not in content.lower():
        content = content.replace(
            'readme = "README.md"',
            'readme = "README.md"\nrepository = "https://github.com/Control39/'
            + service_name.replace("_", "-")
            + '"\n',
        )

    pyproject_path.write_text(content, encoding="utf-8")


def create_gitignore(gitignore_path: Path) -> None:
    """Создать стандартный .gitignore"""
    content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Виртуальное окружение
.venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Тестирование
.pytest_cache/
.coverage
htmlcov/
.tox/

# Линтеры
.ruff_cache/
.mypy_cache/

# Операционные системы
.DS_Store
Thumbs.db

# Секреты
.env
.env.local
*.pem
*.key
"""
    gitignore_path.write_text(content, encoding="utf-8")


def create_publish_instructions(publish_path: Path, service_name: str) -> None:
    """Создать инструкцию по публикации"""
    content = f"""# Инструкция по публикации {service_name.replace("_", "-")}

## 📋 Предварительные требования

```bash
pip install build twine
```

## 🚀 Пошаговая инструкция

### 1. Создать репозиторий на GitHub

1. Зайдите на [github.com/new](https://github.com/new)
2. Название: `{service_name.replace("_", "-")}`
3. Описание: "Частично {service_name.replace("_", "-")} от Portfolio System Architect"
4. Публичный репозиторий
5. Не инициализировать README/Gitignore (мы уже есть)

### 2. Инициализировать Git

```bash
cd {service_name.replace("_", "-")}
git init
git add .
git commit -m "Initial standalone release of {service_name.replace("_", "-")}"
git branch -M main
git remote add origin https://github.com/Control39/{service_name.replace("_", "-")}.git
git push -u origin main
```

### 3. Опубликовать на PyPI (опционально)

```bash
# Построение пакета
python -m build

# Проверка
twine check dist/*

# Публикация на TestPyPI (тест)
twine upload --repository testpypi dist/*

# Публикация на PyPI (реально)
twine upload dist/*
```

### 4. Обновить главный репозиторий

Добавить ссылку на новый проект в `portfolio-system-architect/README.md`:

```markdown
| [it-compass](https://github.com/Control39/it-compass) | Методология компетенций | `pip install it-compass` |
```

## 📝 Чек-лист перед публикацией

- [ ] README.md содержит Quick Start
- [ ] pyproject.toml обновлён с метаданными
- [ ] .gitignore создан
- [ ] Лицензия (MIT) добавлена
- [ ] Версия установлена (1.0.0)
- [ ] Тесты проходят (`pytest`)
- [ ] Документация проверена

## 🔗 Ссылки

- **Исходный код:** [Portfolio System Architect](https://github.com/Control39/portfolio-system-architect)
- **Документация:** [STORY.md](https://github.com/Control39/portfolio-system-architect/blob/main/STORY.md)
- **Методология:** [IT-Compass](https://github.com/Control39/portfolio-system-architect/blob/main/docs/it-compass/METHODOLOGY.md)
"""
    publish_path.write_text(content, encoding="utf-8")


def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("🛠️  Создание standalone-версии микросервиса")
        print("\nИспользование:")
        print("  python scripts/create_standalone.py <service_name>")
        print("  python scripts/create_standalone.py --list")
        print("  python scripts/create_standalone.py it_compass --dry-run")
        print("\nДоступные сервисы:")
        for service in get_available_services():
            priority = ""
            if service in SERVICE_PRIORITY:
                idx = SERVICE_PRIORITY.index(service) + 1
                priority = f" (приоритет #{idx})"
            print(f"  - {service}{priority}")
        return

    if sys.argv[1] == "--list":
        print("📦 Доступные сервисы для вынесения:")
        for service in SERVICE_PRIORITY:
            if service in get_available_services():
                print(f"  ✅ {service}")
            else:
                print(f"  ❌ {service} (не найден)")
        return

    service_name = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    create_standalone(service_name, dry_run)


if __name__ == "__main__":
    main()
