#!/usr/bin/env python3
"""
Скрипт проверки состояния окружения для Cognitive Agent
Проверяет виртуальное окружение, зависимости и конфигурацию
"""

import subprocess
import sys
from pathlib import Path


def check_virtual_environment():
    """Проверка виртуального окружения"""
    print("🔍 Проверка виртуального окружения...")

    # Проверяем, активировано ли виртуальное окружение
    venv_path = Path(sys.executable).parent.parent
    if "venv" in str(venv_path) or ".venv" in str(venv_path):
        print(f"✅ Виртуальное окружение активировано: {venv_path}")
        return True
    else:
        print(f"⚠️  Виртуальное окружение НЕ активировано. Текущий Python: {sys.executable}")
        return False


def check_installed_packages():
    """Проверка установленных пакетов"""
    print("\n📦 Проверка установленных пакетов...")

    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True, check=True)
        packages = result.stdout.split("\n")[2:]  # Пропускаем заголовки

        essential_packages = ["fastapi", "pydantic", "uvicorn", "requests", "yaml"]
        found_packages = []

        for pkg in essential_packages:
            if any(pkg in line for line in packages if line.strip()):
                found_packages.append(pkg)

        print(f"✅ Найдены ключевые пакеты: {found_packages}")

        if len(found_packages) == len(essential_packages):
            print("✅ Все ключевые пакеты установлены")
            return True
        else:
            missing = set(essential_packages) - set(found_packages)
            print(f"❌ Отсутствуют пакеты: {missing}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка проверки пакетов: {e}")
        return False


def check_project_structure():
    """Проверка структуры проекта"""
    print("\n📁 Проверка структуры проекта...")

    required_paths = [
        "agents/cognitive_agent",
        "agents/cognitive_agent/main.py",
        "agents/cognitive_agent/autonomous_agent.py",
        "agents/cognitive_agent/config",
        "agents/cognitive_agent/src",
        "agents/cognitive_agent/tests",
        "requirements.txt",
        "docker-compose.yml",
    ]

    repo_root = Path(__file__).parent.parent
    missing_paths = []

    for path in required_paths:
        full_path = repo_root / path
        if not full_path.exists():
            missing_paths.append(path)

    if not missing_paths:
        print("✅ Вся структура проекта на месте")
        return True
    else:
        print(f"❌ Отсутствуют пути: {missing_paths}")
        return False


def check_agent_config():
    """Проверка конфигурации агента"""
    print("\n⚙️  Проверка конфигурации агента...")

    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "agents" / "cognitive_agent" / "config" / "guardrails.yaml"

    if config_path.exists():
        try:
            import yaml

            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Проверяем наличие реальных обязательных полей guardrails
            required_fields = ["allowed_paths", "blocked_patterns", "safe_actions", "rules"]
            missing_fields = [f for f in required_fields if f not in config]

            if not missing_fields:
                print("✅ Конфигурация guardrails содержит все необходимые поля")
                return True
            else:
                print(f"❌ Конфигурация guardrails не содержит: {missing_fields}")
                return False
        except Exception as e:
            print(f"❌ Ошибка чтения конфигурации: {e}")
            return False
    else:
        print("❌ Файл конфигурации guardrails не найден")
        return False


def check_docker_files():
    """Проверка Docker файлов"""
    print("\n🐳 Проверка Docker файлов...")

    repo_root = Path(__file__).parent.parent
    docker_files = ["docker-compose.yml", "agents/cognitive_agent/Dockerfile", "deployment/auth-deployment.yaml"]

    missing_files = []
    for file in docker_files:
        if not (repo_root / file).exists():
            missing_files.append(file)

    if not missing_files:
        print("✅ Все Docker файлы на месте")
        return True
    else:
        print(f"❌ Отсутствуют Docker файлы: {missing_files}")
        return False


def main():
    print("🔬 Скрипт проверки состояния окружения Cognitive Agent")
    print("=" * 60)

    checks = [
        ("Виртуальное окружение", check_virtual_environment),
        ("Установленные пакеты", check_installed_packages),
        ("Структура проекта", check_project_structure),
        ("Конфигурация агента", check_agent_config),
        ("Docker файлы", check_docker_files),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Ошибка в проверке {name}: {e}")
            results[name] = False

    print("\n" + "=" * 60)
    print("📊 Результаты проверки:")

    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}: {'Успешно' if result else 'Ошибка'}")

    overall_success = all(results.values())
    print(f"\n🎯 Общий результат: {'✅ ВСЁ В ПОРЯДКЕ' if overall_success else '❌ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ'}")

    if not overall_success:
        print("\n💡 Рекомендации:")
        for name, result in results.items():
            if not result:
                if name == "Виртуальное окружение":
                    print("  - Активируйте виртуальное окружение: source .venv/Scripts/activate")
                elif name == "Установленные пакеты":
                    print("  - Установите зависимости: pip install -r requirements.txt")
                elif name == "Структура проекта":
                    print("  - Проверьте целостность файлов проекта")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
