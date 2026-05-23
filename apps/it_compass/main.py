"""
IT Compass — Entry Point

Методология объективного измерения компетенций через 83 маркера в 19 доменах.
Запускает Streamlit UI для визуализации и трекинга навыков.
"""

import subprocess
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.it_compass.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    compass_config = config_manager.get_config()
    print("✅ IT Compass: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(
        f"⚠️  IT Compass: AI Config Manager недоступен ({e}), используется локальный конфиг"
    )
    compass_config = {}


def run_streamlit():
    """Запуск Streamlit приложения"""
    streamlit_script = Path(__file__).parent / "src" / "ui" / "app.py"

    if not streamlit_script.exists():
        # Фолбэк: если UI не найден, запускаем консольную версию
        print("⚠️  Streamlit UI не найден, запускаем консольную версию...")
        from apps.it_compass.src.cli import main

        main()
        return

    port = 8501
    if compass_config:
        port = compass_config.get("it_compass", {}).get("port", 8501)

    print(f"🚀 Запуск IT Compass UI на port {port}...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(streamlit_script),
            "--server.port",
            str(port),
            "--server.address",
            "0.0.0.0",
        ]
    )


if __name__ == "__main__":
    run_streamlit()
