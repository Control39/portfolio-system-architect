"""
Модуль для анализа и улучшения документации
"""

import ast
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DocFormat(Enum):
    """Форматы документации"""

    MARKDOWN = "markdown"
    RST = "rst"
    PYTHON_DOCSTRING = "docstring"
    JSDOC = "jsdoc"
    TSDOC = "tsdoc"


@dataclass
class DocumentationIssue:
    """Проблема в документации"""

    file_path: str
    line_number: int | None
    issue_type: str
    severity: str  # low, medium, high
    message: str
    suggested_fix: str | None = None


@dataclass
class DocumentationResult:
    """Результат анализа документации"""

    format: DocFormat
    success: bool
    issues: list[DocumentationIssue]
    summary: dict[str, Any]


class DocumentationAnalyzer:
    """Класс для анализа документации в проекте"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.supported_extensions = {
            ".md": DocFormat.MARKDOWN,
            ".rst": DocFormat.RST,
            ".py": DocFormat.PYTHON_DOCSTRING,
            ".js": DocFormat.JSDOC,
            ".ts": DocFormat.TSDOC,
            ".jsx": DocFormat.JSDOC,
            ".tsx": DocFormat.TSDOC,
        }
        self.documentation_files = self._find_documentation_files()

    def _find_documentation_files(self) -> list[Path]:
        """Найти все файлы документации в проекте"""
        doc_files = []

        for extension, _format_type in self.supported_extensions.items():
            for file_path in self.project_path.rglob(f"*{extension}"):
                if not self._is_excluded(file_path):
                    doc_files.append(file_path)

        # Также ищем специфичные для документации директории
        doc_dirs = ["docs", "documentation", "wiki", "guides", "manuals"]
        for doc_dir in doc_dirs:
            dir_path = self.project_path / doc_dir
            if dir_path.exists():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix in self.supported_extensions:
                        if file_path not in doc_files:
                            doc_files.append(file_path)

        return sorted(doc_files)

    def _is_excluded(self, path: Path) -> bool:
        """Проверить, исключён ли путь"""
        excluded_dirs = [".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", "build", "dist", ".eggs"]
        return any(part in excluded_dirs for part in path.parts)

    def _extract_python_functions_and_classes(self, file_path: Path) -> list[dict[str, Any]]:
        """Извлечь функции и классы из Python файла вместе с их docstrings"""
        functions_and_classes = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    item_info = {
                        "name": node.name,
                        "type": "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                        "docstring": ast.get_docstring(node),
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "params": [],
                    }

                    # Извлекаем параметры для функций
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for arg in node.args.args:
                            item_info["params"].append(arg.arg)
                        if node.args.vararg:
                            item_info["params"].append(f"*{node.args.vararg.arg}")
                        if node.args.kwarg:
                            item_info["params"].append(f"**{node.args.kwarg.arg}")

                    functions_and_classes.append(item_info)
        except Exception as e:
            logger.warning(f"Ошибка при анализе Python файла {file_path}: {e}")

        return functions_and_classes

    def analyze_python_documentation(self, file_path: Path) -> DocumentationResult:
        """Анализировать документацию в Python файле"""
        issues = []

        # Извлекаем функции и классы с их docstring'ами
        items = self._extract_python_functions_and_classes(file_path)

        for item in items:
            # Проверяем, есть ли docstring
            if not item["docstring"]:
                issues.append(
                    DocumentationIssue(
                        file_path=str(file_path),
                        line_number=item["line_start"],
                        issue_type="missing_docstring",
                        severity="high",
                        message=f"У {item['type']} '{item['name']}' отсутствует docstring",
                    )
                )
            else:
                # Проверяем качество docstring
                docstring = item["docstring"]

                # Проверяем, содержит ли docstring описание параметров
                if item["type"] == "function":
                    missing_params = []
                    for param in item["params"]:
                        if param != "self" and param not in docstring:
                            missing_params.append(param)

                    if missing_params:
                        issues.append(
                            DocumentationIssue(
                                file_path=str(file_path),
                                line_number=item["line_start"],
                                issue_type="missing_param_docs",
                                severity="medium",
                                message=f"В docstring для функции '{item['name']}' отсутствует документация для параметров: {', '.join(missing_params)}",
                            )
                        )

                # Проверяем длину docstring
                if len(docstring.strip()) < 10:
                    issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=item["line_start"],
                            issue_type="short_docstring",
                            severity="medium",
                            message=f"Docstring для {item['type']} '{item['name']}' слишком короткий",
                        )
                    )

        return DocumentationResult(
            format=DocFormat.PYTHON_DOCSTRING,
            success=True,
            issues=issues,
            summary={
                "total_items": len(items),
                "items_without_docstring": len([i for i in issues if i.issue_type == "missing_docstring"]),
                "items_with_missing_params": len([i for i in issues if i.issue_type == "missing_param_docs"]),
                "items_with_short_docstring": len([i for i in issues if i.issue_type == "short_docstring"]),
            },
        )

    def analyze_markdown_documentation(self, file_path: Path) -> DocumentationResult:
        """Анализировать Markdown документацию"""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # Проверяем заголовки
            headers = []
            for i, line in enumerate(lines, 1):
                if line.startswith("#"):
                    headers.append((i, line.strip()))

            # Проверяем, есть ли H1 заголовок
            h1_headers = [h for h in headers if h[1].startswith("# ") and not h[1].startswith("##")]
            if not h1_headers:
                issues.append(
                    DocumentationIssue(
                        file_path=str(file_path),
                        line_number=None,
                        issue_type="missing_h1_header",
                        severity="medium",
                        message=f"В файле {file_path.name} отсутствует заголовок первого уровня (H1)",
                    )
                )

            # Проверяем структуру заголовков (должны быть последовательными)
            header_levels = []
            for header in headers:
                level = len(header[1]) - len(header[1].lstrip("#"))
                header_levels.append(level)

            # Проверяем, есть ли пропуски в уровне заголовков (например, H1 -> H3 без H2)
            for i in range(1, len(header_levels)):
                if header_levels[i] > header_levels[i - 1] + 1:
                    issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=headers[i][0],
                            issue_type="header_structure_violation",
                            severity="medium",
                            message=f"Пропущен уровень заголовка: H{header_levels[i-1]} -> H{header_levels[i]}, ожидался H{header_levels[i-1]+1}",
                        )
                    )

            # Проверяем наличие таблицы содержания или навигации (если файл большой)
            if len(content) > 1000 and len(headers) > 3:
                # Проверяем, есть ли ссылки на другие разделы или файлы
                has_navigation = any(
                    word in content.lower()
                    for word in ["назад", "вверх", "следующий", "предыдущий", "см. также", "смотри также"]
                )
                if not has_navigation:
                    issues.append(
                        DocumentationIssue(
                            file_path=str(file_path),
                            line_number=None,
                            issue_type="missing_navigation",
                            severity="low",
                            message=f"Длинный документ ({len(content)} символов) не содержит навигации между разделами",
                        )
                    )

        except Exception as e:
            logger.warning(f"Ошибка при анализе Markdown файла {file_path}: {e}")
            return DocumentationResult(format=DocFormat.MARKDOWN, success=False, issues=[], summary={"error": str(e)})

        return DocumentationResult(
            format=DocFormat.MARKDOWN,
            success=True,
            issues=issues,
            summary={
                "total_headers": len([h for h in headers]),
                "h1_count": len([h for h in headers if h[1].startswith("# ") and not h[1].startswith("##")]),
                "total_issues": len(issues),
            },
        )

    def analyze_readme(self) -> DocumentationResult:
        """Анализировать файлы README в проекте"""
        readme_files = list(self.project_path.rglob("README.md"))
        readme_issues = []

        for readme_path in readme_files:
            try:
                with open(readme_path, encoding="utf-8") as f:
                    content = f.read()

                # Проверяем основные секции README
                sections_needed = ["установка", "использование", "пример", "лицензия", "авторы"]
                missing_sections = []

                lower_content = content.lower()
                for section in sections_needed:
                    if section not in lower_content:
                        missing_sections.append(section)

                if missing_sections:
                    readme_issues.append(
                        DocumentationIssue(
                            file_path=str(readme_path),
                            line_number=None,
                            issue_type="missing_readme_section",
                            severity="high",
                            message=f"В README отсутствуют важные разделы: {', '.join(missing_sections)}",
                        )
                    )

                # Проверяем, есть ли информация о проекте в начале
                first_lines = content[:500]  # Первые 500 символов
                project_keywords = ["описание", "назначение", "цель", "проект", "система", "приложение"]
                has_project_info = any(keyword in first_lines.lower() for keyword in project_keywords)

                if not has_project_info:
                    readme_issues.append(
                        DocumentationIssue(
                            file_path=str(readme_path),
                            line_number=None,
                            issue_type="missing_project_overview",
                            severity="medium",
                            message="README не содержит краткого описания проекта в начале",
                        )
                    )

                # Проверяем, есть ли информация о лицензии
                license_keywords = ["license", "лицензия", "rights", "авторские права"]
                has_license_info = any(keyword in lower_content for keyword in license_keywords)

                if not has_license_info:
                    readme_issues.append(
                        DocumentationIssue(
                            file_path=str(readme_path),
                            line_number=None,
                            issue_type="missing_license_info",
                            severity="high",
                            message="README не содержит информации о лицензии",
                        )
                    )

            except Exception as e:
                logger.warning(f"Ошибка при анализе README файла {readme_path}: {e}")

        return DocumentationResult(
            format=DocFormat.MARKDOWN,
            success=True,
            issues=readme_issues,
            summary={"readme_files_found": len(readme_files), "issues_found": len(readme_issues)},
        )

    def analyze_documentation_consistency(self) -> dict[str, Any]:
        """Анализировать согласованность документации по всему проекту"""
        consistency_issues = []

        # Проверяем соответствие между кодом и документацией
        python_files = [f for f in self.documentation_files if f.suffix == ".py"]
        markdown_files = [f for f in self.documentation_files if f.suffix in [".md", ".rst"]]

        # Создаем индекс функций/классов из кода
        code_entities = {}
        for py_file in python_files:
            entities = self._extract_python_functions_and_classes(py_file)
            for entity in entities:
                entity_key = f"{py_file.name}#{entity['name']}"
                code_entities[entity_key] = {"file": py_file, "type": entity["type"], "defined": True}

        # Проверяем, упоминаются ли сущности из кода в документации
        documented_entities = set()
        for md_file in markdown_files:
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read().lower()

                # Ищем упоминания сущностей кода в документации
                for entity_key, info in code_entities.items():
                    entity_name = entity_key.split("#")[1]  # Имя сущности
                    if entity_name.lower() in content:
                        documented_entities.add(entity_key)
            except Exception as e:
                logger.warning(f"Ошибка при анализе документации {md_file}: {e}")

        # Находим незадокументированные сущности
        undocumented_entities = set(code_entities.keys()) - documented_entities

        for entity_key in undocumented_entities:
            info = code_entities[entity_key]
            consistency_issues.append(
                DocumentationIssue(
                    file_path=str(info["file"]),
                    line_number=None,
                    issue_type="undocumented_code_entity",
                    severity="medium",
                    message=f"Сущность '{entity_key.split('#')[1]}' в файле {info['file'].name} не задокументирована в справочной документации",
                )
            )

        return {
            "total_code_entities": len(code_entities),
            "documented_entities": len(documented_entities),
            "undocumented_entities_count": len(undocumented_entities),
            "consistency_issues": consistency_issues,
            "documentation_coverage": len(documented_entities) / len(code_entities) if code_entities else 0,
        }

    def run_documentation_analysis(self) -> dict[str, Any]:
        """Запустить полный анализ документации"""
        logger.info(f"🔍 Начинаем анализ документации в проекте: {self.project_path}")

        results = {
            "project_path": str(self.project_path),
            "total_documentation_files": len(self.documentation_files),
            "files_analyzed": {},
            "readme_analysis": {},
            "consistency_analysis": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_severity_issues": 0,
                "medium_severity_issues": 0,
                "low_severity_issues": 0,
            },
        }

        # Анализируем каждый файл документации
        for file_path in self.documentation_files:
            extension = file_path.suffix.lower()

            if extension == ".py":
                result = self.analyze_python_documentation(file_path)
            elif extension in [".md", ".rst"]:
                result = self.analyze_markdown_documentation(file_path)
            else:
                continue  # Пропускаем неподдерживаемые форматы в этом анализе

            results["files_analyzed"][str(file_path)] = {
                "format": result.format.value,
                "success": result.success,
                "issues": [
                    {
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "issue_type": issue.issue_type,
                        "severity": issue.severity,
                        "message": issue.message,
                    }
                    for issue in result.issues
                ],
                "summary": result.summary,
            }

            # Обновляем итоговую статистику
            for issue in result.issues:
                results["summary"]["total_issues"] += 1
                if issue.severity == "high":
                    results["summary"]["high_severity_issues"] += 1
                elif issue.severity == "medium":
                    results["summary"]["medium_severity_issues"] += 1
                elif issue.severity == "low":
                    results["summary"]["low_severity_issues"] += 1

        # Анализируем README файлы
        readme_result = self.analyze_readme()
        results["readme_analysis"] = {
            "success": readme_result.success,
            "issues": [
                {
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "message": issue.message,
                }
                for issue in readme_result.issues
            ],
            "summary": readme_result.summary,
        }

        # Добавляем к итоговой статистике проблемы из README
        for issue in readme_result.issues:
            results["summary"]["total_issues"] += 1
            if issue.severity == "high":
                results["summary"]["high_severity_issues"] += 1
            elif issue.severity == "medium":
                results["summary"]["medium_severity_issues"] += 1
            elif issue.severity == "low":
                results["summary"]["low_severity_issues"] += 1

        # Анализируем согласованность документации
        consistency_result = self.analyze_documentation_consistency()
        results["consistency_analysis"] = consistency_result

        # Обновляем итоговую статистику для проблем согласованности
        for issue in consistency_result["consistency_issues"]:
            results["summary"]["total_issues"] += 1
            results["summary"]["medium_severity_issues"] += 1  # Проблемы согласованности обычно средней важности

        logger.info(f"✅ Анализ документации завершен. Найдено проблем: {results['summary']['total_issues']}")

        return results

    def generate_documentation_improvements(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Сгенерировать рекомендации по улучшению документации"""
        improvements = {
            "timestamp": str(self.project_path),
            "project_path": str(self.project_path),
            "recommendations": [],
            "priority_actions": [],
            "implementation_guide": {},
        }

        # Рекомендации на основе анализа
        summary = analysis_results.get("summary", {})
        readme_analysis = analysis_results.get("readme_analysis", {})
        consistency_analysis = analysis_results.get("consistency_analysis", {})

        # Рекомендации для критических проблем
        if summary.get("high_severity_issues", 0) > 0:
            improvements["recommendations"].append(
                {
                    "category": "critical_documentation",
                    "priority": "high",
                    "description": f"Устранить {summary['high_severity_issues']} критических проблем в документации",
                    "details": "Фокус на файлах README, отсутствующих лицензиях и основных описаниях проекта",
                }
            )

        # Рекомендации для README
        readme_issues = len(readme_analysis.get("issues", []))
        if readme_issues > 0:
            improvements["recommendations"].append(
                {
                    "category": "readme_improvements",
                    "priority": "high",
                    "description": f"Улучшить {readme_analysis.get('summary', {}).get('readme_files_found', 0)} файла(ов) README",
                    "details": f"Исправить {readme_issues} проблем(ы) в файлах README",
                }
            )

        # Рекомендации для согласованности
        undocumented_count = consistency_analysis.get("undocumented_entities_count", 0)
        if undocumented_count > 0:
            improvements["recommendations"].append(
                {
                    "category": "code_documentation",
                    "priority": "medium",
                    "description": f"Документировать {undocumented_count} сущностей кода",
                    "details": f"Покрытие документацией: {consistency_analysis.get('documentation_coverage', 0):.1%}",
                }
            )

        # Приоритетные действия
        if summary.get("high_severity_issues", 0) > 0:
            improvements["priority_actions"].append("Исправить критические проблемы в README")

        if undocumented_count > 10:  # Если много незадокументированных сущностей
            improvements["priority_actions"].append("Создать автоматический генератор документации")

        if consistency_analysis.get("documentation_coverage", 0) < 0.5:  # Если покрытие меньше 50%
            improvements["priority_actions"].append("Разработать стратегию документирования кода")

        # Руководство по внедрению
        improvements["implementation_guide"] = {
            "step_by_step": [
                "1. Исправить критические проблемы в README файлах",
                "2. Добавить недостающие docstring'и к функциям и классам",
                "3. Создать шаблоны документации для разных типов файлов",
                "4. Настроить автоматическую проверку качества документации",
                "5. Обновить CONTRIBUTING.md с требованиями к документации",
            ],
            "tools_suggestions": [
                "Sphinx для генерации документации Python проектов",
                "MkDocs для документации в формате Markdown",
                "pydocstyle для проверки docstring'ов",
                "interrogate для проверки покрытия документацией",
            ],
            "metrics_to_track": [
                "Процент сущностей кода с документацией",
                "Количество проблем в документации",
                "Покрытие документацией по сравнению с предыдущими версиями",
            ],
        }

        return improvements
