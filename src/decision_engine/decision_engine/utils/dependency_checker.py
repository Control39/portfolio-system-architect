# components/cloud-reason/utils/dependency_checker.py
import subprocess
import sys

import pkg_resources

from ..config.loader import COMPONENT_CONFIG
from ..config.utils import get_env_variables


def check_dependencies():
    """Проверяет установленные зависимости против требований конфигурации."""
    required = COMPONENT_CONFIG["dependencies"]["python"]
    missing = []

    for requirement in required:
        try:
            pkg_resources.require(requirement)
        except pkg_resources.DistributionNotFound:
            missing.append(requirement)

    if missing:
        print(f"❌ Отсутствуют зависимости: {missing}")
        install_cmd = f"pip install {' '.join(missing)}"
        print(f"Установите их командой: {install_cmd}")

        # Автоустановка (опционально)
        confirm = input("Установить автоматически? (y/n): ")
        if confirm.lower() == "y":
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        else:
            sys.exit(1)
    else:
        print("✅ Все зависимости установлены")

def print_env_requirements():
    """Выводит список требуемых переменных окружения."""
    env_vars = get_env_variables()
    print("\n🔧 Требуемые переменные окружения:")
    for var in env_vars:
        print(f"  - {var['name']}: {var['description']}")

if __name__ == "__main__":
    check_dependencies()
    print_env_requirements()


