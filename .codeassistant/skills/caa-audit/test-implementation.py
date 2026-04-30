#!/usr/bin/env python3
"""
Тестовый скрипт для проверки реализации Фазы 1 PMR Agent
Проверка режима caa-audit и проактивных триггеров
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml


class Phase1Tester:
    """Тестер реализации Фазы 1"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_results = {
            "test_date": datetime.now().isoformat(),
            "phase": "1",
            "tests": [],
            "summary": {},
            "recommendations": [],
        }

    def run_all_tests(self) -> Dict:
        """Запуск всех тестов Фазы 1"""
        print("🧪 Запуск тестов реализации Фазы 1 PMR Agent...")
        print("=" * 60)

        # 1. Тест структуры файлов
        self._test_file_structure()

        # 2. Тест конфигурации
        self._test_configuration()

        # 3. Тест скрипта аудита
        self._test_audit_script()

        # 4. Тест интеграции с CAA
        self._test_caa_integration()

        # 5. Тест Git хуков
        self._test_git_hooks()

        # 6. Тест производительности
        self._test_performance()

        # Расчет итоговой оценки
        self._calculate_summary()

        return self.test_results

    def _test_file_structure(self):
        """Тест структуры файлов"""
        print("📁 Тест структуры файлов...")

        required_files = [
            ".codeassistant/skills/caa-audit/SKILL.md",
            ".codeassistant/skills/caa-audit/caa-audit-script.py",
            ".codeassistant/skills/caa-audit/pmr-triggers.yaml",
            ".codeassistant/skills/caa-audit/activate-triggers.py",
            ".codeassistant/skills/caa-audit/DEVELOPMENT_PLANS.md",
            ".codeassistant/skills/caa-audit/test-implementation.py",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.test_results["tests"].append(
                    {
                        "name": f"file_exists_{Path(file_path).name}",
                        "status": "passed",
                        "message": f"Файл найден: {file_path}",
                        "details": f"Размер: {full_path.stat().st_size} байт",
                    }
                )
            else:
                self.test_results["tests"].append(
                    {
                        "name": f"file_exists_{Path(file_path).name}",
                        "status": "failed",
                        "message": f"Файл не найден: {file_path}",
                        "recommendation": f"Создать файл: {file_path}",
                    }
                )

    def _test_configuration(self):
        """Тест конфигурационных файлов"""
        print("⚙️  Тест конфигурационных файлов...")

        # Тест YAML конфигурации
        config_files = [".codeassistant/skills/caa-audit/pmr-triggers.yaml"]

        for config_file in config_files:
            full_path = self.project_root / config_file
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f)

                    # Проверка обязательных полей
                    required_fields = ["version", "triggers", "integration"]
                    missing_fields = []

                    for field in required_fields:
                        if field not in config:
                            missing_fields.append(field)

                    if missing_fields:
                        self.test_results["tests"].append(
                            {
                                "name": f"config_valid_{Path(config_file).name}",
                                "status": "failed",
                                "message": f"В конфигурации {config_file} отсутствуют поля: {', '.join(missing_fields)}",
                                "recommendation": "Добавить обязательные поля в конфигурацию",
                            }
                        )
                    else:
                        triggers_count = len(config.get("triggers", {}))
                        self.test_results["tests"].append(
                            {
                                "name": f"config_valid_{Path(config_file).name}",
                                "status": "passed",
                                "message": f"Конфигурация {config_file} валидна",
                                "details": f"Настроено {triggers_count} триггеров, версия: {config.get('version')}",
                            }
                        )

                except yaml.YAMLError as e:
                    self.test_results["tests"].append(
                        {
                            "name": f"config_valid_{Path(config_file).name}",
                            "status": "failed",
                            "message": f"Ошибка YAML в {config_file}: {e}",
                            "recommendation": "Исправить синтаксис YAML",
                        }
                    )

    def _test_audit_script(self):
        """Тест скрипта аудита"""
        print("🔍 Тест скрипта аудита...")

        audit_script = (
            self.project_root / ".codeassistant/skills/caa-audit/caa-audit-script.py"
        )

        if audit_script.exists():
            # Тест 1: Проверка синтаксиса Python
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(audit_script)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    self.test_results["tests"].append(
                        {
                            "name": "audit_script_syntax",
                            "status": "passed",
                            "message": "Синтаксис скрипта аудита корректен",
                            "details": "Проверка py_compile пройдена",
                        }
                    )
                else:
                    self.test_results["tests"].append(
                        {
                            "name": "audit_script_syntax",
                            "status": "failed",
                            "message": "Ошибка синтаксиса в скрипте аудита",
                            "details": result.stderr[:200],
                            "recommendation": "Исправить синтаксические ошибки в Python коде",
                        }
                    )

            except subprocess.TimeoutExpired:
                self.test_results["tests"].append(
                    {
                        "name": "audit_script_syntax",
                        "status": "warning",
                        "message": "Проверка синтаксиса превысила таймаут",
                        "recommendation": "Упростить скрипт или увеличить таймаут",
                    }
                )

            # Тест 2: Быстрый запуск аудита
            try:
                result = subprocess.run(
                    [sys.executable, str(audit_script), "--quick", "--format=text"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    output_lines = len(result.stdout.split("\n"))
                    self.test_results["tests"].append(
                        {
                            "name": "audit_script_execution",
                            "status": "passed",
                            "message": "Скрипт аудита успешно выполнен",
                            "details": f"Вывод: {output_lines} строк, код возврата: {result.returncode}",
                        }
                    )
                else:
                    self.test_results["tests"].append(
                        {
                            "name": "audit_script_execution",
                            "status": "failed",
                            "message": "Скрипт аудита завершился с ошибкой",
                            "details": f"Код возврата: {result.returncode}, stderr: {result.stderr[:200]}",
                            "recommendation": "Исправить ошибки выполнения скрипта",
                        }
                    )

            except subprocess.TimeoutExpired:
                self.test_results["tests"].append(
                    {
                        "name": "audit_script_execution",
                        "status": "failed",
                        "message": "Скрипт аудита превысил таймаут (30 сек)",
                        "recommendation": "Оптимизировать производительность скрипта",
                    }
                )

    def _test_caa_integration(self):
        """Тест интеграции с CAA"""
        print("🔗 Тест интеграции с CAA...")

        # Проверка существования конфигурации CAA
        caa_configs = [".agents/config/triggers.yaml", ".agents/config/git-hooks.yaml"]

        for config_file in caa_configs:
            full_path = self.project_root / config_file
            if full_path.exists():
                self.test_results["tests"].append(
                    {
                        "name": f"caa_config_exists_{Path(config_file).name}",
                        "status": "passed",
                        "message": f"Конфигурация CAA найдена: {config_file}",
                        "details": "Интеграция возможна",
                    }
                )
            else:
                self.test_results["tests"].append(
                    {
                        "name": f"caa_config_exists_{Path(config_file).name}",
                        "status": "warning",
                        "message": f"Конфигурация CAA не найдена: {config_file}",
                        "recommendation": "Создать файл или настроить интеграцию вручную",
                    }
                )

        # Проверка директории .agents/
        agents_dir = self.project_root / ".agents"
        if agents_dir.exists():
            subdirs = [d.name for d in agents_dir.iterdir() if d.is_dir()]
            self.test_results["tests"].append(
                {
                    "name": "caa_structure_exists",
                    "status": "passed",
                    "message": "Директория .agents/ существует",
                    "details": f"Поддиректории: {', '.join(subdirs[:5])}",
                }
            )
        else:
            self.test_results["tests"].append(
                {
                    "name": "caa_structure_exists",
                    "status": "failed",
                    "message": "Директория .agents/ не найдена",
                    "recommendation": "Создать структуру CAA или настроить интеграцию",
                }
            )

    def _test_git_hooks(self):
        """Тест Git хуков"""
        print("🪝 Тест Git хуков...")

        # Проверка директории Git хуков
        git_hooks_dir = self.project_root / ".codeassistant/skills/caa-audit/git-hooks"

        if git_hooks_dir.exists():
            hooks = list(git_hooks_dir.glob("*"))
            hook_files = [h.name for h in hooks if h.is_file()]

            self.test_results["tests"].append(
                {
                    "name": "git_hooks_directory",
                    "status": "passed",
                    "message": "Директория Git хуков существует",
                    "details": f"Файлы: {', '.join(hook_files)}",
                }
            )

            # Проверка исполняемости хуков
            for hook_file in hooks:
                if hook_file.is_file():
                    is_executable = os.access(hook_file, os.X_OK)
                    if is_executable:
                        self.test_results["tests"].append(
                            {
                                "name": f"git_hook_executable_{hook_file.name}",
                                "status": "passed",
                                "message": f"Git хук исполняем: {hook_file.name}",
                                "details": "Права на выполнение установлены",
                            }
                        )
                    else:
                        self.test_results["tests"].append(
                            {
                                "name": f"git_hook_executable_{hook_file.name}",
                                "status": "failed",
                                "message": f"Git хук не исполняем: {hook_file.name}",
                                "recommendation": f"Установить права выполнения: chmod +x {hook_file}",
                            }
                        )
        else:
            self.test_results["tests"].append(
                {
                    "name": "git_hooks_directory",
                    "status": "warning",
                    "message": "Директория Git хуков не найдена",
                    "recommendation": "Создать директорию: mkdir -p .codeassistant/skills/caa-audit/git-hooks",
                }
            )

    def _test_performance(self):
        """Тест производительности"""
        print("⚡ Тест производительности...")

        # Тест времени выполнения быстрого аудита
        audit_script = (
            self.project_root / ".codeassistant/skills/caa-audit/caa-audit-script.py"
        )

        if audit_script.exists():
            import time

            try:
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, str(audit_script), "--quick", "--format=text"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.project_root,
                )
                end_time = time.time()

                execution_time = end_time - start_time

                if execution_time < 30:
                    self.test_results["tests"].append(
                        {
                            "name": "performance_quick_audit",
                            "status": "passed",
                            "message": "Быстрый аудит выполняется быстро",
                            "details": f"Время выполнения: {execution_time:.2f} сек",
                        }
                    )
                elif execution_time < 60:
                    self.test_results["tests"].append(
                        {
                            "name": "performance_quick_audit",
                            "status": "warning",
                            "message": "Быстрый аудит выполняется медленно",
                            "details": f"Время выполнения: {execution_time:.2f} сек (цель: <30 сек)",
                            "recommendation": "Оптимизировать производительность скрипта",
                        }
                    )
                else:
                    self.test_results["tests"].append(
                        {
                            "name": "performance_quick_audit",
                            "status": "failed",
                            "message": "Быстрый аудит выполняется слишком медленно",
                            "details": f"Время выполнения: {execution_time:.2f} сек",
                            "recommendation": "Существенно оптимизировать скрипт или уменьшить объём проверок",
                        }
                    )

            except subprocess.TimeoutExpired:
                self.test_results["tests"].append(
                    {
                        "name": "performance_quick_audit",
                        "status": "failed",
                        "message": "Быстрый аудит превысил таймаут (60 сек)",
                        "recommendation": "Существенно оптимизировать производительность",
                    }
                )

    def _calculate_summary(self):
        """Расчёт итоговой оценки"""
        print("📊 Расчёт итоговой оценки...")

        tests = self.test_results["tests"]

        # Статистика по тестам
        total_tests = len(tests)
        passed_tests = len([t for t in tests if t["status"] == "passed"])
        failed_tests = len([t for t in tests if t["status"] == "failed"])
        warning_tests = len([t for t in tests if t["status"] == "warning"])

        # Оценка в процентах
        if total_tests > 0:
            score_percentage = (passed_tests / total_tests) * 100
        else:
            score_percentage = 0

        # Определение статуса реализации
        if score_percentage >= 80:
            implementation_status = "✅ Отлично"
            phase_status = "Готово к использованию"
        elif score_percentage >= 60:
            implementation_status = "⚠️  Удовлетворительно"
            phase_status = "Требует доработок"
        else:
            implementation_status = "❌ Неудовлетворительно"
            phase_status = "Требует значительных доработок"

        # Критические проблемы
        critical_issues = [t for t in tests if t["status"] == "failed"]

        # Рекомендации
        recommendations = []
        for test in tests:
            if "recommendation" in test:
                recommendations.append(
                    {
                        "test": test["name"],
                        "recommendation": test["recommendation"],
                        "priority": "high" if test["status"] == "failed" else "medium",
                    }
                )

        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warning_tests": warning_tests,
            "score_percentage": round(score_percentage, 1),
            "implementation_status": implementation_status,
            "phase_status": phase_status,
            "critical_issues_count": len(critical_issues),
        }

        self.test_results["recommendations"] = recommendations

    def generate_report(
        self, output_format: str = "markdown", output_path: str = None
    ) -> str:
        """Генерация отчёта о тестировании"""

        if output_format == "markdown":
            report = self._generate_markdown_report()
        elif output_format == "json":
            report = json.dumps(self.test_results, indent=2, ensure_ascii=False)
        else:
            report = str(self.test_results)

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding="utf-8")
            print(f"📄 Отчёт о тестировании сохранён: {output_path}")

        return report

    def _generate_markdown_report(self) -> str:
        """Генерация Markdown отчёта"""

        summary = self.test_results["summary"]

        report = f"""# Отчёт тестирования реализации Фазы 1 PMR Agent

**Дата тестирования**: {self.test_results['test_date']}
**Фаза**: {self.test_results['phase']}

## 📊 Итоговая оценка

| Метрика | Значение |
|---------|----------|
| Всего тестов | {summary['total_tests']} |
| Пройдено успешно | {summary['passed_tests']} |
| Провалено | {summary['failed_tests']} |
| Предупреждения | {summary['warning_tests']} |
| **Оценка** | **{summary['score_percentage']}%** |
| **Статус реализации** | **{summary['implementation_status']}** |
| **Статус фазы** | **{summary['phase_status']}** |

## 🔍 Результаты тестов

### ✅ Успешные тесты ({summary['passed_tests']})
"""

        passed_tests = [
            t for t in self.test_results["tests"] if t["status"] == "passed"
        ]
        for test in passed_tests[:10]:  # Показываем первые 10 успешных тестов
            report += f"- **{test['name']}**: {test['message']}\n"
            if test.get("details"):
                report += f"  *{test['details']}*\n"

        if summary["failed_tests"] > 0:
            report += f"\n### ❌ Проваленные тесты ({summary['failed_tests']})\n"
            failed_tests = [
                t for t in self.test_results["tests"] if t["status"] == "failed"
            ]
            for test in failed_tests:
                report += f"- **{test['name']}**: {test['message']}\n"
                if test.get("details"):
                    report += f"  *{test['details']}*\n"
                if test.get("recommendation"):
                    report += f"  💡 **Рекомендация**: {test['recommendation']}\n"

        if summary["warning_tests"] > 0:
            report += (
                f"\n### ⚠️  Тесты с предупреждениями ({summary['warning_tests']})\n"
            )
            warning_tests = [
                t for t in self.test_results["tests"] if t["status"] == "warning"
            ]
            for test in warning_tests:
                report += f"- **{test['name']}**: {test['message']}\n"
                if test.get("details"):
                    report += f"  *{test['details']}*\n"
                if test.get("recommendation"):
                    report += f"  💡 **Рекомендация**: {test['recommendation']}\n"

        if self.test_results["recommendations"]:
            report += "\n## 🎯 Рекомендации по улучшению\n"

            high_priority = [
                r
                for r in self.test_results["recommendations"]
                if r["priority"] == "high"
            ]
            medium_priority = [
                r
                for r in self.test_results["recommendations"]
                if r["priority"] == "medium"
            ]

            if high_priority:
                report += "### 🔴 Высокий приоритет\n"
                for rec in high_priority:
                    report += f"- **{rec['test']}**: {rec['recommendation']}\n"

            if medium_priority:
                report += "### 🟡 Средний приоритет\n"
                for rec in medium_priority:
                    report += f"- **{rec['test']}**: {rec['recommendation']}\n"

        report += f"""

## 📈 Заключение

### Оценка реализации Фазы 1:
**{summary['score_percentage']}%** - {
    "Отличная реализация" if summary['score_percentage'] >= 80 else
    "Хорошая реализация с незначительными проблемами" if summary['score_percentage'] >= 60 else
    "Требует значительных доработок"
}

### Ключевые сильные стороны:
1. **Структура файлов**: {'✅ Полная' if summary['passed_tests'] > summary['total_tests'] * 0.8 else '⚠️ Частичная' if summary['passed_tests'] > summary['total_tests'] * 0.6 else '❌ Неполная'}
2. **Интеграция с CAA**: {'✅ Настроена' if 'caa_config_exists_triggers.yaml' in [t['name'] for t in passed_tests] else '⚠️ Частичная' if 'caa_structure_exists' in [t['name'] for t in passed_tests] else '❌ Отсутствует'}
3. **Производительность**: {'✅ Оптимальная' if 'performance_quick_audit' in [t['name'] for t in passed_tests] else '⚠️ Приемлемая' if 'performance_quick_audit' in [t['name'] for t in warning_tests] else '❌ Требует оптимизации'}

### Следующие шаги:
1. **Исправить критические проблемы**: {len([t for t in self.test_results['tests'] if t['status'] == 'failed'])} шт.
2. **Активировать триггеры**: `python .codeassistant/skills/caa-audit/activate-triggers.py`
3. **Запустить тестовый аудит**: `python .codeassistant/skills/caa-audit/caa-audit-script.py --quick`
4. **Перейти к Фазе 2**: После достижения оценки ≥80%

---

*Отчёт сгенерирован автоматически Phase 1 Tester*
"""

        return report


def main():
    parser = argparse.ArgumentParser(description="Тестер реализации Фазы 1 PMR Agent")
    parser.add_argument(
        "--project-root", default=".", help="Корневая директория проекта"
    )
    parser.add_argument("--output", help="Путь для сохранения отчёта")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Формат вывода",
    )
    parser.add_argument("--quick", action="store_true", help="Только критические тесты")

    args = parser.parse_args()

    tester = Phase1Tester(args.project_root)
    results = tester.run_all_tests()

    # Генерация отчёта
    report = tester.generate_report(args.format, args.output)

    if not args.output:
        print("\n" + "=" * 60)
        print(report)

    # Вывод итоговой оценки
    summary = results["summary"]
    print(f"\n🎯 Итоговая оценка реализации Фазы 1: {summary['score_percentage']}%")
    print(f"📊 Статус: {summary['implementation_status']}")

    if summary["score_percentage"] >= 80:
        print("✅ Фаза 1 готова к использованию! Можно переходить к активации.")
        sys.exit(0)
    elif summary["score_percentage"] >= 60:
        print("⚠️  Фаза 1 требует доработок перед использованием.")
        sys.exit(1)
    else:
        print("❌ Фаза 1 требует значительных доработок.")
        sys.exit(2)


if __name__ == "__main__":
    main()
