#!/usr/bin/env python3
"""recreate_ddd_scripts.py - Пересоздать DDD скрипты"""

from pathlib import Path


def write_script(filepath: Path, content: str) -> None:
    """Записать скрипт с Unix line endings"""
    filepath.write_bytes(content.encode("utf-8"))


def main():
    """Main entry point"""

    # ddd_full_scan.sh
    ddd_full_scan = """#!/usr/bin/env bash
# ddd_full_scan.sh - Полный DDD анализ репозитория

# Используем относительные пути для совместимости с разными ОС
cd "$(dirname "$0")/.."

# Использовать Python напрямую через полный путь
PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

# Проверка
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ Python не найден по пути: $PYTHON_CMD"
    exit 1
fi

echo "=================================================="
echo "  🏗️  ПОЛНЫЙ DDD АНАЛИЗ РЕПОЗИТОРИЯ"
echo "=================================================="
echo ""
echo "📋 Анализируются:"
echo "   - Доменные контексты (Bounded Contexts)"
echo "   - Сущности и агрегаты"
echo "   - Сервисы и репозитории"
echo "   - API контракты"
echo "   - Зависимости между сервисами"
echo "   - Архитектурные проблемы"
echo ""

# Запускаем анализатор
echo "🔍 Запуск анализа..."
"$PYTHON_CMD" scripts/ddd_analyzer.py .

echo ""
echo "✅ Анализ завершен!"
echo ""
echo "📄 Результаты:"
echo "   - ddd_analysis_report.json (детальный JSON)"
echo "   - ddd_analysis_report.txt (человеко-читаемый отчет)"
echo ""
echo "📊 Быстрая статистика:"
if [ -f "ddd_analysis_report.txt" ]; then
    cat ddd_analysis_report.txt | head -50
fi
"""

    write_script(Path("scripts/ddd_full_scan.sh"), ddd_full_scan)
    print("✅ Записан: scripts/ddd_full_scan.sh")

    # ddd_show_dependencies.sh
    ddd_show_deps = """#!/usr/bin/env bash
# ddd_show_dependencies.sh - Показать зависимости между сервисами

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"
"$PYTHON_CMD" scripts/ddd_show_dependencies.py
"""

    write_script(Path("scripts/ddd_show_dependencies.sh"), ddd_show_deps)
    print("✅ Записан: scripts/ddd_show_dependencies.sh")

    # ddd_show_issues.sh
    ddd_show_issues = """#!/usr/bin/env bash
# ddd_show_issues.sh - Показать архитектурные проблемы

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"
"$PYTHON_CMD" scripts/ddd_show_issues.py
"""

    write_script(Path("scripts/ddd_show_issues.sh"), ddd_show_issues)
    print("✅ Записан: scripts/ddd_show_issues.sh")

    # ddd_analyze_context.sh
    ddd_analyze_context = """#!/usr/bin/env bash
# ddd_analyze_context.sh - Анализ конкретного домена

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🏗️ Анализ доменного контекста"
echo "=================================================="
echo ""
echo "Доступные домены:"
if [ -d "apps" ]; then
    ls -la apps/ | grep ^d | awk '{print "   - " $9}'
else
    echo "   (папка apps/ не найдена)"
fi
echo ""

# Запуск с параметром или интерактивно
if [ -n "$1" ]; then
    "$PYTHON_CMD" scripts/ddd_analyze_context.py "$1"
else
    read -p "Введите имя домена для анализа: " domain
    "$PYTHON_CMD" scripts/ddd_analyze_context.py "$domain"
fi
"""

    write_script(Path("scripts/ddd_analyze_context.sh"), ddd_analyze_context)
    print("✅ Записан: scripts/ddd_analyze_context.sh")


if __name__ == "__main__":
    main()
