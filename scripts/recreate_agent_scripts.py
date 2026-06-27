#!/usr/bin/env python3
"""recreate_agent_scripts.py - Пересоздать shell скрипты для агента"""

from pathlib import Path


def write_script(filepath: Path, content: str) -> None:
    """Записать скрипт с Unix line endings"""
    filepath.write_bytes(content.encode("utf-8"))


def main():
    """Main entry point"""

    # 01_start_agent.sh
    script_01 = """#!/usr/bin/env bash
# 01_start_agent.sh - Запуск агента в фоновом режиме

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🚀 Запуск агента в фоновом режиме..."
nohup "$PYTHON_CMD" agents/cognitive_agent/autonomous_agent.py > logs/agent.out.log 2>&1 &

echo "✅ Агент запущен (PID: $!)"
echo "📋 Логи: tail -f logs/agent.out.log"
"""

    write_script(Path("scripts/01_start_agent.sh"), script_01)
    print("✅ Записан: scripts/01_start_agent.sh")

    # 02_start_agent_foreground.sh
    script_02 = """#!/usr/bin/env bash
# 02_start_agent_foreground.sh - Запуск агента в foreground

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🟢 Запуск агента (Ctrl+C для остановки)..."
echo "=================================================="
"$PYTHON_CMD" agents/cognitive_agent/autonomous_agent.py
"""

    write_script(Path("scripts/02_start_agent_foreground.sh"), script_02)
    print("✅ Записан: scripts/02_start_agent_foreground.sh")

    # 03_stop_agent.sh
    script_03 = """#!/usr/bin/env bash
# 03_stop_agent.sh - Остановка агента

cd "$(dirname "$0")/.."

PYTHON_CMD="/mnt/c/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python.exe"

echo "🔴 Остановка агента..."

# Поиск и завершение процесса Python с autonomous_agent.py
pkill -f "python.*autonomous_agent.py" 2>/dev/null || true

echo "✅ Агент остановлен"
"""

    write_script(Path("scripts/03_stop_agent.sh"), script_03)
    print("✅ Записан: scripts/03_stop_agent.sh")

    # 04_agent_status.sh
    script_04 = """#!/usr/bin/env bash
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
"""

    write_script(Path("scripts/04_agent_status.sh"), script_04)
    print("✅ Записан: scripts/04_agent_status.sh")

    print("\nВсего обновлено: 4 скрипта")


if __name__ == "__main__":
    main()
