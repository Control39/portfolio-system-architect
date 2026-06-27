#!/usr/bin/env python3
"""ddd_show_issues.py - Показать архитектурные проблемы"""

import json
import sys
from pathlib import Path


def find_architecture_issues() -> list[dict]:
    """Найти архитектурные проблемы"""
    issues = []

    apps_dir = Path("apps")
    if not apps_dir.exists():
        return issues

    services = [d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]

    # Проверить наличие README.md в каждом сервисе
    for service_dir in services:
        readme_path = service_dir / "README.md"
        if not readme_path.exists():
            issues.append(
                {
                    "type": "missing_readme",
                    "service": service_dir.name,
                    "severity": "medium",
                    "message": f"Сервис {service_dir.name} не имеет README.md",
                }
            )

    # Проверить наличие Dockerfile
    for service_dir in services:
        dockerfile_path = service_dir / "Dockerfile"
        if not dockerfile_path.exists():
            issues.append(
                {
                    "type": "missing_dockerfile",
                    "service": service_dir.name,
                    "severity": "low",
                    "message": f"Сервис {service_dir.name} не имеет Dockerfile",
                }
            )

    # Проверить наличие requirements.txt
    for service_dir in services:
        req_path = service_dir / "requirements.txt"
        if not req_path.exists():
            issues.append(
                {
                    "type": "missing_requirements",
                    "service": service_dir.name,
                    "severity": "low",
                    "message": f"Сервис {service_dir.name} не имеет requirements.txt",
                }
            )

    # Проверить на пустые сервисы (нет Python файлов)
    for service_dir in services:
        py_files = list(service_dir.rglob("*.py"))
        if len(py_files) == 0:
            issues.append(
                {
                    "type": "empty_service",
                    "service": service_dir.name,
                    "severity": "high",
                    "message": f"Сервис {service_dir.name} не содержит Python файлов",
                }
            )

    return issues


def main():
    """Main entry point"""
    print("🚨 АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ")
    print("=" * 60)

    issues = find_architecture_issues()

    if not issues:
        print("✅ Проблем не найдено!")
        return

    # Сгруппировать по типу
    issues_by_type = {}
    for issue in issues:
        issue_type = issue["type"]
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)

    # Вывести проблемы
    severity_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    total_issues = len(issues)

    for issue_type in sorted(issues_by_type.keys()):
        type_issues = issues_by_type[issue_type]
        print(f"\n{severity_colors.get(type_issues[0]['severity'], '⚪')} {issue_type} ({len(type_issues)} шт.)")
        print("-" * 60)

        for issue in type_issues:
            print(f"   {issue['message']}")

    # Сохранить в JSON
    output_file = Path("ddd_issues.json")
    output_file.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"📊 Всего проблем: {total_issues}")
    print(f"📄 Сохранено в {output_file}")


if __name__ == "__main__":
    main()
