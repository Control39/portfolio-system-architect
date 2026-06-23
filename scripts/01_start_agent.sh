#!/bin/bash
# 01_start_agent.sh - Запуск агента в фоновом режиме

cd /c/repo
source .venv/Scripts/activate

echo "🚀 Запуск агента в фоновом режиме..."
nohup python agents/cognitive_agent/autonomous_agent_enterprise.py --start > logs/agent.out.log 2>&1 &

echo "✅ Агент запущен (PID: $!)"
echo "📋 Логи: tail -f logs/agent.out.log"
