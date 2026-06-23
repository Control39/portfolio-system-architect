#!/usr/bin/env python3
"""
ddd_analyze_context.sh - Анализ конкретного домена
"""

import json
import sys
from pathlib import Path


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else None

    if not domain:
        print("🏗️ Анализ доменного контекста")
        print("=" * 50)
        print("\nДоступные домены:")

        apps_path = Path("apps")
        if apps_path.exists():
            for app_dir in apps_path.iterdir():
                if app_dir.is_dir() and not app_dir.name.startswith("."):
                    print(f"   - {app_dir.name}")

        print("\nИспользование: python ddd_analyze_context.py <domain_name>")
        return

    # Проверяем отчет
    report_file = Path("ddd_analysis_report.json")
    if not report_file.exists():
        print("❌ Отчет не найден. Сначала запустите ddd_full_scan.sh")
        exit(1)

    with open(report_file) as f:
        data = json.load(f)

    if domain not in data.get("domains", {}):
        print(f'❌ Домен "{domain}" не найден')
        exit(1)

    domain_info = data["domains"][domain]

    print(f"\n📁 Анализ домена: {domain}")
    print("=" * 50)

    print(f'   Путь: {domain_info["path"]}')
    print(f'   Тесты: {"✅" if domain_info.get("has_tests") else "❌"}')

    if domain_info.get("sub_domains"):
        print(f'   Под-домены: {", ".join(domain_info["sub_domains"])}')

    # Ищем файлы в домене
    domain_path = Path(domain_info["path"])

    if domain_path.exists():
        py_files = list(domain_path.rglob("*.py"))
        print(f"\n📄 Python файлов: {len(py_files)}")

        # Ищем сущности
        entities = []
        for py_file in py_files:
            try:
                with open(py_file) as f:
                    content = f.read()
                    if "class" in content:
                        entities.append(py_file.name)
            except OSError:
                pass

        print(f"📦 Найдено файлов с классами: {len(entities)}")

        # Проверяем структуру
        has_src = (domain_path / "src").exists()
        has_tests = (domain_path / "tests").exists()
        has_init = (domain_path / "__init__.py").exists()

        print("\n📂 Структура:")
        print(f'   src/: {"✅" if has_src else "❌"}')
        print(f'   tests/: {"✅" if has_tests else "❌"}')
        print(f'   __init__.py: {"✅" if has_init else "❌"}')

        # Ищем API
        api_files = []
        for py_file in py_files:
            try:
                with open(py_file) as f:
                    content = f.read()
                    if "router" in content or "app." in content or "@app" in content:
                        api_files.append(py_file.name)
            except OSError:
                pass

        if api_files:
            print(f"\n📡 Найдено API файлов: {len(api_files)}")
            for f in api_files[:3]:
                print(f"   - {f}")

    # Проверяем API контракты
    if domain in data.get("api_contracts", {}):
        apis = data["api_contracts"][domain]
        print(f"\n📡 API эндпоинты ({len(apis)}):")
        for api in apis[:5]:
            print(f'   {api["method"]} {api["path"]}')


if __name__ == "__main__":
    main()
