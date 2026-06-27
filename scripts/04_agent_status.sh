#!/usr/bin/env bash
# 04_agent_status.sh - Проверка статуса агента

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "📊 Статус агента:"
echo "=================================================="

# Проверка запущенных процессов
if pgrep -f "python.*autonomous_agent.py" > /dev/null; then
    echo "✅ Агент запущен"
    echo ""
    echo "Processes:"
    ps aux | grep "python.*autonomous_agent.py" | grep -v grep
else
    echo "❌ Агент не запущен"
fi
