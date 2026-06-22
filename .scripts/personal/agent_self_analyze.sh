#!/bin/bash
# agent_self_analyze.sh - Агент анализирует сам себя

cd /c/repo
source .venv/Scripts/activate

echo "=================================================="
echo "  🪞 САМОАНАЛИЗ АГЕНТА (Agent Self-Analysis)"
echo "=================================================="
echo ""
echo "Агент будет анализировать:"
echo "   📁 Свой код: agents/cognitive_agent/"
echo "   🧠 Свою архитектуру"
echo "   🔒 Свою безопасность"
echo "   📊 Свою производительность"
echo "   🐛 Свои баги"
echo "   💡 Свои улучшения"
echo ""

python scripts/agent_self_analyze.py
