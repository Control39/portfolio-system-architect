#!/usr/bin/env bash
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
