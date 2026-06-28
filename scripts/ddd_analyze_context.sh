#!/usr/bin/env bash
# ddd_analyze_context.sh - Анализ конкретного домена

# Используем относительные пути для совместимости с разными ОС
cd "$(dirname "$0")/.."

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
    python scripts/ddd_analyze_context.py "$1"
else
    read -p "Введите имя домена для анализа: " domain
    python scripts/ddd_analyze_context.py "$domain"
fi
