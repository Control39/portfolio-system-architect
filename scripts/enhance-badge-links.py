#!/usr/bin/env python3
"""Скрипт для улучшения бейджей: добавляет ссылки на детальные отчеты.
"""

import re
from pathlib import Path


def enhance_badge_links(readme_content):
    """Улучшить бейджи, добавив ссылки на детальные отчеты."""
    # Паттерны для поиска бейджей без ссылок
    patterns = [
        # CI бейдж
        (
            r'(<img src="https://img.shields.io/github/actions/workflow/status/[^>]+alt="CI Status"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/actions/workflows/ci.yml">\1</a>',
        ),
        # Coverage бейдж
        (
            r'(<img src="https://img.shields.io/badge/Code%20Coverage-[^>]+alt="Code Coverage"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/actions/workflows/ci.yml">\1</a>',
        ),
        # Test status бейдж
        (
            r'(<img src="https://img.shields.io/badge/Tests-[^>]+alt="Test Status"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/actions">\1</a>',
        ),
        # Security бейджи
        (
            r'(<img src="https://img.shields.io/badge/Security-Trivy%20Scan[^>]+alt="Security: Trivy Scan"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/security/scanning">\1</a>',
        ),
        (
            r'(<img src="https://img.shields.io/badge/Bandit-Check[^>]+alt="Bandit Security Check"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/security/scanning">\1</a>',
        ),
        (
            r'(<img src="https://img.shields.io/badge/Security-Scan[^>]+alt="Security Scan"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/security">\1</a>',
        ),
        # Dependabot бейдж
        (
            r'(<img src="https://img.shields.io/badge/dependabot-enabled[^>]+alt="Dependabot Enabled"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/security/dependabot">\1</a>',
        ),
        # Python version бейдж
        (
            r'(<img src="https://img.shields.io/badge/Python-[^>]+alt="Python [^"]+"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/blob/main/pyproject.toml">\1</a>',
        ),
        # Dependencies бейдж
        (
            r'(<img src="https://img.shields.io/badge/Dependencies-[^>]+alt="Dependencies"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/blob/main/requirements.txt">\1</a>',
        ),
        # License бейдж
        (
            r'(<img src="https://img.shields.io/badge/License-MIT[^>]+alt="License: MIT"[^>]*>)',
            r'<a href="https://github.com/leadarchitect-ai/portfolio-system-architect/blob/main/LICENSE">\1</a>',
        ),
    ]

    enhanced_content = readme_content

    for pattern, replacement in patterns:
        enhanced_content = re.sub(pattern, replacement, enhanced_content)

    return enhanced_content


def add_report_links_section(readme_content):
    """Добавить секцию с ссылками на детальные отчеты."""
    reports_section = """
## 📊 Detailed Reports & Metrics

For detailed insights behind each badge, explore these reports:

| Report | Description | Link |
|--------|-------------|------|
| **CI/CD Pipeline** | Complete test results, build logs, and deployment status | [GitHub Actions](https://github.com/leadarchitect-ai/portfolio-system-architect/actions) |
| **Test Coverage** | Line-by-line coverage analysis | [Coverage Report](https://github.com/leadarchitect-ai/portfolio-system-architect/actions/workflows/ci.yml) |
| **Security Scan** | Vulnerability assessment with Trivy & Bandit | [Security Scanning](https://github.com/leadarchitect-ai/portfolio-system-architect/security/scanning) |
| **Dependency Health** | Outdated packages and security advisories | [Dependabot](https://github.com/leadarchitect-ai/portfolio-system-architect/security/dependabot) |
| **Code Quality** | Linting, formatting, and style checks | [Pre-commit Reports](https://github.com/leadarchitect-ai/portfolio-system-architect/actions/workflows/code-quality.yml) |
| **Performance Metrics** | API response times and resource usage | [Monitoring Dashboards](docs/screenshots/monitoring/) |

**💡 Tip:** Click on any badge above to jump directly to its detailed report.
"""

    # Находим место для вставки (после бейджей, перед "Who Is This For?")
    if "## 🎯 Who Is This For?" in readme_content:
        return readme_content.replace(
            "## 🎯 Who Is This For?",
            reports_section + "\n## 🎯 Who Is This For?",
        )

    return readme_content


def main():
    """Основная функция."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found")
        return

    content = readme_path.read_text(encoding="utf-8")

    print("Enhancing badge links with detailed reports...")

    # Улучшаем ссылки на бейджах
    enhanced_content = enhance_badge_links(content)

    # Добавляем секцию с отчетами
    final_content = add_report_links_section(enhanced_content)

    # Проверяем, есть ли изменения
    if final_content != content:
        readme_path.write_text(final_content, encoding="utf-8")
        print("✅ README.md updated with enhanced badge links and reports section")

        # Показываем статистику
        old_badges = len(re.findall(r"<img[^>]*badge[^>]*>", content))
        new_badges = len(re.findall(r"<img[^>]*badge[^>]*>", final_content))
        linked_badges = len(
            re.findall(r"<a[^>]*><img[^>]*badge[^>]*></a>", final_content)
        )

        print("📊 Statistics:")
        print(f"  - Total badges: {new_badges}")
        print(f"  - Badges with links: {linked_badges}")
        print(f"  - Percentage linked: {(linked_badges/new_badges)*100:.1f}%")
    else:
        print("✅ Badge links are already enhanced")


if __name__ == "__main__":
    main()
