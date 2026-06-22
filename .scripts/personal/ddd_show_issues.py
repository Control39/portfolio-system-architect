#!/usr/bin/env python3
"""
ddd_show_issues.sh - Показать архитектурные проблемы
"""

import json
from pathlib import Path


def main():
    report_file = Path("ddd_analysis_report.json")
    if not report_file.exists():
        print("❌ Отчет не найден. Сначала запустите ddd_full_scan.sh")
        exit(1)

    with open(report_file) as f:
        data = json.load(f)

    issues = data.get("issues", [])

    if not issues:
        print("✅ Архитектурных проблем не найдено!")
        exit(0)

    print("🐛 АРХ��ТЕКТУРНЫЕ ПРОБЛЕМЫ:")
    print("=" * 60)

    # Группировка по серьезности
    critical = [i for i in issues if i["severity"] == "high"]
    medium = [i for i in issues if i["severity"] == "medium"]
    low = [i for i in issues if i["severity"] == "low"]

    if critical:
        print(f"\n🔴 КРИТИЧЕСКИЕ ({len(critical)}):")
        for issue in critical:
            print(f'   • {issue["message"]}')

    if medium:
        print(f"\n🟡 СРЕДНИЕ ({len(medium)}):")
        for issue in medium:
            print(f'   • {issue["message"]}')

    if low:
        print(f"\n🟢 НИЗКИЕ ({len(low)}):")
        for issue in low:
            print(f'   • {issue["message"]}')


if __name__ == "__main__":
    main()
