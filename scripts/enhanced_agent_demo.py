#!/usr/bin/env python3
"""
Демонстрационный скрипт для улучшенного агента с анализом качества кода
"""

import sys
from pathlib import Path

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# Добавляем корень проекта в путь для импорта
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def demo_code_quality_analysis():
    """Демонстрация анализа качества кода"""
    print("🚀 Запуск демонстрации улучшенного агента с анализом качества кода")

    # Создаем агента для текущего репозитория
    agent = AutonomousCognitiveAgent(project_path=str(repo_root))

    print("\n🔍 Запуск анализа качества кода...")
    quality_report = agent.analyze_code_quality()

    print("\n📊 Результаты анализа качества кода:")
    if "error" in quality_report:
        print(f"❌ Ошибка при анализе: {quality_report['error']}")
        return

    print(f"  - Директория проекта: {quality_report['project_path']}")
    print(f"  - Инструментов запущено: {quality_report['tools_run']}")

    summary = quality_report.get("summary", {})
    print(f"  - Всего ошибок типизации: {summary.get('total_errors', 0)}")
    print(f"  - Всего предупреждений: {summary.get('total_warnings', 0)}")
    print(f"  - Проблем безопасности: {summary.get('total_security_issues', 0)}")
    print(f"  - Проблем стиля кода: {summary.get('total_style_issues', 0)}")
    print(f"  - Покрытие тестами: {summary.get('coverage_percentage', 0)}%")

    print(f"\n  - Все хорошо: {'Да' if summary.get('all_good', False) else 'Нет'}")

    print("\n🔧 Доступные инструменты:")
    for tool, available in quality_report.get("tools_available", {}).items():
        status = "✅" if available else "❌"
        print(f"  {status} {tool}: {'Доступен' if available else 'Недоступен'}")

    print("\n📋 Результаты по инструментам:")
    for tool, result in quality_report.get("results", {}).items():
        print(f"  - {tool}: {'Успешно' if result['success'] else 'Ошибка'}, " f"проблем: {result['issue_count']}")

    print("\n📝 Генерация плана улучшения качества кода...")
    improvement_plan = agent.generate_quality_improvement_plan()

    if "error" in improvement_plan:
        print(f"❌ Ошибка при генерации плана: {improvement_plan['error']}")
        return

    print(f"\n📅 План улучшения качества кода (сгенерирован {improvement_plan['timestamp']}):")
    print(f"  - Рекомендаций: {len(improvement_plan['recommendations'])}")
    print(f"  - Приоритетных элементов: {len(improvement_plan['priority_items'])}")

    print("\n🎯 Рекомендации:")
    for i, rec in enumerate(improvement_plan["recommendations"], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['category']}: {rec['description']}")
        print(f"     Действие: {rec['action']}")
        print(f"     Оценка времени: {rec['estimated_time']}")
        print()


def demo_project_scan_with_quality():
    """Демонстрация сканирования проекта с анализом качества кода"""
    print("🔍 Запуск сканирования проекта с анализом качества кода...")

    agent = AutonomousCognitiveAgent(project_path=str(repo_root))

    # Запускаем сканирование проекта
    scan_results = agent.scan_project(mode="full")

    print("\n📋 Результаты сканирования:")
    print(f"  - Режим: {scan_results['mode']}")
    print(f"  - Файлов просканировано: {scan_results['files']}")
    print(f"  - Проблем найдено: {len(scan_results['issues'])}")
    print(f"  - Рекомендаций: {len(scan_results['recommendations'])}")

    # Показываем результаты анализа качества кода
    quality_results = scan_results.get("code_quality", {})
    if quality_results:
        print("\n🔬 Результаты анализа качества кода:")
        summary = quality_results.get("summary", {})
        print(f"  - Ошибок типизации: {summary.get('total_errors', 0)}")
        print(f"  - Предупреждений: {summary.get('total_warnings', 0)}")
        print(f"  - Проблем безопасности: {summary.get('total_security_issues', 0)}")
        print(f"  - Покрытие тестами: {summary.get('coverage_percentage', 0)}%")


if __name__ == "__main__":
    print("🧪 Демонстрация улучшенного агента с анализом качества кода")
    print("=" * 60)

    # Выполняем демонстрацию анализа качества кода
    demo_code_quality_analysis()

    print("\n" + "=" * 60)

    # Выполняем демонстрацию сканирования проекта с анализом качества
    demo_project_scan_with_quality()

    print("\n✅ Демонстрация завершена")
