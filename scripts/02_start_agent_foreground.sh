#!/usr/bin/env bash
# 02_start_agent_foreground.sh - Запуск агента в foreground

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🟢 Запуск агента (Ctrl+C для остановки)..."
echo "=================================================="
"$PYTHON_CMD" agents/cognitive_agent/autonomous_agent.py
