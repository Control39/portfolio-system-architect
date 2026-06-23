#!/bin/bash
# 04_agent_status.sh - Проверка статуса агента

cd /c/repo
source .venv/Scripts/activate

echo "📊 Статус агента:"
echo "=================================================="
python agents/cognitive_agent/autonomous_agent_enterprise.py --status

echo ""
echo "📈 Процессы:"
ps aux | grep "autonomous_agent_enterprise.py" | grep -v grep || echo "Агент не запущен"
