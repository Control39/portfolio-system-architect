#!/usr/bin/env python3
"""Health check для проверки работоспособности Cognitive Automation Agent и SourceCraft Agent Skills
"""

import json
import os
import sys
from datetime import datetime

import yaml


class HealthChecker:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()

    def log(self, level, message, component=None):
        """Логирование результата проверки"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "component": component,
            "message": message,
        }
        self.results.append(result)

        # Вывод в консоль
        prefix = f"[{level.upper():8}]"
        if component:
            prefix += f" [{component}]"
        print(f"{prefix} {message}")

        return level == "success"

    def check_agents_structure(self):
        """Проверка структуры Cognitive Automation Agent"""
        component = "CAA Structure"

        # Проверка обязательных директорий
        required_dirs = [
            ".agents/config",
            ".agents/skills",
            ".agents/changelogs",
            ".agents/scripts",
        ]

        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self.log("success", f"Директория существует: {dir_path}", component)
            else:
                self.log("error", f"Директория отсутствует: {dir_path}", component)
                return False

        # Проверка обязательных файлов
        required_files = [
            ".agents/config/agent-config.yaml",
            ".agents/config/triggers.yaml",
            ".agents/README.md",
        ]

        for file_path in required_files:
            if os.path.exists(file_path):
                self.log("success", f"Файл существует: {file_path}", component)
            else:
                self.log("warning", f"Файл отсутствует: {file_path}", component)

        return True

    def check_codeassistant_structure(self):
        """Проверка структуры SourceCraft Agent Skills"""
        component = "SourceCraft Structure"

        # Проверка обязательных директорий
        required_dirs = [
            ".codeassistant/skills",
        ]

        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self.log("success", f"Директория существует: {dir_path}", component)
            else:
                self.log("error", f"Директория отсутствует: {dir_path}", component)
                return False

        # Проверка обязательных файлов
        required_files = [
            ".codeassistant/context.md",
            ".codeassistant/mcp.json",
        ]

        for file_path in required_files:
            if os.path.exists(file_path):
                self.log("success", f"Файл существует: {file_path}", component)
            else:
                self.log("warning", f"Файл отсутствует: {file_path}", component)

        # Проверка skill caa-audit
        caa_audit_path = ".codeassistant/skills/caa-audit/SKILL.md"
        if os.path.exists(caa_audit_path):
            self.log("success", f"Skill caa-audit существует: {caa_audit_path}", component)
        else:
            self.log("warning", f"Skill caa-audit отсутствует: {caa_audit_path}", component)

        return True

    def check_architecture_documentation(self):
        """Проверка архитектурной документации"""
        component = "Architecture Documentation"

        required_files = [
            "ARCHITECTURE.md",
            "diagrams/agents-codeassistant-dependencies.mmd",
        ]

        for file_path in required_files:
            if os.path.exists(file_path):
                self.log("success", f"Документация существует: {file_path}", component)
            else:
                self.log("warning", f"Документация отсутствует: {file_path}", component)

        return True

    def check_ci_cd_workflow(self):
        """Проверка CI/CD workflow"""
        component = "CI/CD Workflow"

        workflow_path = ".github/workflows/agents-codeassistant-compatibility.yml"
        if os.path.exists(workflow_path):
            self.log("success", f"CI/CD workflow существует: {workflow_path}", component)

            # Проверка синтаксиса YAML
            try:
                with open(workflow_path) as f:
                    yaml.safe_load(f)
                self.log("success", "CI/CD workflow имеет валидный YAML синтаксис", component)
            except yaml.YAMLError as e:
                self.log("error", f"Ошибка синтаксиса YAML: {e}", component)
                return False
        else:
            self.log("warning", f"CI/CD workflow отсутствует: {workflow_path}", component)

        return True

    def check_agents_operational_status(self):
        """Проверка операционного статуса Cognitive Automation Agent"""
        component = "CAA Operational Status"

        # Проверка статусов планировщика и сканера
        status_files = [
            ".agents/plans/last_plan_status.json",
            ".agents/scans/last_scan_status.json",
        ]

        for status_file in status_files:
            if os.path.exists(status_file):
                try:
                    with open(status_file) as f:
                        status = json.load(f)

                    # Проверка наличия ключевых полей
                    if "status" in status:
                        status_value = status["status"]
                        self.log(
                            "success",
                            f"Статус файла {status_file}: {status_value}",
                            component,
                        )
                    else:
                        self.log(
                            "warning",
                            f"Статус файла {status_file} не содержит поле 'status'",
                            component,
                        )
                except json.JSONDecodeError as e:
                    self.log(
                        "error",
                        f"Ошибка чтения JSON файла {status_file}: {e}",
                        component,
                    )
            else:
                self.log("warning", f"Статус файл отсутствует: {status_file}", component)

        return True

    def check_changelog_integrity(self):
        """Проверка целостности changelog"""
        component = "Changelog Integrity"

        changelog_path = ".agents/changelogs/"
        if os.path.exists(changelog_path):
            changelog_files = [f for f in os.listdir(changelog_path) if f.endswith(".md")]

            if changelog_files:
                latest_changelog = max(changelog_files)
                full_path = os.path.join(changelog_path, latest_changelog)

                try:
                    with open(full_path) as f:
                        content = f.read()

                    # Проверка наличия ключевых разделов
                    required_sections = ["Коммит:", "Дата:", "Автор:", "Сообщение:"]
                    missing_sections = []

                    for section in required_sections:
                        if section not in content:
                            missing_sections.append(section)

                    if missing_sections:
                        self.log(
                            "warning",
                            f"В changelog отсутствуют разделы: {missing_sections}",
                            component,
                        )
                    else:
                        self.log(
                            "success",
                            f"Changelog {latest_changelog} имеет правильную структуру",
                            component,
                        )
                except Exception as e:
                    self.log("error", f"Ошибка чтения changelog: {e}", component)
            else:
                self.log("warning", "Нет файлов changelog в директории", component)
        else:
            self.log("warning", "Директория changelogs отсутствует", component)

        return True

    def generate_report(self):
        """Генерация отчета о health check"""
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "checks_performed": len(self.results),
            "results": self.results,
            "summary": {
                "success": sum(1 for r in self.results if r["level"] == "success"),
                "warning": sum(1 for r in self.results if r["level"] == "warning"),
                "error": sum(1 for r in self.results if r["level"] == "error"),
            },
        }

        # Сохранение отчета в файл
        report_dir = ".agents/health-reports"
        os.makedirs(report_dir, exist_ok=True)

        report_file = os.path.join(
            report_dir, f"health-check-{self.start_time.strftime('%Y%m%d-%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log("success", f"Отчет сохранен: {report_file}", "Health Check")

        return report_file

    def run_all_checks(self):
        """Запуск всех проверок"""
        print("=" * 80)
        print("🚀 ЗАПУСК HEALTH CHECK ДЛЯ COGNITIVE AUTOMATION AGENT И SOURCECRAFT AGENT SKILLS")
        print("=" * 80)

        checks = [
            (
                "Проверка структуры Cognitive Automation Agent",
                self.check_agents_structure,
            ),
            (
                "Проверка структуры SourceCraft Agent Skills",
                self.check_codeassistant_structure,
            ),
            (
                "Проверка архитектурной документации",
                self.check_architecture_documentation,
            ),
            ("Проверка CI/CD workflow", self.check_ci_cd_workflow),
            (
                "Проверка операционного статуса CAA",
                self.check_agents_operational_status,
            ),
            ("Проверка целостности changelog", self.check_changelog_integrity),
        ]

        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}")
            print("-" * 60)
            try:
                check_func()
            except Exception as e:
                self.log("error", f"Ошибка выполнения проверки: {e}", check_name)

        # Генерация отчета
        report_file = self.generate_report()

        # Итоговый вывод
        print("\n" + "=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 80)

        success = self.results.count("success")
        warning = self.results.count("warning")
        error = self.results.count("error")

        print(f"✅ Успешно: {success}")
        print(f"⚠️  Предупреждения: {warning}")
        print(f"❌ Ошибки: {error}")

        if error > 0:
            print("\n❌ HEALTH CHECK НЕ ПРОЙДЕН: обнаружены критические ошибки")
            return False
        if warning > 0:
            print("\n⚠️  HEALTH CHECK ПРОЙДЕН С ПРЕДУПРЕЖДЕНИЯМИ")
            return True
        print("\n✅ HEALTH CHECK ПРОЙДЕН УСПЕШНО")
        return True


def main():
    """Основная функция"""
    checker = HealthChecker()

    try:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Health check прерван пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
