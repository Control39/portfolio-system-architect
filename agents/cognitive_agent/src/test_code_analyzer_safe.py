"""
Безопасный тестовый скрипт для CodeAnalyzer.

ЗАПУСК:
    python test_code_analyzer_safe.py

НАСТРОЙКИ БЕЗОПАСНОСТИ (по умолчанию):
    - AGENT_ACTIONS_READONLY=1 (запрет изменений файлов)
    - USE_AI_FOR_FIXES=0 (только rule-based фиксы)
    - Анализ тестового файла (не основного кода)
"""

import os
import sys
from pathlib import Path
from typing import Any

# ==================== НАСТРОЙКИ БЕЗОПАСНОСТИ ====================
os.environ["AGENT_ACTIONS_READONLY"] = "1"  # 🔒 ЗАПРЕТ изменений файлов
os.environ["USE_AI_FOR_FIXES"] = "0"  # 🔒 ОТКЛЮЧИТЬ AI (быстрее и безопаснее)
# ================================================================

# Добавляем корень репозитория в sys.path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer, AnalysisTool


def print_header(text: str):
    """Красивый заголовок."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(name: str, value: Any, status: str = "ok"):
    """Статус строка."""
    icons = {"ok": "✅", "warn": "⚠️", "error": "❌", "info": "ℹ️"}
    icon = icons.get(status, "•")
    print(f"{icon} {name:30s}: {value}")


def test_analyzer_initialization():
    """Тест 1: Инициализация анализатора."""
    print_header("ТЕСТ 1: Инициализация анализатора")

    try:
        analyzer = CodeAnalyzer(project_path=".")
        print_status("Создание анализатора", "Успешно", "ok")
        return analyzer
    except Exception as e:
        print_status("Создание анализатора", str(e), "error")
        return None


def test_tools_availability(analyzer: CodeAnalyzer):
    """Тест 2: Проверка доступности инструментов."""
    print_header("ТЕСТ 2: Доступность инструментов анализа")

    tools_status = {
        "MyPy": analyzer.tools_available.get(AnalysisTool.MYPY, False),
        "Ruff": analyzer.tools_available.get(AnalysisTool.RUFF, False),
        "Bandit": analyzer.tools_available.get(AnalysisTool.BANDIT, False),
        "Pyright": analyzer.tools_available.get(AnalysisTool.PYRIGHT, False),
        "Pytest + Coverage": analyzer.tools_available.get(AnalysisTool.PYTEST_COVERAGE, False),
    }

    for tool, available in tools_status.items():
        status = "ok" if available else "warn"
        print_status(tool, "Доступен" if available else "Не доступен", status)

    return tools_status


def test_ai_availability(analyzer: CodeAnalyzer):
    """Тест 3: Проверка доступности AI."""
    print_header("ТЕСТ 3: Доступность AI-ассистентов")

    ai_status = analyzer.ai_available

    print_status("GigaChat", ai_status.get("gigachat", False), "ok" if ai_status.get("gigachat") else "warn")
    print_status("Ollama", ai_status.get("ollama", False), "ok" if ai_status.get("ollama") else "warn")

    if ai_status.get("reason"):
        for reason in ai_status["reason"]:
            print_status("Причина", reason, "info")

    return ai_status


def create_test_file() -> str:
    """Создать тестовый файл с намеренными ошибками."""
    test_content = '''"""Тестовый файл с намеренными ошибками для анализа."""

import os  # unused import
import sys  # unused import
from typing import List

def long_function_name_that_is_too_long(  # line too long (E501)
    param1: str,
    param2: int,
    param3: bool,
    param4: float,
    param5: dict,
) -> None:
    """Функция с проблемами."""
    x = 1  # unused variable (F841)
    y: str = 123  # type error (mypy)
    z: int = "abc"  # type error (mypy)

    # Security issue (bandit)
    eval("print('dangerous')")

    # Style issue (ruff)
    if param1=="test":  # missing whitespace
        print("bad style")

    return None

# Missing type hints
def no_type_hints(a, b, c):
    return a + b + c
'''

    test_file = REPO_ROOT / "test_sample_with_issues.py"
    test_file.write_text(test_content, encoding="utf-8")
    return str(test_file)


def test_analysis(analyzer: CodeAnalyzer):
    """Тест 4: Запуск анализа."""
    print_header("ТЕСТ 4: Анализ тестового файла с ошибками")

    # Создаём тестовый файл
    test_file = create_test_file()
    print_status("Создан тестовый файл", test_file, "info")

    try:
        # Запускаем полный анализ
        print("\n🔍 Запуск анализа...")
        report = analyzer.generate_quality_report()

        print_header("РЕЗУЛЬТАТЫ АНАЛИЗА")
        print_status("Всего инструментов", report["tools_run"], "info")
        print_status(
            "Всего ошибок",
            report["summary"]["total_errors"],
            "error" if report["summary"]["total_errors"] > 0 else "ok",
        )
        print_status(
            "Всего предупреждений",
            report["summary"]["total_warnings"],
            "warn" if report["summary"]["total_warnings"] > 0 else "ok",
        )
        print_status(
            "Security issues",
            report["summary"]["total_security_issues"],
            "error" if report["summary"]["total_security_issues"] > 0 else "ok",
        )
        print_status(
            "Style issues",
            report["summary"]["total_style_issues"],
            "warn" if report["summary"]["total_style_issues"] > 0 else "ok",
        )
        print_status("Coverage %", f"{report['summary']['coverage_percentage']}%", "info")

        # Детали по инструментам
        print_header("ДЕТАЛИ ПО ИНСТРУМЕНТАМ")
        for tool_name, result in report["results"].items():
            status = "✅" if result["success"] else "❌"
            issue_count = result.get("issue_count", 0)
            print(f"{status} {tool_name}: {issue_count} проблем")

        # Метрики производительности
        print_header("МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ")
        metrics = report.get("metrics", {})
        tool_times = metrics.get("tool_execution_times", {})
        for tool, time in tool_times.items():
            print_status(f"Время {tool}", f"{time:.3f}s", "info")

        return report

    except Exception as e:
        print_status("Ошибка анализа", str(e), "error")
        import traceback

        traceback.print_exc()
        return None
    finally:
        # Удаляем тестовый файл
        try:
            Path(test_file).unlink()
            print_status("Тестовый файл удалён", test_file, "info")
        except Exception:
            pass


def test_recommendations(analyzer: CodeAnalyzer):
    """Тест 5: Рекомендации и фиксы."""
    print_header("ТЕСТ 5: Рекомендации по исправлению")

    try:
        results = analyzer.run_analysis_with_recommendations()

        print_status(
            "Всего проблем",
            results["summary"]["total_issues"],
            "warn" if results["summary"]["total_issues"] > 0 else "ok",
        )
        print_status("AI фиксов доступно", results["summary"]["ai_fixes_available"], "info")
        print_status("AI статус", results["summary"]["ai_status"], "info")

        if results["recommendations"]:
            print_header("РЕКОМЕНДАЦИИ")
            for i, rec in enumerate(results["recommendations"][:5], 1):  # Первые 5
                print(f"{i}. {rec}")

        if results["fixes"]:
            print_header("ПРИМЕРЫ ФИКСОВ (первые 3)")
            for i, fix_item in enumerate(results["fixes"][:3], 1):
                issue = fix_item.get("issue", {})
                fix = fix_item.get("fix", "N/A")
                source = fix_item.get("source", "unknown")
                print(f"\n{i}. Проблема: {issue.get('message', 'N/A')[:60]}")
                print(f"   Источник: {source}")
                print(f"   Фикс: {fix[:80]}...")

        return results

    except Exception as e:
        print_status("Ошибка получения рекомендаций", str(e), "error")
        import traceback

        traceback.print_exc()
        return None


def test_readonly_protection(analyzer: CodeAnalyzer):
    """Тест 6: Проверка защиты от изменений (AGENT_ACTIONS_READONLY)."""
    print_header("ТЕСТ 6: Проверка защиты READONLY")

    readonly = os.getenv("AGENT_ACTIONS_READONLY", "0")
    print_status("AGENT_ACTIONS_READONLY", readonly, "ok" if readonly == "1" else "warn")

    if readonly == "1":
        print("✅ Защита активна: apply_fix() будет заблокирован")

        # Проверяем, что apply_fix возвращает None
        test_issue = {
            "tool": "ruff",
            "file": "test.py",
            "line": 1,
            "message": "unused import",
            "severity": "warning",
        }

        try:
            result = analyzer.apply_fix(test_issue, "test.py")
            if result is None:
                print_status("apply_fix() заблокирован", "Correctly blocked", "ok")
            else:
                print_status("apply_fix() сработал", f"Returned {result}", "error")
        except Exception as e:
            print_status("Ошибка при проверке", str(e), "error")
    else:
        print("⚠️ Защита НЕ активна: apply_fix() может изменять файлы!")

    return readonly == "1"


def main():
    """Главная функция."""
    print_header("🔒 БЕЗОПАСНЫЙ ТЕСТ CODE ANALYZER")
    print("Настройки:")
    print(f"  - AGENT_ACTIONS_READONLY = {os.getenv('AGENT_ACTIONS_READONLY', '0')}")
    print(f"  - USE_AI_FOR_FIXES = {os.getenv('USE_AI_FOR_FIXES', '0')}")
    print(f"  - Project path = {REPO_ROOT}")

    results = {
        "initialization": False,
        "tools": {},
        "ai": {},
        "analysis": None,
        "recommendations": None,
        "readonly": False,
    }

    # Тест 1: Инициализация
    analyzer = test_analyzer_initialization()
    if analyzer:
        results["initialization"] = True

        # Тест 2: Инструменты
        results["tools"] = test_tools_availability(analyzer)

        # Тест 3: AI
        results["ai"] = test_ai_availability(analyzer)

        # Тест 4: Анализ
        results["analysis"] = test_analysis(analyzer)

        # Тест 5: Рекомендации
        results["recommendations"] = test_recommendations(analyzer)

        # Тест 6: Защита
        results["readonly"] = test_readonly_protection(analyzer)

    # Итоговый отчёт
    print_header("📊 ИТОГОВЫЙ ОТЧЁТ")

    passed = sum(
        [
            results["initialization"],
            results["readonly"],
            1 if results["analysis"] else 0,
        ]
    )
    total = 5

    print(f"Пройдено тестов: {passed}/{total}")

    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Анализатор безопасен для использования.")
    elif passed >= total - 1:
        print("\n✅ БОЛЬШИНСТВО ТЕСТОВ ПРОЙДЕНО. Можно использовать с осторожностью.")
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. Проверьте настройки.")

    print("\n" + "=" * 60)
    print("Рекомендации:")
    print("  1. Запускайте с AGENT_ACTIONS_READONLY=1 для безопасности")
    print("  2. Проверяйте фиксы перед применением")
    print("  3. Используйте в CI/CD для автоматического анализа")
    print("=" * 60 + "\n")

    return 0 if passed >= total - 1 else 1


if __name__ == "__main__":
    sys.exit(main())
