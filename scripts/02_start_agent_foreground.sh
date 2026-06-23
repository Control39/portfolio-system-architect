#!/bin/bash
# 02_start_agent_foreground.sh - Запуск с отображением логов

cd /c/repo
source .venv/Scripts/activate

echo "🟢 Запуск агента в foreground (Ctrl+C для остановки)..."
echo "=================================================="
python agents/cognitive_agent/autonomous_agent_enterprise.py --start --foreground
