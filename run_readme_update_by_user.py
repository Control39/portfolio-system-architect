#!/usr/bin/env python3
"""
Скрипт для запуска обновления README по команде пользователя
"""
from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


def update_readme_by_user_command():
    """Функция для обновления README по команде пользователя"""

    print("🚀 Запуск обновления README по команде пользователя...")

    # Создаем агента
    agent = AutonomousCognitiveAgent(project_path=str(REPO_ROOT))

    # Запрашиваем у пользователя путь к сервису
    service_path = input(
        "Введите путь к сервису для обновления README (например, apps/knowledge_graph): ").strip()

    if not service_path:
        service_path = "apps/knowledge_graph"  # Путь по умолчанию

    # Проверяем, что путь существует
    full_path = REPO_ROOT / service_path
    if not full_path.exists():
        print(f"❌ Путь {full_path} не существует")
        return

    # Создаем профиль сервиса
    class ServiceProfile:
        def __init__(self, name, path):
            self.name = name
            self.path = path

    service_name = full_path.name
    service_profile = ServiceProfile(
        name=service_name,
        path=str(full_path)
    )

    print(f"🔧 Подготовлен профиль сервиса: {service_profile.name}")
    print(f"📁 Путь к сервису: {service_profile.path}")

    # Вызываем обновление README
    print("🔄 Выполняем обновление README...")
    result = agent.update_readme_for_service(service_profile)

    print(f"✅ Результат обновления: {result}")

    # Проверяем, что README был создан или обновлен
    readme_path = Path(service_profile.path) / "README.md"
    if readme_path.exists():
        print(f"📄 README успешно обновлён: {readme_path}")
        print(f"📏 Размер файла: {readme_path.stat().st_size} байт")

        # Показываем начало файла
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Первые 500 символов
            print(f"📝 Начало содержимого README:\n{content}...")
    else:
        print(f"❌ README не найден по пути: {readme_path}")

    return result


if __name__ == "__main__":
    update_readme_by_user_command()
