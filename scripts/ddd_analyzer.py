#!/usr/bin/env python3
"""ddd_analyzer.py - Полный DDD анализ репозитория"""

import json
import sys
from datetime import datetime
from pathlib import Path


def analyze_service(service_dir: Path) -> dict:
    """Анализ одного сервиса"""
    result = {
        "name": service_dir.name,
        "path": str(service_dir),
        "files": [],
        "python_files": [],
        "readme": False,
        "dockerfile": False,
        "requirements": False,
        "tests": [],
        "modules": [],
    }

    # Подсчет файлов
    for item in service_dir.rglob("*"):
        if item.is_file():
            result["files"].append(str(item.relative_to(service_dir)))

            if item.suffix == ".py":
                result["python_files"].append(str(item.relative_to(service_dir)))

            if item.suffix == ".py" and item.name.startswith("test_"):
                result["tests"].append(str(item.relative_to(service_dir)))

            if item.name == "README.md":
                result["readme"] = True

            if item.name == "Dockerfile":
                result["dockerfile"] = True

            if item.name == "requirements.txt":
                result["requirements"] = True

            if item.is_dir() and item.name not in [".git", "__pycache__"]:
                result["modules"].append(item.name)

    # Удалить дубликаты
    result["modules"] = list(set(result["modules"]))

    return result


def analyze_repository(root_dir: Path = Path(".")) -> dict:
    """Полный анализ репозитория"""
    start_time = datetime.now()

    apps_dir = root_dir / "apps"

    result = {
        "analysis_time": start_time.isoformat(),
        "repository_root": str(root_dir),
        "services": [],
        "summary": {
            "total_services": 0,
            "total_python_files": 0,
            "total_tests": 0,
            "services_with_readme": 0,
            "services_with_dockerfile": 0,
            "services_with_requirements": 0,
        },
    }

    if not apps_dir.exists():
        result["error"] = "Папка apps/ не найдена"
        return result

    services = [d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]

    result["summary"]["total_services"] = len(services)

    for service_dir in services:
        service_analysis = analyze_service(service_dir)
        result["services"].append(service_analysis)

        # Обновление статистики
        result["summary"]["total_python_files"] += len(service_analysis["python_files"])
        result["summary"]["total_tests"] += len(service_analysis["tests"])

        if service_analysis["readme"]:
            result["summary"]["services_with_readme"] += 1

        if service_analysis["dockerfile"]:
            result["summary"]["services_with_dockerfile"] += 1

        if service_analysis["requirements"]:
            result["summary"]["services_with_requirements"] += 1

    # Расчет времени анализа
    end_time = datetime.now()
    result["analysis_duration"] = str(end_time - start_time)

    return result


def main():
    """Main entry point"""
    print("🏗️  ПОЛНЫЙ DDD АНАЛИЗ РЕПОЗИТОРИЯ")
    print("=" * 60)

    # Поиск корня репозитория
    root_dir = Path(__file__).parent.parent

    # Анализ
    result = analyze_repository(root_dir)

    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
        sys.exit(1)

    # Вывод краткой статистики
    summary = result["summary"]
    print(f"\n📊 КРАТКАЯ СТАТИСТИКА:")
    print(f"   Всего сервисов: {summary['total_services']}")
    print(f"   Python файлов: {summary['total_python_files']}")
    print(f"   Тестов: {summary['total_tests']}")
    print(f"   С сервисами README: {summary['services_with_readme']}")
    print(f"   С Dockerfile: {summary['services_with_dockerfile']}")
    print(f"   С requirements.txt: {summary['services_with_requirements']}")

    # Вывод деталей сервисов
    print(f"\n{'=' * 60}")
    print("📄 ДЕТАЛЬНЫЕ СВЕДЕНИЯ О СЕРВИСАХ:")
    print("=" * 60)

    for service in result["services"]:
        print(f"\n🔹 {service['name']}")
        print(f"   Папка: {service['path']}")
        print(f"   Python файлов: {len(service['python_files'])}")
        print(f"   Тестов: {len(service['tests'])}")
        print(f"   README.md: {'✅' if service['readme'] else '❌'}")
        print(f"   Dockerfile: {'✅' if service['dockerfile'] else '❌'}")
        print(f"   Requirements: {'✅' if service['requirements'] else '❌'}")
        if service["modules"]:
            print(f"   Модули: {', '.join(service['modules'][:5])}...")

    # Сохранение JSON отчета
    json_report = root_dir / "ddd_analysis_report.json"
    json_report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # Генерация текстового отчета
    txt_report = root_dir / "ddd_analysis_report.txt"
    txt_content = f"""{"=" * 60}
DDD АНАЛИЗ РЕПОЗИТОРИЯ
{"=" * 60}

Дата анализа: {result['analysis_time']}
Длительность: {result['analysis_duration']}

{"=" * 60}
СВОДКА
{"=" * 60}

Всего сервисов: {summary['total_services']}
Python файлов: {summary['total_python_files']}
Тестов: {summary['total_tests']}
С сервисами README: {summary['services_with_readme']}
С Dockerfile: {summary['services_with_dockerfile']}
С requirements.txt: {summary['services_with_requirements']}

{"=" * 60}
ДЕТАЛИ СЕРВИСОВ
{"=" * 60}

"""

    for service in result["services"]:
        txt_content += f"""
🔹 {service['name']}
   Папка: {service['path']}
   Python файлов: {len(service['python_files'])}
   Тестов: {len(service['tests'])}
   README.md: {'Да' if service['readme'] else 'Нет'}
   Dockerfile: {'Да' if service['dockerfile'] else 'Нет'}
   Requirements: {'Да' if service['requirements'] else 'Нет'}
"""

    txt_report.write_text(txt_content, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"✅ Анализ завершен!")
    print(f"📄 JSON отчет: {json_report}")
    print(f"📄 Текст отчет: {txt_report}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
