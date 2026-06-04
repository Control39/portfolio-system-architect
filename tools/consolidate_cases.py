#!/usr/bin/env python3
"""
Консолидация кейсов и обновление ссылок
Цель: Переместить кейсы в новую структуру и обновить все ссылки
"""

import shutil
from pathlib import Path

# Корень проекта
ROOT = Path(r"C:\repo")
CASES_SRC = ROOT / "docs" / "cases"
CASES_DST = ROOT / "docs" / "cases" / "archive_original"  # Бэкап

# Новая структура
NEW_STRUCTURE = {
    "integration": [
        "case-1-it-compass-portfolio-organizer",
        "case-2-infra-orchestrator-decision-engine",
        "case-3-system-proof-thought-architecture",
    ],
    "business": ["business-impact"],
    "thinking": ["thinking-cases"],
    "evolution": ["evolution-cases"],
    "methodology": ["it-compass"],
    "technical": ["ai-config-manager"],  # Будет перемещен
}

# Файлы в корне docs/, которые нужно переместить
ROOT_DOCS_FILES = {
    "BIZ-CASES-AUTOARCHITECT.md": "business/autoarchitect.md",
}


def move_case(src_name, dst_category):
    """Переместить папку кейса"""
    src = CASES_SRC / src_name
    dst = CASES_SRC / dst_category

    if not src.exists():
        print(f"⚠️  Не найдено: {src}")
        return

    dst.mkdir(parents=True, exist_ok=True)

    # Если src_name уже содержит категорию (например, business-impact), просто перемещаем
    if src_name in dst_category:
        print(f"ℹ️  Пропускаем {src_name} (уже в категории)")
        return

    for item in src.iterdir():
        dst_item = dst / item.name
        if dst_item.exists():
            print(f"⚠️  Конфликт: {dst_item} уже существует, пропускаем")
            continue

        if item.is_dir():
            shutil.copytree(item, dst_item)
        else:
            shutil.copy2(item, dst_item)
        print(f"✅ {item.name} → {dst_category}/")


def update_links_in_file(file_path, replacements):
    """Обновить ссылки в файле"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🔗 Обновлены ссылки в: {file_path.name}")


def find_all_markdown_files(directory):
    """Найти все markdown файлы"""
    return list(directory.rglob("*.md"))


def main():
    print("=" * 60)
    print("🚀 Начало консолидации кейсов")
    print("=" * 60)

    # 1. Создаем бэкап текущей структуры
    print("\n📦 Создание бэкапа текущей структуры...")
    if CASES_SRC.exists():
        if CASES_DST.exists():
            shutil.rmtree(CASES_DST)
        shutil.copytree(CASES_SRC, CASES_DST)
        print(f"✅ Бэкап создан: {CASES_DST}")

    # 2. Создаем новую структуру папок
    print("\n📁 Создание новой структуры...")
    for category in NEW_STRUCTURE.keys():
        (CASES_SRC / category).mkdir(exist_ok=True)
        print(f"   + {category}/")

    # 3. Перемещаем кейсы по категориям
    print("\n📤 Перемещение кейсов...")

    # Интеграционные кейсы
    move_case("case-1-it-compass-portfolio-organizer", "integration")
    move_case("case-2-infra-orchestrator-decision-engine", "integration")
    move_case("case-3-system-proof-thought-architecture", "integration")

    # Бизнес-кейсы
    move_case("business-impact", "business")

    # Кейсы мышления
    move_case("thinking-cases", "thinking")

    # Эволюционные кейсы
    move_case("evolution-cases", "evolution")

    # IT-Compass
    move_case("it-compass", "methodology")

    # AI Config Manager (технический кейс)
    move_case("ai-config-manager", "technical")

    # Инфра-синк (технический кейс)
    infra_sync = CASES_SRC / "infra-sync-hardening-2026.md"
    if infra_sync.exists():
        shutil.copy2(infra_sync, CASES_SRC / "technical" / "infra-sync-hardening-2026.md")
        print("✅ infra-sync-hardening-2026.md → technical/")

    # 4. Создаем индексные файлы для категорий
    print("\n📝 Создание индексных файлов категорий...")

    category_indexes = {
        "integration": """# Интеграционные кейсы

Кейсы демонстрации интеграции нескольких сервисов.

| Кейс | Описание |
|------|----------|
| [IT-Compass + Portfolio Organizer](case-1-it-compass-portfolio-organizer/) | Методология оценки компетенций |
| [Infra Orchestrator + Decision Engine](case-2-infra-orchestrator-decision-engine/) | AI Reasoning Engine |
| [System Proof + Thought Architecture](case-3-system-proof-thought-architecture/) | Валидация архитектурных решений |
""",
        "business": """# Бизнес-кейсы (ROI)

Кейсы с расчетом бизнес-ценности и ROI.

| Кейс | Описание |
|------|----------|
| [Onboarding Optimization](business-impact/case-01-onboarding-optimization.md) | Ускорение онбординга в 2.5x |
| [AI Development Acceleration](business-impact/case-02-ai-development-acceleration.md) | Ускорение разработки на 80% |
| [GitOps Operational Efficiency](business-impact/case-03-gitops-operational-efficiency.md) | Снижение операционных затрат |
| [AutoArchitect Engine](autoarchitect.md) | Автоматизация DevOps рутин |
""",
        "thinking": """# Кейсы системного мышления

Аналитические кейсы и шаблоны мышления.

| Кейс | Описание |
|------|----------|
| [AI Communication Breakthrough](01-ai-communication-breakthrough/) | Улучшение коммуникации с ИИ |
| [System Analysis Template](02-system-analysis-template/) | Шаблон системного анализа |
| [Bookmark Architecture Design](03-bookmark-architecture-design/) | Дизайн архитектуры |
| [Documentation Automation](04-documentation-automation/) | Автоматизация документации |
| [Uber Freight Analysis](06-uber-freight-analysis/) | Анализ кейса Uber Freight |
| [Brusnika Analysis](09-brusnika-analysis/) | Анализ кейса Брусники |
""",
        "evolution": """# Эволюционные кейсы

Путь эволюции архитектуры и решений.

| Кейс | Описание |
|------|----------|
| [Knowledge Management](01_knowledge_management/) | Путь от идеи к архитектуре |
| [GigaChain RAG Self-Analysis](06_gigachain_rag_self_analysis/) | RAG для самоанализа |
""",
        "methodology": """# Методологические кейсы

Кейсы применения методологии IT-Compass.

| Кейс | Описание |
|------|----------|
| [Arch-Compass Framework](case-04-arch-compass-framework.md) | Архитектурный фреймворк |
""",
        "technical": """# Технические кейсы

Глубокие технические разборы.

| Кейс | Описание |
|------|----------|
| [AI Config Manager](ai-config-manager/README.md) | Управление AI-сервисами |
| [Technical Deep-Dive](ai-config-manager/TECHNICAL_DEEP_DIVE.md) | Детальный технический анализ |
| [Infra Sync Hardening](infra-sync-hardening-2026.md) | Восстановление после рассинхронизации |
""",
    }

    for category, content in category_indexes.items():
        index_file = CASES_SRC / category / "README.md"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   + {category}/README.md")

    # 5. Обновляем главный README кейсов
    print("\n📝 Обновление docs/cases/README.md...")
    main_readme = CASES_SRC / "README.md"
    with open(main_readme, "w", encoding="utf-8") as f:
        f.write("""# Cases Overview

Коллекция кейсов, демонстрирующих применение методологии, архитектурных решений и бизнес-ценность системы.

## 📂 Навигация по категориям

| Категория | Описание | Ссылка |
|-----------|----------|--------|
| **Интеграционные** | Интеграция нескольких сервисов | [`integration/`](integration/) |
| **Бизнес-кейсы** | ROI и бизнес-ценность | [`business/`](business/) |
| **Системное мышление** | Аналитические кейсы | [`thinking/`](thinking/) |
| **Эволюционные** | Путь эволюции архитектуры | [`evolution/`](evolution/) |
| **Методология** | IT-Compass применение | [`methodology/`](methodology/) |
| **Технические** | Глубокие технические разборы | [`technical/`](technical/) |

## 🔗 Быстрые ссылки для разных аудиторий

### Для HR и рекрутеров
- [Бизнес-кейсы](business/) — ROI и ценность для бизнеса
- [Интеграционные кейсы](integration/) — демонстрация комплексных решений

### Для технических интервьюеров
- [Технические кейсы](technical/) — глубина реализации
- [Системное мышление](thinking/) — подход к решению проблем

### Для себя и развития
- [Эволюционные кейсы](evolution/) — уроки и эволюция решений
- [Методология](methodology/) — применение IT-Compass

## 📚 Архив
Старая структура кейсов доступна в [`archive_original/`](archive_original/) (бэкап перед консолидацией).
""")
    print("✅ docs/cases/README.md обновлен")

    # 6. Обновляем ссылки в других документах
    print("\n🔗 Поиск и обновление ссылок в других документах...")

    # Маппинг старых путей на новые
    link_replacements = {
        # Интеграционные кейсы
        "docs/cases/case-1-it-compass-portfolio-organizer/": "docs/cases/integration/case-1-it-compass-portfolio-organizer/",
        "docs/cases/case-2-infra-orchestrator-decision-engine/": "docs/cases/integration/case-2-infra-orchestrator-decision-engine/",
        "docs/cases/case-3-system-proof-thought-architecture/": "docs/cases/integration/case-3-system-proof-thought-architecture/",
        # Бизнес-кейсы
        "docs/cases/business-impact/": "docs/cases/business/business-impact/",
        # Кейсы мышления
        "docs/cases/thinking-cases/": "docs/cases/thinking/thinking-cases/",
        # Эволюционные
        "docs/cases/evolution-cases/": "docs/cases/evolution/evolution-cases/",
        # IT-Compass
        "docs/cases/it-compass/": "docs/cases/methodology/it-compass/",
        # Технические
        "docs/cases/ai-config-manager/": "docs/cases/technical/ai-config-manager/",
        "docs/cases/infra-sync-hardening-2026.md": "docs/cases/technical/infra-sync-hardening-2026.md",
    }

    # Проверяем все markdown файлы в docs/
    all_md_files = find_all_markdown_files(ROOT / "docs")
    updated_count = 0

    for md_file in all_md_files:
        if "archive_original" in str(md_file):
            continue  # Пропускаем бэкап

        try:
            update_links_in_file(md_file, link_replacements)
            updated_count += 1
        except Exception as e:
            print(f"❌ Ошибка при обработке {md_file}: {e}")

    print(f"✅ Обновлено ссылок в {updated_count} файлах")

    # 7. Создаем редиректы для GitHub Pages
    print("\n🕸️ Создание редиректов для GitHub Pages...")
    redirects_dir = CASES_SRC / "_redirects"
    redirects_dir.mkdir(exist_ok=True)

    redirect_content = """# Редиректы для GitHub Pages
# Этот файл используется для обновления ссылок в документации

## Пример редиректа (нужно добавить в mkdocs.yml или создать HTML-страницы)

Для каждого старого пути создайте HTML-страницу с редиректом:
<html>
  <head>
    <meta http-equiv="refresh" content="0; url=НОВЫЙ_ПУТЬ">
    <title>Страница перемещена</title>
  </head>
  <body>
    <a href="НОВЫЙ_ПУТЬ">Перейти на новую страницу</a>
  </body>
</html>
"""

    with open(redirects_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(redirect_content)

    print("✅ Создана папка для редиректов: docs/cases/_redirects/")

    # 8. Вывод итогов
    print("\n" + "=" * 60)
    print("✅ Консолидация завершена!")
    print("=" * 60)
    print("\n📊 Итоги:")
    print("   - Создан бэкап: docs/cases/archive_original/")
    print(
        "   - Созданы категории: integration/, business/, thinking/, evolution/, methodology/, technical/"
    )
    print("   - Обновлен главный README: docs/cases/README.md")
    print("   - Обновлены ссылки в документах")
    print("   - Созданы индексные файлы для каждой категории")

    print("\n🔜 Следующие шаги:")
    print("   1. Проверить, что все ссылки работают (открыть несколько кейсов)")
    print("   2. Обновить mkdocs.yml (если используется) с новой навигацией")
    print(
        "   3. Закоммитить изменения: git add docs/cases/ && git commit -m 'chore: консолидация кейсов'"
    )
    print(
        "   4. Пушнуть и проверить GitHub Pages: https://control39.github.io/portfolio-system-architect/"
    )

    print("\n⚠️  Важно:")
    print("   - Старая структура сохранена в docs/cases/archive_original/")
    print("   - Для GitHub Pages могут потребоваться редиректы (см. docs/cases/_redirects/)")
    print("   - Проверьте mkdocs.yml и обновите навигацию")


if __name__ == "__main__":
    main()
