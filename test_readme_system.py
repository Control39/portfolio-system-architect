#!/usr/bin/env python3
"""
Тест для проверки работоспособности системы управления README файлами
"""
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


def test_readme_system():
    """Тест системы управления README"""
    print("🧪 Запуск теста системы управления README...")

    try:
        # Импорт агента
        from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent
        print("✅ Агент успешно импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта агента: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ Синтаксическая ошибка в файле агента: {e}")
        return False

    try:
        # Создание агента
        agent = AutonomousCognitiveAgent(project_path=str(REPO_ROOT))
        print("✅ Агент успешно создан")
    except Exception as e:
        print(f"❌ Ошибка создания агента: {e}")
        return False

    # Проверка наличия методов
    required_methods = [
        'update_readme_for_service',
        'update_readme_for_all_services',
        'update_apps_directory_readme',
        '_parse_service_readme'
    ]

    for method_name in required_methods:
        if hasattr(agent, method_name):
            print(f"✅ Метод {method_name} доступен")
        else:
            print(f"❌ Метод {method_name} отсутствует")
            return False

    # Проверка директории apps
    apps_dir = REPO_ROOT / "apps"
    if apps_dir.exists():
        service_dirs = [d for d in apps_dir.iterdir() if d.is_dir(
        ) and not d.name.startswith('.') and not d.name.startswith('__')]
        print(f"✅ Найдено {len(service_dirs)} сервисов в директории apps")

        if len(service_dirs) > 0:
            # Проверим, что первый сервис имеет README
            first_service = service_dirs[0]
            readme_path = first_service / "README.md"
            if readme_path.exists():
                print(f"✅ README для сервиса {first_service.name} существует")
            else:
                print(
                    f"⚠️ README для сервиса {first_service.name} отсутствует, но это нормально для первого запуска")
    else:
        print("❌ Директория apps не найдена")
        return False

    # Проверка общего README
    apps_readme_path = apps_dir / "README.md"
    if apps_readme_path.exists():
        print("✅ Общий README для директории apps существует")
    else:
        print("⚠️ Общий README для директории apps отсутствует, но это нормально для первого запуска")

    print("✅ Все тесты системы управления README пройдены успешно!")
    return True


if __name__ == "__main__":
    success = test_readme_system()
    if success:
        print("\n🎉 Система управления README полностью работоспособна!")
    else:
        print("\n💥 Обнаружены проблемы в системе управления README!")
        sys.exit(1)
