#!/usr/bin/env bash
# 03_stop_agent.sh - Остановка агента

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🔴 Остановка агента..."

# Поиск и завершение процесса Python с autonomous_agent.py
pkill -f "python.*autonomous_agent.py" 2>/dev/null || true

echo "✅ Агент остановлен"
