#!/bin/bash
# ddd_analyze_context.sh - Анализ конкретного домена

cd /c/repo
source .venv/Scripts/activate

echo "🏗️ Анализ доменного контекста"
echo "=================================================="
echo ""
echo "Доступные домены:"
ls -la apps/ | grep ^d | awk '{print "   - " $9}'
echo ""
read -p "Введите имя домена для анализа: " domain

python scripts/ddd_analyze_context.py "$domain"
