#!/usr/bin/env python3
"""
Скрипт для запуска Cognitive Agent
"""

import sys
from pathlib import Path

# Добавляем корень репозитория в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def run_cognitive_agent():
    """Запуск Cognitive Agent"""
    print("🚀 Запуск Cognitive Automation Agent...")

    try:
        # Импортируем основной класс агента
        from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

        print("✅ Класс агента импортирован")

        # Создаем экземпляр агента
        agent = AutonomousCognitiveAgent()
        print("✅ Enterprise агент создан")

        # Проверяем статус агента
        status = agent.get_status()
        print(f"📊 Статус агента: {status.get('agent_id')}")
        print(f"   Запущен: {status.get('running')}")
        print(f"   Путь проекта: {status.get('project_path')}")
        print(f"   AI провайдер: {status.get('ai_provider')}")

        # Запускаем агента в фоновом режиме
        agent.start(background=True)
        print("✅ Агент запущен в фоновом режиме")

        # Проверяем сканирование
        print("\n🔍 Выполняем начальное сканирование...")
        scan_result = agent.scan_project(mode="auto")
        print("✅ Сканирование завершено")
        print(f"   Режим: {scan_result.get('mode')}")
        print(f"   Файлов просканировано: {scan_result.get('files', 0)}")
        print(f"   Проблем найдено: {len(scan_result.get('issues', []))}")

        # Проверяем рекомендации
        recommendations = scan_result.get("recommendations", [])
        print(f"   Рекомендаций: {len(recommendations)}")

        print("\n🎉 Cognitive Enterprise Agent успешно запущен!")
        print("   API доступен на http://localhost:8000")
        print("   Документация: http://localhost:8000/docs")

        # Оставляем агента работать
        print("\n💡 Агент будет работать в фоне каждые 30 минут")
        print("   Нажмите Ctrl+C для остановки")

        try:
            import time

            while agent.running:
                time.sleep(10)  # Проверяем каждые 10 секунд
        except KeyboardInterrupt:
            print("\n🛑 Остановка агента...")
            agent.stop()
            print("✅ Агент остановлен")

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что все зависимости установлены:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Ошибка запуска агента: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_cognitive_agent()
