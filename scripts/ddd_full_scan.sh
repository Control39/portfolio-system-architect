#!/bin/bash
# ddd_full_scan.sh - Полный DDD анализ репозитория

cd /c/repo
source .venv/Scripts/activate

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
python scripts/ddd_analyzer.py .

echo ""
echo "✅ Анализ завершен!"
echo ""
echo "📄 Результаты:"
echo "   - ddd_analysis_report.json (детальный JSON)"
echo "   - ddd_analysis_report.txt (человеко-читаемый отчет)"
echo ""
echo "📊 Быстрая статистика:"
cat ddd_analysis_report.txt | head -50
