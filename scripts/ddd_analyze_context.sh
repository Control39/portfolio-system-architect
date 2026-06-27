#!/usr/bin/env bash
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
