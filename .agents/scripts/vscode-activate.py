#!/usr/bin/env python3
"""
Скрипт активации Cognitive Automation Agent для VS Code.
Запускается автоматически при открытии проекта.
"""

import os
import sys
from pathlib import Path

def activate_cognitive_agent():
    """Активация Cognitive Automation Agent"""
    agent_path = Path(".agents")
    
    if not agent_path.exists():
        print("❌ Директория .agents не найдена")
        return False
    
    # Проверяем конфигурацию
    config_path = agent_path / "config" / "agent-config.yaml"
    if not config_path.exists():
        print("❌ Конфигурационный файл не найден")
        return False
    
    # Запускаем валидацию
    validation_script = agent_path / "tests" / "validation-test.py"
    if validation_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(validation_script)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Cognitive Agent прошел валидацию")
            
            # Запускаем сканирование если автоактивация включена
            launch_script = agent_path / "launch-script.py"
            if launch_script.exists():
                subprocess.Popen(
                    [sys.executable, str(launch_script), "--trigger=project_open"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("🚀 Cognitive Agent активирован")
                return True
        else:
            print("⚠️  Cognitive Agent требует настройки")
            print(result.stdout)
    
    return False

if __name__ == "__main__":
    # Проверяем, запущено ли в VS Code
    vs_code_env = os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode"
    
    if vs_code_env:
        print("🔍 Обнаружена среда VS Code")
        activate_cognitive_agent()
    else:
        print("📁 Запуск вне VS Code, активация пропущена")
