#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обновления README по команде пользователя
"""

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


def test_readme_update():
    """Тестируем обновление README по команде пользователя"""

    print("🚀 Запуск теста обновления README по команде пользователя...")

    # Создаем агента
    agent = AutonomousCognitiveAgent(project_path=str(REPO_ROOT))

    # Создаем профиль сервиса для тестирования
    class ServiceProfile:
        def __init__(self, name, path):
            self.name = name
            self.path = path

    # Тестируем на одном из существующих сервисов
    service_profile = ServiceProfile(
        name="Knowledge Graph Service",
        path=str(REPO_ROOT / "apps" / "knowledge_graph")
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
    test_readme_update()
