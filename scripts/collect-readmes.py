#!/usr/bin/env python3
"""
Скрипт для сбора и классификации всех README-файлов проекта.
Создает структуру в .reports/READMEs/ с группировкой по темам.
"""

import shutil
from pathlib import Path
from datetime import datetime

# Корень проекта
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / ".reports" / "READMEs"

# Классификатор по темам на основе пути
THEME_MAPPING = {
    "apps": ("📦 Микросервисы и Приложения", [
        "apps/cognitive-agent",
        "apps/decision-engine", 
        "apps/it_compass",
        "apps/portfolio_organizer",
        "apps/system-proof",
        "apps/ml-model-registry",
        "apps/auth_service",
        "apps/career_development",
        "apps/infra-orchestrator",
        "apps/ai-config-manager",
        "apps/knowledge-graph",
        "apps/mcp-server",
        "apps/template-service",
        "apps/job-automation-agent",
        "apps/thought-architecture",
    ]),
    "docs-methodology": ("🎓 Методология IT-Compass", [
        "docs/methodology",
        "docs/methodology/02_METHODOLOGY",
        "docs/methodology/03_EVIDENCE",
        "docs/methodology/04_ARTIFACTS",
        "docs/methodology/05_MANIFEST",
    ]),
    "docs-cases": ("📋 Кейсы и Примеры", [
        "docs/cases",
        "docs/cases/thinking-cases",
        "docs/cases/evolution-cases",
        "docs/cases/cases",
        "docs/cases/ai-config-manager",
    ]),
    "docs-internal": ("🔍 Внутренний Анализ", [
        "docs/internal/analysis",
        "docs/internal/analysis/security",
        "docs/internal/analysis/code-quality",
        "docs/internal/analysis/performance",
        "docs/internal/analysis/scalability",
        "docs/internal/analysis/devops",
        "docs/internal/analysis/business_goals",
        "docs/internal/analysis/innovation",
        "docs/internal/analysis/technology_refresh",
        "docs/internal/analysis/processes",
        "docs/internal/analysis/documentation",
    ]),
    "docs-presentations": ("🎤 Презентации и Демонстрации", [
        "docs/presentations",
        "docs/presentations/technical",
        "docs/presentations/workshop",
        "docs/screenshots",
        "docs/screenshots/monitoring",
    ]),
    "docs-professional": ("👤 Профессиональный Путь", [
        "docs/professional-journey",
        "docs/evidence/self-analysis",
    ]),
    "deployment": ("🚀 Деплой и Kubernetes", [
        "deployment",
        "deployment/k8s",
        "deployment/gitops",
        "deployment/secrets",
    ]),
    "codeassistant": ("🤖 AI Ассистент и SourceCraft", [
        "codeassistant",
        "codeassistant/tools",
    ]),
    "ci-cd": ("⚙️ CI/CD и GitHub Actions", [
        ".github/workflows",
        "config/ci-cd",
    ]),
    "devops": ("🔧 DevOps и Инструменты", [
        "tools",
        "scripts",
        "scripts/dev",
        "monitoring",
        "docker",
        "docker/base-images",
    ]),
    "client": ("💻 Frontend и Клиент", [
        "client",
    ]),
    "config": ("⚙️ Конфигурации", [
        "config",
        "config/ai",
        "config/vscode",
    ]),
    "tests": ("🧪 Тестирование", [
        "tests",
    ]),
    "src": ("📚 Исходный Код", [
        "src",
        "src/shared/schemas",
    ]),
    "examples": ("💡 Примеры", [
        "examples",
        "examples/templates",
        "examples/badges",
        "examples/legacy",
    ]),
    "legacy": ("📜 Устаревший Код", [
        "legacy",
        "migrations",
    ]),
    "meta": ("📝 Мета-информация", [
        "",
        ".github",
        ".github/profile",
        ".koda",
        ".kodacli",
        ".continue",
        ".devcontainer",
        ".sourcecraft",
        "docs",
        "diagrams",
        "settings",
        "postgres",
        "mcp-server",
        "utils",
        "cases",
    ]),
}

def classify_readme(readme_path: Path) -> tuple:
    """
    Определяет тему для README на основе относительного пути.
    Возвращает (тема, подтема).
    """
    rel_path = readme_path.relative_to(PROJECT_ROOT)
    path_str = str(rel_path.parent).replace("\\", "/")
    parts = rel_path.parent.parts
    
    # Список тем в порядке приоритета (от специфичных к общим)
    priority_themes = [
        ("📦 Микросервисы и Приложения", [
            "apps/cognitive-agent", "apps/decision-engine", "apps/it_compass",
            "apps/portfolio_organizer", "apps/system-proof", "apps/ml-model-registry",
            "apps/auth_service", "apps/career_development", "apps/infra-orchestrator",
            "apps/ai-config-manager", "apps/knowledge-graph", "apps/mcp-server",
            "apps/template-service", "apps/job-automation-agent", "apps/thought-architecture"
        ]),
        ("🎓 Методология IT-Compass", [
            "docs/methodology/02_METHODOLOGY/arch-compass",
            "docs/methodology/02_METHODOLOGY/it-compass",
            "docs/methodology/02_METHODOLOGY",
            "docs/methodology/03_EVIDENCE/rag-system",
            "docs/methodology/03_EVIDENCE",
            "docs/methodology/04_ARTIFACTS/grants",
            "docs/methodology/04_ARTIFACTS/case-studies",
            "docs/methodology/04_ARTIFACTS",
            "docs/methodology/05_MANIFEST",
            "docs/methodology"
        ]),
        ("📋 Кейсы и Примеры", [
            "docs/cases/thinking-cases",
            "docs/cases/evolution-cases",
            "docs/cases/cases/presentation-cases",
            "docs/cases/cases/thinking-cases",
            "docs/cases/ai-config-manager",
            "docs/cases"
        ]),
        ("🔍 Внутренний Анализ", [
            "docs/internal/analysis/security",
            "docs/internal/analysis/code-quality",
            "docs/internal/analysis/performance",
            "docs/internal/analysis/scalability",
            "docs/internal/analysis/devops",
            "docs/internal/analysis/business_goals",
            "docs/internal/analysis/innovation",
            "docs/internal/analysis/technology_refresh",
            "docs/internal/analysis/processes",
            "docs/internal/analysis/documentation",
            "docs/internal/analysis"
        ]),
        ("🎤 Презентации и Демонстрации", [
            "docs/presentations/technical",
            "docs/presentations/workshop",
            "docs/presentations",
            "docs/screenshots/monitoring",
            "docs/screenshots"
        ]),
        ("👤 Профессиональный Путь", [
            "docs/professional-journey",
            "docs/evidence/self-analysis"
        ]),
        ("🚀 Деплой и Kubernetes", [
            "deployment/secrets",
            "deployment/k8s",
            "deployment/gitops",
            "deployment"
        ]),
        ("🤖 AI Ассистент и SourceCraft", [
            "codeassistant/tools",
            "codeassistant",
            ".sourcecraft"
        ]),
        ("⚙️ CI/CD и GitHub Actions", [
            ".github/workflows",
            "config/ci-cd"
        ]),
        ("🔧 DevOps и Инструменты", [
            "scripts/dev",
            "scripts",
            "tools",
            "monitoring",
            "docker/base-images",
            "docker"
        ]),
        ("💻 Frontend и Клиент", ["client"]),
        ("⚙️ Конфигурации", [
            "config/vscode",
            "config/ai",
            "config"
        ]),
        ("🧪 Тестирование", ["tests"]),
        ("📚 Исходный Код", [
            "src/shared/schemas",
            "src"
        ]),
        ("💡 Примеры", [
            "examples/templates",
            "examples/badges",
            "examples/legacy/automation",
            "examples/legacy/packages/terraform/examples/basic",
            "examples/legacy/packages/terraform",
            "examples/legacy",
            "examples"
        ]),
        ("📜 Устаревший Код", [
            "legacy/infra-chat-demo",
            "legacy",
            "migrations"
        ])
    ]
    
    for theme_title, paths in priority_themes:
        for base_path in paths:
            if path_str == base_path or path_str.startswith(base_path + "/"):
                # Подтема
                if len(parts) >= 2:
                    if parts[0] == "docs" and len(parts) > 3:
                        subtheme = "/".join(parts[2:])
                    elif parts[0] in ["apps", "docs", "deployment", "config", "examples", "legacy", "scripts", "docs/internal/analysis", "docs/cases"]:
                        if len(parts) > 2:
                            subtheme = "/".join(parts[1:])
                        else:
                            subtheme = parts[0]
                    else:
                        subtheme = "/".join(parts[-2:])
                elif len(parts) == 1:
                    subtheme = parts[0]
                else:
                    subtheme = "root"
                return theme_title, subtheme
    
    return "📝 Мета-информация", parts[-1] if parts else "root"

def create_index(themes_data: dict) -> str:
    """Создает индексный файл с оглавлением."""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = []
    lines.append("# Индекс всех README проекта")
    lines.append("")
    lines.append(f"**Сгенерировано:** {timestamp}")
    lines.append("")
    lines.append("Этот каталог содержит все README-файлы проекта, сгруппированные по темам для удобной навигации.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for theme_title, files in sorted(themes_data.items(), key=lambda x: x[0]):
        lines.append(f"## {theme_title}")
        lines.append("")
        for file_info in sorted(files, key=lambda x: x["subtheme"]):
            subtheme = file_info["subtheme"]
            title = file_info["title"]
            rel_path = file_info["relative_path"]
            lines.append(f"- **{subtheme}**: [{title}]({rel_path})")
        lines.append("")
    
    total_files = sum(len(files) for files in themes_data.values())
    total_themes = len(themes_data)
    lines.append("---")
    lines.append("")
    lines.append("## Статистика")
    lines.append("")
    lines.append(f"- **Всего README файлов:** {total_files}")
    lines.append(f"- **Количество тем:** {total_themes}")
    lines.append("")
    lines.append("*Этот индекс автоматически сгенерирован скриптом `scripts/collect-readmes.py`*")
    
    return "\n".join(lines)

def clean_theme_name(name: str) -> str:
    """Очищает название темы для использования в имени директории."""
    emojis = ["📦", "🎓", "📋", "🔍", "🎤", "👤", "🚀", "🤖", "⚙️", "🔧", "💻", "📚", "💡", "📜", "📁", "📝"]
    for emoji in emojis:
        name = name.replace(emoji, "")
    return name.replace(" ", "-").lower().strip("-")

def main():
    print("🚀 Сбор всех README-файлов проекта...")
    print(f"📂 Корень проекта: {PROJECT_ROOT}")
    print(f"📁 Выходная директория: {OUTPUT_DIR}")
    
    # Очистка и создание выходной директории
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Поиск всех README.md
    readme_files = list(PROJECT_ROOT.rglob("README.md"))
    print(f"📄 Найдено README файлов: {len(readme_files)}")
    
    # Структура для хранения данных по темам
    themes_data = {}
    
    # Обработка каждого README
    for readme_path in readme_files:
        theme_title, subtheme = classify_readme(readme_path)
        
        # Создаем директорию темы
        theme_dir = OUTPUT_DIR / clean_theme_name(theme_title)
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем подтему (субдиректорию)
        if subtheme != "root":
            subtheme_safe = subtheme.replace("/", "_").replace("\\", "_")
            target_subdir = theme_dir / subtheme_safe
            target_subdir.mkdir(parents=True, exist_ok=True)
        else:
            target_subdir = theme_dir
        
        # Копируем файл с уникальным именем
        target_path = target_subdir / readme_path.name
        
        # Если файл уже существует, добавляем префикс пути
        if target_path.exists():
            prefix = "_".join(readme_path.relative_to(PROJECT_ROOT).parent.parts)
            target_path = theme_dir / f"{prefix}_README.md"
        
        shutil.copy2(readme_path, target_path)
        
        # Сохраняем информацию для индекса
        if theme_title not in themes_data:
            themes_data[theme_title] = []
        
        themes_data[theme_title].append({
            "title": readme_path.stem,
            "original_path": readme_path,
            "relative_path": target_path.relative_to(OUTPUT_DIR),
            "subtheme": subtheme,
            "theme": theme_title,
        })
    
    # Создаем индекс
    index_content = create_index(themes_data)
    index_path = OUTPUT_DIR / "INDEX.md"
    index_path.write_text(index_content, encoding="utf-8")
    
    # Создаем README в корне .reports
    reports_readme = PROJECT_ROOT / ".reports" / "README.md"
    timestamp2 = datetime.now().strftime("%d.%m.%Y %H:%M")
    content_lines = []
    content_lines.append("# Отчёты и Документация")
    content_lines.append("")
    content_lines.append("Эта папка содержит сгенерированные отчёты и сводки документации.")
    content_lines.append("")
    content_lines.append("## 📚 Сводка всех README")
    content_lines.append("")
    content_lines.append(f"Полный индекс всех README-файлов проекта доступен здесь: [INDEX.md]({index_path.relative_to(PROJECT_ROOT)})")
    content_lines.append("")
    content_lines.append("## 📊 Структура")
    content_lines.append("")
    content_lines.append("- **READMEs/** - Все README-файлы, сгруппированные по темам")
    content_lines.append("- **INDEX.md** - Оглавление и навигация")
    content_lines.append("")
    content_lines.append(f"*Генерация: {timestamp2}*")
    reports_readme.write_text("\n".join(content_lines), encoding="utf-8")
    
    print("✅ Готово!")
    print("📊 Статистика:")
    for theme, files in sorted(themes_data.items()):
        print(f"   {theme}: {len(files)} файлов")
    print(f"📁 Выход: {OUTPUT_DIR}")
    print(f"📑 Индекс: {index_path}")

if __name__ == "__main__":
    main()