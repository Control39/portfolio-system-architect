"""
Модуль код-качества для когнитивного агента
Содержит анализ и безопасное исправление кода
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer


class CodeFixer:
    """Безопасный исправитель кода"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.code_analyzer = autonomous_agent.code_analyzer
        self.guardrails = autonomous_agent.guardrails
        self.project_path = autonomous_agent.project_path

    def fix_all(self, issues: list[dict], approved: bool = False) -> dict[str, Any]:
        """
        Исправление всех проблем
        :param issues: Список проблем для исправления
        :param approved: Подтверждено ли исправление
        :return: Результат исправления
        """
        results = {
            "total_issues": len(issues),
            "fixed": [],
            "failed": [],
            "skipped": [],
            "human_approval_required": False,
        }

        for issue in issues:
            try:
                # Проверка через guardrails
                if not self._check_guardrails(issue):
                    results["skipped"].append(issue)
                    continue

                # Попытка исправления
                if self._fix_issue(issue):
                    results["fixed"].append(issue)
                else:
                    results["failed"].append(issue)

            except Exception as e:
                results["failed"].append({"issue": issue, "error": str(e)})

        return results

    def _fix_issue(self, issue: dict) -> bool:
        """Попытка исправления одной проблемы"""
        # Логика исправления в зависимости от типа проблемы
        issue_type = issue.get("type", "")

        if issue_type == "syntax_error":
            return self._fix_syntax_error(issue)
        elif issue_type == "type_error":
            return self._fix_type_error(issue)
        elif issue_type == "security_vulnerability":
            return self._fix_security_vulnerability(issue)
        elif issue_type == "code_quality":
            return self._fix_code_quality(issue)
        else:
            return False

    def _fix_syntax_error(self, issue: dict) -> bool:
        """Исправление синтаксической ошибки"""
        # Используем AI для генерации исправления
        file_path = issue.get("file_path", "")
        line_number = issue.get("line_number", 0)
        error_message = issue.get("error", "")

        # Генерация исправления через AI
        fixed_code = self.autonomous_agent.ai_provider.generate_fix(
            file_path=file_path, line_number=line_number, error_message=error_message
        )

        if fixed_code:
            # Применение исправления
            self._apply_fix(file_path, line_number, fixed_code)
            return True
        return False

    def _fix_type_error(self, issue: dict) -> bool:
        """Исправление ошибки типов"""
        # Анализ и исправление через AI
        file_path = issue.get("file_path", "")
        line_number = issue.get("line_number", 0)
        error_message = issue.get("error", "")

        fixed_code = self.autonomous_agent.ai_provider.generate_fix(
            file_path=file_path, line_number=line_number, error_message=error_message, fix_type="type_annotation"
        )

        if fixed_code:
            self._apply_fix(file_path, line_number, fixed_code)
            return True
        return False

    def _fix_security_vulnerability(self, issue: dict) -> bool:
        """Исправление уязвимости безопасности"""
        # Исправление через безопасные шаблоны
        file_path = issue.get("file_path", "")
        line_number = issue.get("line_number", 0)
        vulnerability = issue.get("vulnerability", "")

        fixed_code = self.autonomous_agent.security_guard.generate_fix(
            vulnerability=vulnerability, file_path=file_path, line_number=line_number
        )

        if fixed_code:
            self._apply_fix(file_path, line_number, fixed_code)
            return True
        return False

    def _fix_code_quality(self, issue: dict) -> bool:
        """Исправление проблем качества кода"""
        # Исправление через AI с учетом best practices
        file_path = issue.get("file_path", "")
        line_number = issue.get("line_number", 0)
        quality_issue = issue.get("issue", "")

        fixed_code = self.autonomous_agent.ai_provider.generate_fix(
            file_path=file_path, line_number=line_number, error_message=quality_issue, fix_type="code_quality"
        )

        if fixed_code:
            self._apply_fix(file_path, line_number, fixed_code)
            return True
        return False

    def _apply_fix(self, file_path: str, line_number: int, fixed_code: str) -> None:
        """Применение исправления к файлу"""
        # Читаем файл
        path = Path(file_path)
        if not path.exists():
            return

        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        # Применяем исправление
        if 0 < line_number <= len(lines):
            lines[line_number - 1] = fixed_code + "\n"

        # Записываем обратно
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _check_guardrails(self, issue: dict) -> bool:
        """Проверка через guardrails"""
        # Проверка уровня критичности
        severity = issue.get("severity", "low")

        if severity == "critical":
            # Требуется одобрение человека
            return self.guardrails.request_approval(action="code_fix", details=issue)

        return True


class CodeQualityGuard:
    """Охранник качества кода"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.code_analyzer = autonomous_agent.code_analyzer
        self.code_fixer = CodeFixer(autonomous_agent)
        self.guardrails = autonomous_agent.guardrails

    def analyze_full_repository(self) -> dict[str, Any]:
        """
        Анализ качества кода всего репозитория
        :return: Отчет о качестве кода
        """
        results = {}

        for service in self.autonomous_agent.service_registry.services:
            service_report = self.code_analyzer.analyze_service(service.path)
            results[service.name] = service_report

        # Генерация общего отчета
        return {
            "summary": self._generate_summary(results),
            "services": results,
            "recommendations": self._generate_recommendations(results),
        }

    def _generate_summary(self, results: dict) -> dict:
        """Генерация сводного отчета"""
        total_issues = 0
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0

        for _service_name, service_results in results.items():
            issues = service_results.get("issues", [])
            total_issues += len(issues)

            for issue in issues:
                severity = issue.get("severity", "low")
                if severity == "critical":
                    critical_issues += 1
                elif severity == "high":
                    high_issues += 1
                elif severity == "medium":
                    medium_issues += 1
                else:
                    low_issues += 1

        return {
            "total_services": len(results),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "overall_score": self._calculate_score(total_issues, critical_issues, high_issues),
        }

    def _calculate_score(self, total: int, critical: int, high: int) -> float:
        """Расчет оценки качества"""
        # Веса для разных уровней
        weight_critical = 10
        weight_high = 5
        weight_low = 1

        penalty = critical * weight_critical + high * weight_high + total * weight_low  # Упрощенная формула

        score = max(0, 100 - penalty)
        return round(score, 2)

    def _generate_recommendations(self, results: dict) -> list[dict]:
        """Генерация рекомендаций"""
        recommendations = []

        for service_name, service_results in results.items():
            issues = service_results.get("issues", [])

            # Группировка по типу проблемы
            by_type = {}
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(issue)

            # Генерация рекомендаций
            for issue_type, issues_list in by_type.items():
                recommendations.append(
                    {
                        "service": service_name,
                        "issue_type": issue_type,
                        "count": len(issues_list),
                        "recommendation": self._generate_recommendation(issue_type, len(issues_list)),
                    }
                )

        return recommendations

    def _generate_recommendation(self, issue_type: str, count: int) -> str:
        """Генерация рекомендации для типа проблемы"""
        recommendations = {
            "syntax_error": f"Исправьте {count} синтаксических ошибок",
            "type_error": f"Исправьте {count} ошибок типов",
            "security_vulnerability": f"Критически важно исправить {count} уязвимостей безопасности",
            "code_quality": f"Улучшите качество кода: {count} проблем",
            "test_coverage": f"Увеличьте покрытие тестами на {count} сервисов",
            "documentation": f"Добавьте документацию для {count} компонентов",
        }

        return recommendations.get(issue_type, f"Рассмотрите {count} проблем")

    def fix_code_safely(self, service_name: str, issues: list[dict], mode: str = "semi_autonomous") -> dict[str, Any]:
        """
        Безопасное исправление кода
        :param service_name: Имя сервиса
        :param issues: Список проблем
        :param mode: Режим исправления (autonomous, semi_autonomous, manual)
        :return: Результат исправления
        """
        if mode == "autonomous":
            return self.code_fixer.fix_all(issues)
        elif mode == "semi_autonomous":
            # Запрос подтверждения для критичных проблем
            critical_issues = [i for i in issues if i.get("severity") == "critical"]

            if critical_issues:
                approved = self.guardrails.request_approval(action="fix_critical_issues", details=critical_issues)

                if not approved:
                    return {"status": "human_approval_required", "issues": critical_issues}

            return self.code_fixer.fix_all(issues, approved=True)
        else:
            return {"status": "manual_approval_required"}
