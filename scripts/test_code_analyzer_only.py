#!/usr/bin/env python3
"""
Тестирование модуля анализа качества кода без запуска всего агента
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer


def test_code_analyzer():
    """Тестирование анализатора кода"""
    print("🚀 Запуск тестирования анализатора качества кода")

    # Создаем анализатор для текущего репозитория
    analyzer = CodeAnalyzer(str(repo_root))

    print(f"\n📁 Директория проекта: {analyzer.project_path}")

    print("\n🔧 Доступные инструменты анализа:")
    for tool, available in analyzer.tools_available.items():
        status = "✅" if available else "❌"
        print(f"  {status} {tool.value}: {'Доступен' if available else 'Недоступен'}")

    print("\n🔍 Выполнение анализа качества кода...")
    quality_report = analyzer.generate_quality_report()

    print("\n📊 Результаты анализа качества кода:")
    print(f"  - Директория проекта: {quality_report['project_path']}")
    print(f"  - Инструментов запущено: {quality_report['tools_run']}")

    summary = quality_report.get("summary", {})
    print(f"  - Всего ошибок типизации: {summary.get('total_errors', 0)}")
    print(f"  - Всего предупреждений: {summary.get('total_warnings', 0)}")
    print(f"  - Проблем безопасности: {summary.get('total_security_issues', 0)}")
    print(f"  - Проблем стиля кода: {summary.get('total_style_issues', 0)}")
    print(f"  - Покрытие тестами: {summary.get('coverage_percentage', 0)}%")

    print(f"\n  - Все хорошо: {'Да' if summary.get('all_good', False) else 'Нет'}")

    print("\n📋 Результаты по инструментам:")
    for tool, result in quality_report.get("results", {}).items():
        print(f"  - {tool}: {'Успешно' if result['success'] else 'Ошибка'}, " f"проблем: {result['issue_count']}")


if __name__ == "__main__":
    print("🧪 Тестирование модуля анализа качества кода")
    print("=" * 50)

    test_code_analyzer()

    print("\n✅ Тестирование завершено")
