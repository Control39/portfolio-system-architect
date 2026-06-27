#!/usr/bin/env bash
# 01_start_agent.sh - Запуск агента в фоновом режиме

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🚀 Запуск агента в фоновом режиме..."
nohup "$PYTHON_CMD" agents/cognitive_agent/autonomous_agent.py > logs/agent.out.log 2>&1 &

echo "✅ Агент запущен (PID: $!)"
echo "📋 Логи: tail -f logs/agent.out.log"
