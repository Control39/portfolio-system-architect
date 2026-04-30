#!/usr/bin/env python3
"""
Тестирование и валидация Cognitive Automation Agent.
Проверка всех компонентов агента на корректность работы.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

# Добавляем путь к модулям агента
sys.path.insert(0, str(Path(__file__).parent.parent))


class CognitiveAgentValidator:
    """Валидатор Cognitive Automation Agent"""

    def __init__(self, agent_root: str = ".agents"):
        self.agent_root = Path(agent_root)
        self.validation_results = {
            "overall": "pending",
            "components": {},
            "issues": [],
            "recommendations": [],
        }

    def validate_structure(self) -> Dict[str, Any]:
        """Проверка структуры директорий агента"""
        print("🔍 Проверка структуры директорий...")

        required_dirs = [
            "skills",
            "config",
            "workflows",
            "tests",
            "logs",
            "scans",
            "reports",
            "backups",
            "cache",
            "models",
            "data",
            "knowledge",
            "alerts",
        ]

        results = {"passed": [], "missing": [], "optional": []}

        for dir_name in required_dirs:
            dir_path = self.agent_root / dir_name
            if dir_path.exists():
                results["passed"].append(dir_name)
            else:
                if dir_name in ["logs", "scans", "reports", "backups", "cache"]:
                    # Эти директории могут создаваться автоматически
                    results["optional"].append(dir_name)
                else:
                    results["missing"].append(dir_name)

        return results

    def validate_skills(self) -> Dict[str, Any]:
        """Проверка скиллов агента"""
        print("🔍 Проверка скиллов...")

        skills_dir = self.agent_root / "skills"
        required_skills = [
            "cognitive-automation-agent",
            "project-scanner",
            "task-planner",
            "learning-system",
        ]

        results = {"found": [], "missing": [], "valid": [], "invalid": []}

        for skill_name in required_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                results["found"].append(skill_name)

                # Проверка содержимого файла
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    if (
                        "---" in content
                        and "name:" in content
                        and "description:" in content
                    ):
                        results["valid"].append(skill_name)
                    else:
                        results["invalid"].append(skill_name)
                except Exception as e:
                    results["invalid"].append(f"{skill_name} (error: {str(e)})")
            else:
                results["missing"].append(skill_name)

        return results

    def validate_configurations(self) -> Dict[str, Any]:
        """Проверка конфигурационных файлов"""
        print("🔍 Проверка конфигураций...")

        config_dir = self.agent_root / "config"
        required_configs = [
            "agent-config.yaml",
            "integrations.yaml",
            "planner.yaml",
            "learning.yaml",
            "scanner.yaml",
        ]

        results = {"found": [], "missing": [], "valid_yaml": [], "invalid_yaml": []}

        for config_file in required_configs:
            config_path = config_dir / config_file
            if config_path.exists():
                results["found"].append(config_file)

                # Проверка YAML валидности
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                    results["valid_yaml"].append(config_file)
                except yaml.YAMLError as e:
                    results["invalid_yaml"].append(f"{config_file} (error: {str(e)})")
            else:
                # Проверяем, есть ли альтернативные имена
                alt_names = [
                    f.stem + ext
                    for ext in [".yaml", ".yml"]
                    for f in config_dir.glob(f"*{ext}")
                ]
                if config_file.replace(".yaml", "") in [
                    name.replace(".yaml", "").replace(".yml", "") for name in alt_names
                ]:
                    results["found"].append(f"{config_file} (alternative)")
                else:
                    results["missing"].append(config_file)

        return results

    def validate_workflows(self) -> Dict[str, Any]:
        """Проверка рабочих процессов"""
        print("🔍 Проверка рабочих процессов...")

        workflows_dir = self.agent_root / "workflows"
        required_workflows = ["project-setup.yaml"]

        results = {"found": [], "missing": [], "valid": [], "invalid": []}

        for workflow_file in required_workflows:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                results["found"].append(workflow_file)

                # Проверка YAML и структуры
                try:
                    with open(workflow_path, "r", encoding="utf-8") as f:
                        workflow_data = yaml.safe_load(f)

                    # Проверка обязательных полей
                    required_fields = ["name", "description", "phases"]
                    if all(field in workflow_data for field in required_fields):
                        results["valid"].append(workflow_file)
                    else:
                        missing = [f for f in required_fields if f not in workflow_data]
                        results["invalid"].append(
                            f"{workflow_file} (missing: {', '.join(missing)})"
                        )
                except (yaml.YAMLError, Exception) as e:
                    results["invalid"].append(f"{workflow_file} (error: {str(e)})")
            else:
                results["missing"].append(workflow_file)

        return results

    def validate_integrations(self) -> Dict[str, Any]:
        """Проверка интеграций"""
        print("🔍 Проверка интеграций...")

        integrations_file = (
            self.agent_root / "integrations" / "ecosystem-integration.md"
        )

        results = {
            "file_exists": integrations_file.exists(),
            "content_valid": False,
            "integration_points": [],
        }

        if integrations_file.exists():
            try:
                content = integrations_file.read_text(encoding="utf-8")

                # Проверка наличия ключевых разделов
                required_sections = [
                    "Интеграция с архитектурой проекта",
                    "Интеграция с DevOps инструментами",
                    "Интеграция с инструментами разработки",
                ]

                missing_sections = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)

                if not missing_sections:
                    results["content_valid"] = True

                # Извлечение точек интеграции
                import re

                integration_points = re.findall(
                    r"```yaml\nintegration_points:", content
                )
                results["integration_points"] = len(integration_points)

            except Exception as e:
                results["error"] = str(e)

        return results

    def validate_dependencies(self) -> Dict[str, Any]:
        """Проверка зависимостей"""
        print("🔍 Проверка зависимостей...")

        # Проверяем наличие requirements.txt для агента
        requirements_file = self.agent_root / "requirements.txt"

        results = {
            "requirements_exists": requirements_file.exists(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "required_modules": [],
            "missing_modules": [],
        }

        # Проверяем наличие ключевых модулей Python
        required_modules = ["yaml", "json", "pathlib", "pytest"]

        for module in required_modules:
            try:
                __import__(module)
                results["required_modules"].append(module)
            except ImportError:
                results["missing_modules"].append(module)

        return results

    def run_full_validation(self) -> Dict[str, Any]:
        """Запуск полной валидации"""
        print("=" * 60)
        print("🚀 Запуск полной валидации Cognitive Automation Agent")
        print("=" * 60)

        validation_results = {
            "timestamp": self._get_timestamp(),
            "agent_version": self._get_agent_version(),
            "tests": {},
        }

        # Запуск всех проверок
        tests = [
            ("structure", self.validate_structure),
            ("skills", self.validate_skills),
            ("configurations", self.validate_configurations),
            ("workflows", self.validate_workflows),
            ("integrations", self.validate_integrations),
            ("dependencies", self.validate_dependencies),
        ]

        all_passed = True
        for test_name, test_func in tests:
            try:
                result = test_func()
                validation_results["tests"][test_name] = result

                # Определяем, прошла ли проверка
                if self._is_test_passed(test_name, result):
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    all_passed = False

            except Exception as e:
                validation_results["tests"][test_name] = {"error": str(e)}
                print(f"⚠️  {test_name}: ERROR - {str(e)}")
                all_passed = False

        # Общий результат
        validation_results["overall"] = "PASSED" if all_passed else "FAILED"

        # Генерация отчета
        self._generate_report(validation_results)

        return validation_results

    def _is_test_passed(self, test_name: str, result: Dict[str, Any]) -> bool:
        """Определение, прошла ли проверка"""
        if test_name == "structure":
            # Проверка проходит, если нет обязательных директорий в missing
            # Опциональные директории (logs, scans, reports, backups, cache) не считаются ошибкой
            missing = result.get("missing", [])
            # Фильтруем опциональные директории
            optional_dirs = ["logs", "scans", "reports", "backups", "cache"]
            required_missing = [d for d in missing if d not in optional_dirs]
            return len(required_missing) == 0

        elif test_name == "skills":
            required = [
                "cognitive-automation-agent",
                "project-scanner",
                "task-planner",
                "learning-system",
            ]
            found = result.get("found", [])
            return all(skill in found for skill in required)

        elif test_name == "configurations":
            required = ["agent-config.yaml"]
            found = result.get("found", [])
            return any(config in found for config in required)

        elif test_name == "workflows":
            return len(result.get("valid", [])) > 0

        elif test_name == "integrations":
            return result.get("content_valid", False)

        elif test_name == "dependencies":
            return len(result.get("missing_modules", [])) == 0

        return False

    def _get_timestamp(self) -> str:
        """Получение временной метки"""
        from datetime import datetime

        return datetime.now().isoformat()

    def _get_agent_version(self) -> str:
        """Получение версии агента"""
        config_path = self.agent_root / "config" / "agent-config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                return config.get("version", "unknown")
            except:
                pass
        return "unknown"

    def _generate_report(self, validation_results: Dict[str, Any]):
        """Генерация отчета о валидации"""
        report_dir = self.agent_root / "reports"
        report_dir.mkdir(exist_ok=True, parents=True)

        report_file = (
            report_dir
            / f"validation_report_{self._get_timestamp().replace(':', '-')}.json"
        )

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, indent=2, ensure_ascii=False)

        # Генерация читаемого отчета
        self._generate_human_readable_report(validation_results, report_dir)

        print(f"\n📊 Отчет сохранен: {report_file}")

    def _generate_human_readable_report(
        self, validation_results: Dict[str, Any], report_dir: Path
    ):
        """Генерация читаемого отчета в markdown"""
        md_file = (
            report_dir
            / f"validation_summary_{self._get_timestamp().replace(':', '-')}.md"
        )

        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# Отчет валидации Cognitive Automation Agent\n\n")
            f.write(f"**Время проверки:** {validation_results['timestamp']}\n")
            f.write(f"**Версия агента:** {validation_results['agent_version']}\n")
            f.write(f"**Общий результат:** **{validation_results['overall']}**\n\n")

            f.write("## Результаты проверок\n\n")

            for test_name, test_result in validation_results["tests"].items():
                f.write(f"### {test_name.replace('_', ' ').title()}\n\n")

                if "error" in test_result:
                    f.write(f"❌ Ошибка: {test_result['error']}\n\n")
                    continue

                # Структурированный вывод в зависимости от типа проверки
                if test_name == "structure":
                    f.write(
                        f"- Найдено директорий: {len(test_result.get('passed', []))}\n"
                    )
                    f.write(f"- Отсутствует: {len(test_result.get('missing', []))}\n")
                    if test_result.get("missing"):
                        f.write(f"  - {', '.join(test_result['missing'])}\n")
                    f.write(
                        f"- Опциональные: {len(test_result.get('optional', []))}\n\n"
                    )

                elif test_name == "skills":
                    f.write(f"- Найдено скиллов: {len(test_result.get('found', []))}\n")
                    f.write(f"- Валидных: {len(test_result.get('valid', []))}\n")
                    f.write(f"- Отсутствует: {len(test_result.get('missing', []))}\n")
                    if test_result.get("missing"):
                        f.write(f"  - {', '.join(test_result['missing'])}\n")
                    f.write("\n")

                elif test_name == "configurations":
                    f.write(
                        f"- Найдено конфигураций: {len(test_result.get('found', []))}\n"
                    )
                    f.write(
                        f"- Валидных YAML: {len(test_result.get('valid_yaml', []))}\n"
                    )
                    f.write(f"- Отсутствует: {len(test_result.get('missing', []))}\n")
                    if test_result.get("missing"):
                        f.write(f"  - {', '.join(test_result['missing'])}\n")
                    f.write("\n")

                elif test_name == "workflows":
                    f.write(
                        f"- Найдено процессов: {len(test_result.get('found', []))}\n"
                    )
                    f.write(f"- Валидных: {len(test_result.get('valid', []))}\n")
                    f.write(f"- Отсутствует: {len(test_result.get('missing', []))}\n")
                    f.write("\n")

                elif test_name == "integrations":
                    f.write(
                        f"- Файл интеграций: {'✅ Существует' if test_result.get('file_exists') else '❌ Отсутствует'}\n"
                    )
                    f.write(
                        f"- Контент валиден: {'✅ Да' if test_result.get('content_valid') else '❌ Нет'}\n"
                    )
                    f.write(
                        f"- Точек интеграции: {test_result.get('integration_points', 0)}\n\n"
                    )

                elif test_name == "dependencies":
                    f.write(
                        f"- Python версия: {test_result.get('python_version', 'unknown')}\n"
                    )
                    f.write(
                        f"- Найдено модулей: {len(test_result.get('required_modules', []))}\n"
                    )
                    f.write(
                        f"- Отсутствует модулей: {len(test_result.get('missing_modules', []))}\n"
                    )
                    if test_result.get("missing_modules"):
                        f.write(f"  - {', '.join(test_result['missing_modules'])}\n")
                    f.write("\n")

            # Рекомендации
            f.write("## Рекомендации\n\n")

            issues = []
            for test_name, test_result in validation_results["tests"].items():
                if not self._is_test_passed(test_name, test_result):
                    issues.append(test_name)

            if not issues:
                f.write(
                    "✅ Все проверки пройдены успешно. Агент готов к использованию.\n"
                )
            else:
                f.write("⚠️  Обнаружены проблемы в следующих областях:\n")
                for issue in issues:
                    f.write(f"- {issue.replace('_', ' ').title()}\n")

                f.write("\n**Действия для исправления:**\n")

                if "structure" in issues:
                    f.write(
                        "1. Создайте недостающие директории: `mkdir -p .agents/{config,workflows,logs,scans,reports}`\n"
                    )

                if "skills" in issues:
                    f.write(
                        "2. Проверьте наличие обязательных скиллов в `.agents/skills/`\n"
                    )

                if "configurations" in issues:
                    f.write(
                        "3. Создайте файл конфигурации `.agents/config/agent-config.yaml`\n"
                    )

                if "dependencies" in issues:
                    f.write("4. Установите недостающие модули Python\n")

            f.write("\n## Следующие шаги\n\n")
            f.write(
                "1. Запустите тестовый рабочий процесс: `python -m agents.workflows.run --workflow=project-setup --test`\n"
            )
            f.write("2. Проверьте интеграции с существующей экосистемой\n")
            f.write("3. Настройте уровень автономности в конфигурации\n")
            f.write("4. Запустите первое обучение моделей\n")


# Тесты pytest для автоматического тестирования
@pytest.fixture
def validator():
    # Получаем абсолютный путь к директории .agents относительно корня проекта
    agent_root = os.path.join(os.path.dirname(__file__), "..")
    return CognitiveAgentValidator(agent_root)


def test_agent_structure(validator):
    """Тест структуры агента"""
    result = validator.validate_structure()
    assert (
        len(result.get("missing", [])) == 0
    ), f"Missing directories: {result.get('missing')}"


def test_required_skills(validator):
    """Тест обязательных скиллов"""
    result = validator.validate_skills()
    required_skills = [
        "cognitive-automation-agent",
        "project-scanner",
        "task-planner",
        "learning-system",
    ]
    for skill in required_skills:
        assert skill in result.get("found", []), f"Missing skill: {skill}"


def test_configuration_files(validator):
    """Тест конфигурационных файлов"""
    result = validator.validate_configurations()
    assert "agent-config.yaml" in result.get("found", []), "Missing agent-config.yaml"


def test_workflow_existence(validator):
    """Тест наличия рабочих процессов"""
    result = validator.validate_workflows()
    assert len(result.get("found", [])) > 0, "No workflows found"


def test_integration_documentation(validator):
    """Тест документации интеграций"""
    result = validator.validate_integrations()
    assert result.get("file_exists", False), "Integration documentation missing"


def test_python_dependencies(validator):
    """Тест зависимостей Python"""
    result = validator.validate_dependencies()
    assert (
        len(result.get("missing_modules", [])) == 0
    ), f"Missing modules: {result.get('missing_modules')}"


def test_full_validation(validator):
    """Полный тест валидации"""
    result = validator.run_full_validation()
    assert result["overall"] == "PASSED", f"Validation failed: {result}"


if __name__ == "__main__":
    # Запуск валидации при прямом вызове
    validator = CognitiveAgentValidator()

    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        # Запуск тестов через pytest
        pytest.main([__file__, "-v"])
    else:
        # Запуск интерактивной валидации
        results = validator.run_full_validation()

        # Вывод краткого результата
        print("\n" + "=" * 60)
        print(f"📋 ИТОГ ВАЛИДАЦИИ: {results['overall']}")
        print("=" * 60)

        if results["overall"] == "PASSED":
            print("🎉 Cognitive Automation Agent прошел все проверки!")
            print("Агент готов к использованию.")
        else:
            print("⚠️  Обнаружены проблемы. Смотрите отчет для деталей.")
            print("Рекомендации по исправлению в сгенерированном отчете.")

        sys.exit(0 if results["overall"] == "PASSED" else 1)
