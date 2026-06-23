"""
Модуль безопасности для когнитивного агента
Аудит безопасности и устранение уязвимостей
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class SecurityGuard:
    """Охранник безопасности"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.project_path = autonomous_agent.project_path
        self.security_auditor = (
            autonomous_agent.security_auditor if hasattr(autonomous_agent, "security_auditor") else None
        )

    def perform_full_security_audit(self) -> dict[str, Any]:
        """
        Полный аудит безопасности репозитория
        :return: Отчет о безопасности
        """
        audit_results = {"services": {}, "vulnerabilities": [], "recommendations": [], "security_score": 100.0}

        # Аудит каждого сервиса
        for service in self.autonomous_agent.service_registry.services:
            service_audit = self.audit_service(service.path)
            audit_results["services"][service.name] = service_audit

            # Сбор уязвимостей
            vulnerabilities = service_audit.get("vulnerabilities", [])
            audit_results["vulnerabilities"].extend(vulnerabilities)

            # Сбор рекомендаций
            recommendations = service_audit.get("recommendations", [])
            audit_results["recommendations"].extend(recommendations)

        # Расчет оценки безопасности
        audit_results["security_score"] = self._calculate_security_score(audit_results["vulnerabilities"])

        return audit_results

    def audit_service(self, service_path: str) -> dict[str, Any]:
        """
        Аудит безопасности сервиса
        :param service_path: Путь к сервису
        :return: Результат аудита
        """
        result = {"path": service_path, "vulnerabilities": [], "recommendations": [], "security_checks": {}}

        # Проверка файлов на уязвимости
        vulnerabilities = self._scan_files_for_vulnerabilities(service_path)
        result["vulnerabilities"] = vulnerabilities

        # Генерация рекомендаций
        result["recommendations"] = self._generate_recommendations(vulnerabilities)

        # Проверки безопасности
        result["security_checks"] = {
            "secrets_scanned": self._check_secrets(service_path),
            "dependencies_scanned": self._check_dependencies(service_path),
            "code_scanned": self._check_code_security(service_path),
        }

        return result

    def _scan_files_for_vulnerabilities(self, service_path: str) -> list[dict[str, Any]]:
        """Сканирование файлов на уязвимости"""
        vulnerabilities = []

        try:
            path = Path(service_path)
            if not path.exists():
                return vulnerabilities

            # Ищем потенциально опасные файлы
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read(10000)  # Ограничиваем чтение

                            # Проверка на секреты
                            if self._contains_secrets(content):
                                vulnerabilities.append(
                                    {
                                        "type": "secrets_exposed",
                                        "file": str(file_path),
                                        "severity": "critical",
                                        "description": "Обнаружены потенциальные секреты",
                                    }
                                )

                            # Проверка на SQL инъекции
                            if self._contains_sql_injection(content):
                                vulnerabilities.append(
                                    {
                                        "type": "sql_injection",
                                        "file": str(file_path),
                                        "severity": "critical",
                                        "description": "Обнаружены потенциальные SQL инъекции",
                                    }
                                )

                            # Проверка на XSS
                            if self._contains_xss(content):
                                vulnerabilities.append(
                                    {
                                        "type": "xss_vulnerability",
                                        "file": str(file_path),
                                        "severity": "high",
                                        "description": "Обнаружены потенциальные XSS уязвимости",
                                    }
                                )

                    except Exception:
                        continue

        except Exception as e:
            vulnerabilities.append(
                {"type": "scan_error", "severity": "medium", "description": f"Ошибка сканирования: {str(e)}"}
            )

        return vulnerabilities

    def _contains_secrets(self, content: str) -> bool:
        """Проверка на наличие секретов"""
        secret_patterns = [
            "api_key",
            "api_key =",
            "API_KEY",
            "secret",
            "secret =",
            "SECRET",
            "password",
            "password =",
            "PASSWORD",
            "token",
            "token =",
            "TOKEN",
            "aws_access_key",
            "aws_secret_key",
        ]

        return any(pattern.lower() in content.lower() for pattern in secret_patterns)

    def _contains_sql_injection(self, content: str) -> bool:
        """Проверка на SQL инъекции"""
        sql_patterns = ["SELECT * FROM", "DROP TABLE", "INSERT INTO", "DELETE FROM", "UNION SELECT"]

        return any(pattern.lower() in content.lower() for pattern in sql_patterns)

    def _contains_xss(self, content: str) -> bool:
        """Проверка на XSS"""
        xss_patterns = ["<script>", "javascript:", "onerror=", "onload="]

        return any(pattern.lower() in content.lower() for pattern in xss_patterns)

    def _check_secrets(self, service_path: str) -> bool:
        """Проверка сканирования секретов"""
        # TODO: Интеграция с реальным сканером секретов
        return True

    def _check_dependencies(self, service_path: str) -> bool:
        """Проверка сканирования зависимостей"""
        # TODO: Интеграция с реальным сканером зависимостей
        return True

    def _check_code_security(self, service_path: str) -> bool:
        """Проверка безопасности кода"""
        # TODO: Интеграция с реальным сканером кода
        return True

    def _generate_recommendations(self, vulnerabilities: list[dict]) -> list[dict[str, str]]:
        """Генерация рекомендаций"""
        recommendations = []

        for vuln in vulnerabilities:
            if vuln["type"] == "secrets_exposed":
                recommendations.append(
                    {
                        "recommendation": "Удалить или переместить секреты в безопасное хранилище",
                        "priority": "critical",
                        "type": "secrets",
                    }
                )
            elif vuln["type"] == "sql_injection":
                recommendations.append(
                    {
                        "recommendation": "Использовать параметризованные запросы",
                        "priority": "critical",
                        "type": "sql_injection",
                    }
                )
            elif vuln["type"] == "xss_vulnerability":
                recommendations.append(
                    {"recommendation": "Экранировать пользовательский ввод", "priority": "high", "type": "xss"}
                )

        return recommendations

    def _calculate_security_score(self, vulnerabilities: list[dict]) -> float:
        """Расчет оценки безопасности"""
        score = 100.0

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            if severity == "critical":
                score -= 30
            elif severity == "high":
                score -= 20
            elif severity == "medium":
                score -= 10
            else:
                score -= 5

        return max(0.0, round(score, 2))

    def remediate_vulnerabilities(self, vulnerabilities: list[dict]) -> dict[str, Any]:
        """
        Устранение уязвимостей
        :param vulnerabilities: Список уязвимостей
        :return: Результат устранения
        """
        results = {"fixed": [], "mitigated": [], "documented": [], "failed": []}

        for vuln in vulnerabilities:
            try:
                if vuln["severity"] == "critical":
                    # Пытаемся исправить критические
                    if self._fix_vulnerability(vuln):
                        results["fixed"].append(vuln)
                    else:
                        results["documented"].append(vuln)
                elif vuln["severity"] == "high":
                    # Митигируем высокие
                    if self._mitigate_vulnerability(vuln):
                        results["mitigated"].append(vuln)
                    else:
                        results["documented"].append(vuln)
                else:
                    results["documented"].append(vuln)

            except Exception as e:
                results["failed"].append({"vulnerability": vuln, "error": str(e)})

        return results

    def _fix_vulnerability(self, vuln: dict) -> bool:
        """Попытка исправления уязвимости"""
        # Логика исправления
        return False  # TODO: Реализовать исправление

    def _mitigate_vulnerability(self, vuln: dict) -> bool:
        """Попытка митигации уязвимости"""
        # Логика митигации
        return False  # TODO: Реализовать митигацию

    def scan_service(self, service_name: str) -> dict[str, Any]:
        """
        Сканирование сервиса на уязвимости
        :param service_name: Имя сервиса
        :return: Результат сканирования
        """
        service = self.autonomous_agent.service_registry.get_profile_by_name(service_name)
        if not service:
            return {"error": f"Сервис {service_name} не найден"}

        return self.audit_service(service.path)

    def generate_security_recommendations(self) -> list[dict[str, Any]]:
        """
        Генерация рекомендаций по безопасности
        :return: Список рекомендаций
        """
        recommendations = []

        # Рекомендации на основе текущей архитектуры
        recommendations.append(
            {
                "recommendation": "Внедрить CI/CD пайплайны для автоматического сканирования безопасности",
                "priority": "high",
                "effort": "medium",
                "impact": "high",
            }
        )

        recommendations.append(
            {
                "recommendation": "Использовать секреты через менеджер секретов (Vault, AWS Secrets Manager)",
                "priority": "critical",
                "effort": "low",
                "impact": "high",
            }
        )

        recommendations.append(
            {
                "recommendation": "Регулярно обновлять зависимости для устранения уязвимостей",
                "priority": "high",
                "effort": "low",
                "impact": "medium",
            }
        )

        return recommendations
