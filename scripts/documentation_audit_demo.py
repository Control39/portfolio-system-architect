#!/usr/bin/env python3
"""
Демонстрация работы механизма аудита документации

Этот скрипт показывает, как агент может обнаруживать рассинхронизацию
между документацией и реальным состоянием кода.
"""

import sys
from pathlib import Path

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main():
    print("🚀 Запуск демонстрации аудита документации")
    print("=" * 60)

    # Создаем агента
    agent = AutonomousCognitiveAgent(project_path=str(REPO_ROOT))

    print("\n🔍 Выполняем аудит согласованности документации и кода...")

    # Выполняем аудит документации
    audit_results = agent.audit_documentation_sync()

    print("\n📊 Результаты аудита:")
    print(f"   Время проверки: {audit_results['timestamp']}")
    print(f"   Статус: {audit_results['status']}")
    print(f"   Найдено несоответствий: {audit_results['summary']['total_discrepancies']}")
    print(f"   Высокий приоритет: {audit_results['summary']['severity_counts']['high']}")
    print(f"   Средний приоритет: {audit_results['summary']['severity_counts']['medium']}")
    print(f"   Низкий приоритет: {audit_results['summary']['severity_counts']['low']}")

    if audit_results["discrepancies"]:
        print("\n📝 Обнаруженные несоответствия:")
        for i, discrepancy in enumerate(audit_results["discrepancies"], 1):
            print(f"   {i}. Тип: {discrepancy['type']}")
            print(f"      Файл: {discrepancy['location']}")
            print(f"      Проблема: {discrepancy['issue']}")
            print(f"      Уровень: {discrepancy['severity']}")
            print(f"      Рекомендация: {discrepancy['recommended_action']}")
            print()

    print("\n📋 Генерируем отчет о синхронизации документации...")
    report = agent.generate_documentation_sync_report()
    print(f"\n{report}")

    print("\n✅ Демонстрация завершена")
    print("=" * 60)


if __name__ == "__main__":
    main()
