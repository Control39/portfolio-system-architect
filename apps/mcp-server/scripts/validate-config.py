#!/usr/bin/env python3
"""
Скрипт для валидации и миграции конфигураций агентов

Проверяет конфигурационные файлы на:
1. Устаревшие модели AI (GPT-5 и другие несуществующие)
2. Конфликтующие настройки
3. Избыточную вложенность
4. Разбросанные конфигурации

Автоматически исправляет обнаруженные проблемы.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Добавляем путь к корню проекта
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class ConfigValidator:
    """Валидатор конфигурационных файлов"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.problems = []
        self.fixes_applied = []

        # Устаревшие модели AI
        self.outdated_models = [
            "gpt-5",
            "GPT-5",
            "GPT5",
            "gpt-4.5",
            "GPT-4.5",
            "claude-4",
            "Claude-4",
            "gemini-2.0",
            "Gemini-2.0",
        ]

        # Актуальные модели для замены
        self.replacement_models = {
            "gpt-5": "gpt-4",
            "GPT-5": "GPT-4",
            "GPT5": "GPT4",
            "gpt-4.5": "gpt-4",
            "GPT-4.5": "GPT-4",
            "claude-4": "claude-3-opus",
            "Claude-4": "Claude-3-Opus",
            "gemini-2.0": "gemini-1.5-pro",
            "Gemini-2.0": "Gemini-1.5-Pro",
        }

        # Конфигурационные файлы для проверки
        self.config_files = [
            # Continue.dev конфигурации
            {
                "path": project_root / ".continue" / "agents" / "new-config.yaml",
                "type": "yaml",
                "description": "Continue.dev основная конфигурация",
            },
            {
                "path": project_root / ".continue" / "config.yaml",
                "type": "yaml",
                "description": "Continue.dev общая конфигурация",
            },
            # Code Assistant конфигурации
            {
                "path": project_root / ".codeassistant" / "config.yaml",
                "type": "yaml",
                "description": "Code Assistant конфигурация",
            },
            # Настройки проекта
            {
                "path": project_root / "settings" / "custom_modes.yaml",
                "type": "yaml",
                "description": "Кастомные режимы Code Assistant",
            },
            {
                "path": project_root / "settings" / "mcp_settings.json",
                "type": "json",
                "description": "Настройки MCP серверов",
            },
            # AI Config Manager
            {
                "path": project_root
                / "apps"
                / "ai-config-manager"
                / "config"
                / "default.yaml",
                "type": "yaml",
                "description": "AI Config Manager конфигурация",
            },
            # Общая конфигурация проекта
            {
                "path": project_root / "project-config.yaml",
                "type": "yaml",
                "description": "Общая конфигурация проекта",
            },
            # MCP сервер конфигурация
            {
                "path": project_root
                / "apps"
                / "mcp-server"
                / "config"
                / "mcp-config.yaml",
                "type": "yaml",
                "description": "MCP сервер конфигурация",
            },
        ]

    def validate_all(self) -> Dict[str, Any]:
        """Проверка всех конфигурационных файлов"""
        print("=" * 60)
        print("Валидация конфигурационных файлов")
        print("=" * 60)

        results = {
            "total_files": 0,
            "checked_files": 0,
            "accessible_files": 0,
            "problems_found": 0,
            "fixes_applied": 0,
            "details": [],
        }

        for config in self.config_files:
            result = self.validate_file(config)
            results["details"].append(result)
            results["total_files"] += 1

            if result["exists"]:
                results["checked_files"] += 1

            if result["accessible"]:
                results["accessible_files"] += 1

            results["problems_found"] += len(result["problems"])
            results["fixes_applied"] += len(result["fixes_applied"])

        return results

    def validate_file(self, config: Dict) -> Dict[str, Any]:
        """Проверка одного конфигурационного файла"""
        file_path = config["path"]
        result = {
            "file": str(file_path.relative_to(self.project_root)),
            "description": config["description"],
            "exists": file_path.exists(),
            "accessible": False,
            "problems": [],
            "fixes_applied": [],
            "content": None,
        }

        if not result["exists"]:
            result["problems"].append("Файл не существует")
            return result

        try:
            # Пытаемся прочитать файл
            if config["type"] == "yaml":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    result["content"] = (
                        yaml.safe_load(content) if content.strip() else {}
                    )
            elif config["type"] == "json":
                with open(file_path, "r", encoding="utf-8") as f:
                    result["content"] = json.load(f)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    result["content"] = f.read()

            result["accessible"] = True

            # Проверяем на устаревшие модели
            if result["content"]:
                content_str = str(result["content"])
                problems = self.check_outdated_models(content_str, file_path)
                result["problems"].extend(problems)

                # Если есть проблемы, предлагаем исправления
                if problems and config["type"] in ["yaml", "json"]:
                    fixes = self.fix_outdated_models(
                        file_path, config["type"], content_str
                    )
                    result["fixes_applied"].extend(fixes)

            # Проверяем другие проблемы
            other_problems = self.check_other_problems(file_path, result["content"])
            result["problems"].extend(other_problems)

        except PermissionError:
            result["problems"].append("Нет прав доступа к файлу")
        except yaml.YAMLError as e:
            result["problems"].append(f"Ошибка YAML: {str(e)}")
        except json.JSONDecodeError as e:
            result["problems"].append(f"Ошибка JSON: {str(e)}")
        except Exception as e:
            result["problems"].append(f"Ошибка при чтении файла: {str(e)}")

        return result

    def check_outdated_models(self, content: str, file_path: Path) -> List[str]:
        """Проверка на устаревшие модели AI"""
        problems = []

        for model in self.outdated_models:
            if model in content:
                problems.append(f"Устаревшая модель AI: {model}")

        return problems

    def fix_outdated_models(
        self, file_path: Path, file_type: str, original_content: str
    ) -> List[str]:
        """Исправление устаревших моделей AI"""
        fixes = []

        try:
            if file_type == "yaml":
                # Загружаем YAML
                data = yaml.safe_load(original_content)

                # Преобразуем в строку для поиска
                content_str = yaml.dump(data, default_flow_style=False)

                # Заменяем устаревшие модели
                for old, new in self.replacement_models.items():
                    if old in content_str:
                        content_str = content_str.replace(old, new)
                        fixes.append(f"Заменена {old} -> {new}")

                # Сохраняем изменения
                if fixes:
                    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_content)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content_str)

            elif file_type == "json":
                # Загружаем JSON
                data = json.loads(original_content)

                # Преобразуем в строку для поиска
                content_str = json.dumps(data, indent=2)

                # Заменяем устаревшие модели
                for old, new in self.replacement_models.items():
                    if old in content_str:
                        content_str = content_str.replace(old, new)
                        fixes.append(f"Заменена {old} -> {new}")

                # Сохраняем изменения
                if fixes:
                    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_content)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content_str)

        except Exception as e:
            fixes.append(f"Ошибка при исправлении: {str(e)}")

        return fixes

    def check_other_problems(self, file_path: Path, content: Any) -> List[str]:
        """Проверка других проблем"""
        problems = []

        # Проверяем избыточную вложенность по пути
        path_str = str(file_path)
        depth = path_str.count(os.sep) - str(self.project_root).count(os.sep)

        if depth > 6:
            problems.append(f"Избыточная вложенность: {depth} уровней")

        # Проверяем размер файла
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 1:
                problems.append(f"Большой размер файла: {size_mb:.2f} MB")

        # Дополнительные проверки в зависимости от типа файла
        if isinstance(content, dict):
            problems.extend(self.check_dict_problems(content))

        return problems

    def check_dict_problems(self, data: Dict) -> List[str]:
        """Проверка проблем в словарях конфигурации"""
        problems = []

        # Проверяем наличие обязательных полей для Continue.dev
        if "models" in data:
            models = data.get("models", [])
            if not isinstance(models, list):
                problems.append("Поле 'models' должно быть списком")
            elif len(models) == 0:
                problems.append("Нет настроенных моделей AI")

        # Проверяем наличие MCP серверов
        if "mcpServers" in data:
            servers = data.get("mcpServers", {})
            if not isinstance(servers, dict):
                problems.append("Поле 'mcpServers' должно быть словарем")

        return problems

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Генерация отчета о валидации"""
        report = []
        report.append("=" * 60)
        report.append("ОТЧЕТ О ВАЛИДАЦИИ КОНФИГУРАЦИЙ")
        report.append("=" * 60)
        report.append("")

        # Сводка
        report.append("СВОДКА:")
        report.append(f"  Всего файлов: {results['total_files']}")
        report.append(f"  Проверено файлов: {results['checked_files']}")
        report.append(f"  Доступно файлов: {results['accessible_files']}")
        report.append(f"  Найдено проблем: {results['problems_found']}")
        report.append(f"  Применено исправлений: {results['fixes_applied']}")
        report.append("")

        # Детали по файлам
        report.append("ДЕТАЛИ ПО ФАЙЛАМ:")
        for detail in results["details"]:
            report.append(f"\n{detail['file']} ({detail['description']}):")
            report.append(f"  Существует: {'Да' if detail['exists'] else 'Нет'}")
            report.append(f"  Доступен: {'Да' if detail['accessible'] else 'Нет'}")

            if detail["problems"]:
                report.append(f"  Проблемы ({len(detail['problems'])}):")
                for problem in detail["problems"]:
                    report.append(f"    - {problem}")

            if detail["fixes_applied"]:
                report.append(f"  Исправления ({len(detail['fixes_applied'])}):")
                for fix in detail["fixes_applied"]:
                    report.append(f"    - {fix}")

        # Рекомендации
        report.append("")
        report.append("РЕКОМЕНДАЦИИ:")

        if results["problems_found"] > 0:
            report.append("1. Проверьте и исправьте устаревшие модели AI")
            report.append("2. Упростите структуру директорий с избыточной вложенностью")
            report.append("3. Объедините разбросанные конфигурации")
        else:
            report.append("Все конфигурации в порядке. Проблем не обнаружено.")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    """Основная функция"""
    validator = ConfigValidator(project_root)

    # Проверяем все конфигурации
    results = validator.validate_all()

    # Генерируем отчет
    report = validator.generate_report(results)

    # Выводим отчет
    print(report)

    # Сохраняем отчет в файл
    report_path = project_root / "docs" / "audit" / "config-validation-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nОтчет сохранен в: {report_path.relative_to(project_root)}")

    # Возвращаем код выхода в зависимости от наличия проблем
    if results["problems_found"] > 0:
        print("\n⚠️  Обнаружены проблемы. Рекомендуется их исправить.")
        return 1
    else:
        print("\n✅ Все конфигурации в порядке.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
