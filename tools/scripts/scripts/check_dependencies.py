#!/usr/bin/env python3
"""Скрипт для проверки и унификации зависимостей в проекте.
Проверяет соответствие зависимостей в компонентах и корневом requirements.txt.
"""

import re
import sys
from pathlib import Path

import yaml


class DependencyChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.components_dir = self.project_root / "components"

    def find_requirements_files(self) -> list[Path]:
        """Находит все файлы requirements.txt в проекте."""
        requirements_files = []

        # Корневой requirements.txt
        root_req = self.project_root / "requirements.txt"
        if root_req.exists():
            requirements_files.append(root_req)

        # requirements.txt в компонентах
        for req_file in self.components_dir.rglob("requirements.txt"):
            requirements_files.append(req_file)

        return requirements_files

    def parse_requirements(self, file_path: Path) -> dict[str, str]:
        """Парсит файл requirements.txt и возвращает словарь зависимостей."""
        dependencies = {}

        if not file_path.exists():
            return dependencies

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Регулярное выражение для извлечения зависимостей
        # Поддерживает форматы: package, package==version, package>=version, package<=version
        pattern = r"^([a-zA-Z0-9\-_\[\]]+)([=<>!~]=?[^#\s]*)?"

        for line in content.split("\n"):
            line = line.strip()
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue

            match = re.match(pattern, line)
            if match:
                package = match.group(1).strip()
                version = match.group(2).strip() if match.group(2) else ""
                dependencies[package] = version

        return dependencies

    def parse_project_config(self) -> dict[str, dict]:
        """Парсит project-config.yaml и извлекает информацию о компонентах."""
        config_path = self.project_root / "project-config.yaml"
        components = {}

        if not config_path.exists():
            return components

        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if "components" in config:
            for component in config["components"]:
                comp_name = component.get("name", "")
                if comp_name:
                    components[comp_name] = {
                        "path": component.get("path", ""),
                        "language": component.get("language", ""),
                        "dependencies": component.get("dependencies", []),
                        "testing": component.get("testing", {}),
                    }

        return components

    def check_dependencies_consistency(self) -> tuple[bool, dict]:
        """Проверяет согласованность зависимостей между компонентами и корневым файлом."""
        requirements_files = self.find_requirements_files()
        all_dependencies = {}

        # Собираем зависимости из всех файлов
        for req_file in requirements_files:
            rel_path = req_file.relative_to(self.project_root)
            deps = self.parse_requirements(req_file)
            all_dependencies[str(rel_path)] = deps

        # Анализируем корневой requirements.txt
        root_deps = all_dependencies.get("requirements.txt", {})

        # Находим зависимости, которые есть в компонентах, но нет в корневом файле
        missing_in_root = {}
        conflicts = {}

        for file_path, deps in all_dependencies.items():
            if file_path == "requirements.txt":
                continue

            for package, version in deps.items():
                if package not in root_deps:
                    if file_path not in missing_in_root:
                        missing_in_root[file_path] = []
                    missing_in_root[file_path].append(f"{package}{version}")

                # Проверяем конфликты версий
                for other_file, other_deps in all_dependencies.items():
                    if other_file == file_path:
                        continue

                    if package in other_deps and other_deps[package] != version:
                        conflict_key = f"{package}:{file_path} vs {other_file}"
                        conflicts[conflict_key] = {
                            file_path: version,
                            other_file: other_deps[package],
                        }

        # Проверяем project-config.yaml
        project_config = self.parse_project_config()
        config_deps_missing = {}

        for comp_name, comp_info in project_config.items():
            comp_deps = comp_info.get("dependencies", [])
            for dep in comp_deps:
                # Извлекаем имя пакета из строки зависимости
                match = re.match(r"^([a-zA-Z0-9\-_]+)", dep)
                if match:
                    package = match.group(1)
                    if package not in root_deps:
                        if comp_name not in config_deps_missing:
                            config_deps_missing[comp_name] = []
                        config_deps_missing[comp_name].append(dep)

        return {
            "all_dependencies": all_dependencies,
            "missing_in_root": missing_in_root,
            "conflicts": conflicts,
            "config_deps_missing": config_deps_missing,
            "root_deps_count": len(root_deps),
            "total_files": len(requirements_files),
        }

    def check_testing_frameworks(self) -> dict:
        """Проверяет используемые фреймворки тестирования в компонентах."""
        project_config = self.parse_project_config()
        testing_frameworks = {}

        for comp_name, comp_info in project_config.items():
            testing = comp_info.get("testing", {})
            framework = testing.get("framework", "не указан")
            language = comp_info.get("language", "не указан")

            if comp_name not in testing_frameworks:
                testing_frameworks[comp_name] = {}

            testing_frameworks[comp_name] = {
                "framework": framework,
                "language": language,
                "recommended": self.get_recommended_framework(language),
            }

        return testing_frameworks

    def get_recommended_framework(self, language: str) -> str:
        """Возвращает рекомендуемый фреймворк тестирования для языка."""
        recommendations = {
            "python": "pytest",
            "powershell": "Pester",
            "markdown": "markdownlint (для линтинга)",
        }
        return recommendations.get(language.lower(), "не определено")

    def generate_report(self) -> str:
        """Генерирует отчет о проверке зависимостей."""
        dep_check = self.check_dependencies_consistency()
        test_check = self.check_testing_frameworks()

        report = []
        report.append("=" * 80)
        report.append("ОТЧЕТ О ПРОВЕРКЕ ЗАВИСИМОСТЕЙ И ТЕСТИРОВАНИЯ")
        report.append("=" * 80)
        report.append("")

        # Раздел 1: Общая информация
        report.append("1. ОБЩАЯ ИНФОРМАЦИЯ")
        report.append("-" * 40)
        report.append(f"Найдено файлов requirements.txt: {dep_check['total_files']}")
        report.append(
            f"Зависимостей в корневом requirements.txt: {dep_check['root_deps_count']}"
        )
        report.append("")

        # Раздел 2: Пропущенные зависимости
        if dep_check["missing_in_root"]:
            report.append("2. ЗАВИСМОСТТСУТСТВУЮЩИЕ В КОРНЕВОМ ФАЙЛЕ")
            report.append("-" * 40)
            for file_path, deps in dep_check["missing_in_root"].items():
                report.append(f"  {file_path}:")
                for dep in deps:
                    report.append(f"    - {dep}")
            report.append("")
        else:
            report.append("2. ВСЕ ЗАВИСИМОСТИ ПРИСУТСТВУЮТ В КОРНЕВОМ ФАЙЛЕ ✓")
            report.append("")

        # Раздел 3: Конфликты версий
        if dep_check["conflicts"]:
            report.append("3. КОНФЛИКТЫ ВЕРСИЙ ЗАВИСИМОСТЕЙ")
            report.append("-" * 40)
            for conflict, versions in dep_check["conflicts"].items():
                report.append(f"  {conflict.split(':')[0]}:")
                for file_path, version in versions.items():
                    report.append(f"    - {file_path}: {version}")
            report.append("")
        else:
            report.append("3. КОНФЛИКТОВ ВЕРСИЙ НЕ ОБНАРУЖЕНО ✓")
            report.append("")

        # Раздел 4: Зависимости из project-config.yaml
        if dep_check["config_deps_missing"]:
            report.append(
                "4. ЗАВИСИМОСТИ ИЗ PROJECT-CONFIG.YAML, ОТСУТСТВУЮЩИЕ В REQUIREMENTS.TXT"
            )
            report.append("-" * 40)
            for comp_name, deps in dep_check["config_deps_missing"].items():
                report.append(f"  {comp_name}:")
                for dep in deps:
                    report.append(f"    - {dep}")
            report.append("")

        # Раздел 5: Фреймворки тестирования
        report.append("5. ФРЕЙМВОРКИ ТЕСТИРОВАНИЯ")
        report.append("-" * 40)
        for comp_name, info in test_check.items():
            framework = info["framework"]
            recommended = info["recommended"]
            status = "✓" if framework == recommended else "⚠"
            report.append(f"  {comp_name}:")
            report.append(f"    Язык: {info['language']}")
            report.append(f"    Используется: {framework}")
            report.append(f"    Рекомендуется: {recommended}")
            report.append(f"    Статус: {status}")
        report.append("")

        # Раздел 6: Рекомендации
        report.append("6. РЕКОМЕНДАЦИИ")
        report.append("-" * 40)

        if dep_check["missing_in_root"]:
            report.append(
                "  - Добавьте отсутствующие зависимости в корневой requirements.txt"
            )

        if dep_check["conflicts"]:
            report.append("  - Унифицируйте версии зависимостей между компонентами")

        if dep_check["config_deps_missing"]:
            report.append(
                "  - Обновите project-config.yaml или добавьте зависимости в requirements.txt"
            )

        # Проверяем рекомендации по тестированию
        needs_testing_unification = False
        for comp_name, info in test_check.items():
            if (
                info["framework"] != info["recommended"]
                and info["recommended"] != "не определено"
            ):
                needs_testing_unification = True
                break

        if needs_testing_unification:
            report.append(
                "  - Унифицируйте фреймворки тестирования согласно рекомендациям"
            )

        report.append(
            "  - Запускайте этот скрипт регулярно для поддержания согласованности"
        )
        report.append("")

        report.append("=" * 80)
        report.append("Проверка завершена.")
        report.append("=" * 80)

        return "\n".join(report)

    def run_checks(self):
        """Запускает все проверки и выводит отчет."""
        print(self.generate_report())

        # Возвращаем код выхода в зависимости от найденных проблем
        dep_check = self.check_dependencies_consistency()
        has_problems = (
            bool(dep_check["missing_in_root"])
            or bool(dep_check["conflicts"])
            or bool(dep_check["config_deps_missing"])
        )

        return 1 if has_problems else 0


def main():
    """Основная функция скрипта."""
    checker = DependencyChecker()

    print("Запуск проверки зависимостей и тестирования...")
    print()

    exit_code = checker.run_checks()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
