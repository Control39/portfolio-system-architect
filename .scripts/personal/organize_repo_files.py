#!/usr/bin/env python3
"""
Скрипт для организации файлов репозитория
Переносит логи и отчеты в соответствующие директории
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


def organize_repo_files():
    """
    Организует файлы в репозитории, перемещая логи и отчеты в соответствующие директории
    """
    repo_root = Path(__file__).parent.parent

    # Создаем необходимые директории, если они не существуют
    logs_dir = repo_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    reports_dir = repo_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Определяем файлы, которые нужно переместить
    log_patterns = [
        r".*_log\.txt$",
        r".*_log\.json$",
        r"log.*\.txt$",
        r"log.*\.json$",
        r".*\.log$",
        r"it_compass\.log$",
        r"orchestrator\.log$",
    ]

    report_patterns = [
        r".*report\.json$",
        r".*report\.txt$",
        r".*analysis.*\.json$",
        r".*analysis.*\.txt$",
        r".*self_analysis.*",
        r".*strategic.*report.*",
        r".*ddd.*analysis.*",
        r".*health.*check.*",
        r".*diagnostic.*",
        r".*audit.*report.*",
    ]

    moved_files = {"logs": [], "reports": []}

    # Перебираем файлы в корне репозитория
    for file_path in repo_root.iterdir():
        if file_path.is_file():
            file_name = file_path.name

            # Проверяем, является ли файл логом
            is_log = any(re.search(pattern, file_name, re.IGNORECASE) for pattern in log_patterns)

            # Проверяем, является ли файл отчетом
            is_report = any(re.search(pattern, file_name, re.IGNORECASE) for pattern in report_patterns)

            if is_log:
                dest_path = logs_dir / file_name
                shutil.move(str(file_path), str(dest_path))
                moved_files["logs"].append(file_name)
                print(f"Перемещен лог-файл: {file_name}")

            elif is_report:
                dest_path = reports_dir / file_name
                shutil.move(str(file_path), str(dest_path))
                moved_files["reports"].append(file_name)
                print(f"Перемещен отчет: {file_name}")

    # Также перемещаем файлы в поддиректории logs и reports
    archive_dir = repo_root / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Архивируем старые файлы в этих директориях, если они были
    old_logs = list(logs_dir.glob("*.old")) + list(logs_dir.glob("*_old.*"))
    old_reports = list(reports_dir.glob("*.old")) + list(reports_dir.glob("*_old.*"))

    for old_file in old_logs + old_reports:
        archive_path = archive_dir / f"{old_file.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(old_file), str(archive_path))

    print("\nОрганизация файлов завершена!")
    print(f"Перемещено логов: {len(moved_files['logs'])}")
    print(f"Перемещено отчетов: {len(moved_files['reports'])}")

    return moved_files


def create_priority_marker(priority_level: str, description: str, target_file: str):
    """
    Создает маркер приоритета для указанного файла
    """
    repo_root = Path(__file__).parent.parent
    priority_markers_dir = repo_root / "priority_markers"
    priority_markers_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    marker_filename = f"{timestamp}_{priority_level}_{Path(target_file).name}.txt"
    marker_path = priority_markers_dir / marker_filename

    with open(marker_path, "w", encoding="utf-8") as f:
        f.write("ПРИОРИТЕТНЫЙ ФАЙЛ\n")
        f.write(f"Уровень: {priority_level}\n")
        f.write(f"Описание: {description}\n")
        f.write(f"Целевой файл: {target_file}\n")
        f.write(f"Дата создания: {datetime.now()}\n")
        f.write("Статус: АКТИВЕН\n")

    print(f"Создан маркер приоритета: {marker_filename}")
    return marker_path


def setup_agent_config_for_new_structure():
    """
    Обновляет конфигурацию агента для использования новых директорий
    """
    repo_root = Path(__file__).parent.parent

    # Обновляем конфигурационный файл агента, если он существует
    agent_config_paths = [
        repo_root / "agents" / "cognitive_agent" / "config" / "guardrails.yaml",
        repo_root / "agents" / "cognitive_agent" / "config" / "config.yaml",
        repo_root / "config" / "ai-config.yaml",
    ]

    for config_path in agent_config_paths:
        if config_path.exists():
            print(f"Обновление конфигурации агента: {config_path}")
            # Здесь можно добавить логику обновления конфигурации
            # для использования новых директорий logs и reports
            break


if __name__ == "__main__":
    print("Запуск скрипта организации файлов репозитория...")
    print("=" * 60)

    # Организуем файлы
    moved_files = organize_repo_files()

    # Обновляем конфигурацию агента
    setup_agent_config_for_new_structure()

    print("\nДополнительно:")
    print("- Файлы логов теперь хранятся в директории ./logs/")
    print("- Файлы отчетов теперь хранятся в директории ./reports/")
    print("- Для создания маркера приоритета используйте create_priority_marker(level, description, filename)")
    print("- Старые файлы архивируются в директории ./archive/")

    print("\nПример создания маркера приоритета:")
    print("create_priority_marker('КРИТИЧНО', 'Требует немедленного внимания', 'some_report.json')")
