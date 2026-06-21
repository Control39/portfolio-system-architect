#!/usr/bin/env python3
"""
ddd_show_dependencies.sh - Показать зависимости между сервисами
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

    print("🔗 ЗАВИСИМОСТИ МЕЖДУ СЕРВИСАМИ:")
    print("=" * 60)

    for context, deps in data.get("dependencies", {}).items():
        if deps:
            print(f"\n📁 {context}:")
            for dep in deps:
                print(f"   └─→ {dep}")

    # Граф зависимостей (Mermaid)
    print("\n\n📊 ГРАФ ЗАВИСИМОСТЕЙ (Mermaid):")
    print("```mermaid")
    print("graph TD")
    for context, deps in data.get("dependencies", {}).items():
        for dep in deps:
            print(f"    {context} --> {dep}")
    print("```")


if __name__ == "__main__":
    main()
