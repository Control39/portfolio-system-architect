#!/usr/bin/env python3
"""
Интерактивный чат с Cognitive Enterprise Agent
"""

import sys
from pathlib import Path

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# Добавляем корень репозитория в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Импортируем enterprise версию агента


def chat_with_agent():
    """Функция для интерактивного чата с агентом"""
    print("🤖 Добро пожаловать в интерактивный чат с Cognitive Enterprise Agent!")
    print("Введите 'quit' или 'exit' для выхода из чата")
    print("Введите 'status' для получения статуса агента")
    print("Введите 'scan' для запуска сканирования проекта")
    print("-" * 50)

    # Создаем экземпляр enterprise агента
    agent = AutonomousCognitiveAgent()

    # Запускаем агента (в фоновом режиме)
    agent.start(background=True)

    try:
        while True:
            user_input = input("\n💬 Вы: ").strip()

            if user_input.lower() in ["quit", "exit", "выйти", "q"]:
                print("👋 Пока! Завершение работы агента...")
                break
            elif user_input.lower() == "status":
                status = agent.get_status()
                print(f"📊 Статус агента: {status}")
            elif user_input.lower() == "scan":
                print("🔍 Запуск сканирования проекта...")
                scan_result = agent.scan_project()
                print("✅ Сканирование завершено!")
                print(f"   Режим: {scan_result.get('mode')}")
                print(f"   Файлов просканировано: {scan_result.get('files', 0)}")
                print(f"   Проблем найдено: {len(scan_result.get('issues', []))}")
                print(f"   Рекомендаций: {len(scan_result.get('recommendations', []))}")
            elif user_input.lower().startswith("task:"):
                task = user_input[5:].strip()  # Убираем 'task:' из начала
                print(f"📝 Выполнение задачи: {task}")
                result = agent.execute_task(task)
                print(f"✅ Результат выполнения задачи: {result}")
            else:
                # Обработка обычного сообщения
                print(f"🤔 Агент получил сообщение: {user_input}")
                print("💡 Пока что агент не может напрямую отвечать на сообщения в чате, но может выполнять команды.")
                print("   Попробуйте команды: status, scan, task:<описание_задачи>")

    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем! Завершение работы агента...")
    finally:
        agent.stop()


if __name__ == "__main__":
    chat_with_agent()
