#!/bin/bash
# 03_stop_agent.sh - Остановка агента

cd /c/repo
source .venv/Scripts/activate

echo "🔴 Остановка агента..."
python agents/cognitive_agent/autonomous_agent_enterprise.py --stop

pkill -f "autonomous_agent_enterprise.py" 2>/dev/null

echo "✅ Агент остановлен"
