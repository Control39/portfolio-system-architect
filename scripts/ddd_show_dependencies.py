#!/usr/bin/env python3
"""ddd_show_dependencies.py - Показать зависимости между сервисами"""

import json
import sys
from pathlib import Path


def get_service_dependencies(service_dir: Path) -> list[str]:
    """Получить зависимости сервиса из его Python файлов"""
    dependencies = set()

    for py_file in service_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            # Искать импорты из других сервисов
            import_lines = [line for line in content.split("\n") if line.strip().startswith(("from ", "import "))]

            for line in import_lines:
                # Извлечь имя сервиса из импорта
                if "apps/" in line:
                    parts = line.split("apps/")
                    if len(parts) > 1:
                        service_name = parts[1].split("/")[0]
                        dependencies.add(service_name)
        except Exception:
            continue

    return sorted(list(dependencies))


def main():
    """Main entry point"""
    apps_dir = Path("apps")

    if not apps_dir.exists():
        print("❌ Папка apps/ не найдена")
        sys.exit(1)

    print("📦 ЗАВИСИМОСТИ МЕЖДУ СЕРВИСАМИ")
    print("=" * 60)

    services = sorted([d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith("_")])

    dependencies_map = {}

    for service_dir in services:
        service_name = service_dir.name
        deps = get_service_dependencies(service_dir)
        dependencies_map[service_name] = deps

    # Вывести зависимости
    for service_name in sorted(dependencies_map.keys()):
        deps = dependencies_map[service_name]
        if deps:
            print(f"\n🔹 {service_name}")
            for dep in deps:
                print(f"   📦 -> {dep}")
        else:
            print(f"\n🔹 {service_name}")
            print("   📦 (нет внешних зависимостей)")

    # Сохранить в JSON
    output_file = Path("ddd_dependencies.json")
    output_file.write_text(json.dumps(dependencies_map, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"📊 Сохранено в {output_file}")
    print(f"📄 Всего сервисов: {len(dependencies_map)}")


if __name__ == "__main__":
    main()
