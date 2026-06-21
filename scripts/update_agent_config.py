#!/usr/bin/env python3
"""
Скрипт для обновления конфигурации когнитивного агента
Обновляет пути к логам и отчетам в соответствии с новой структурой репозитория
"""

import json
from pathlib import Path

import yaml


def update_agent_config():
    """
    Обновляет конфигурацию агента для использования новых директорий
    """
    repo_root = Path(__file__).parent.parent

    # Пути к возможным конфигурационным файлам агента
    config_paths = [
        repo_root / "agents" / "cognitive_agent" / "config" / "guardrails.yaml",
        repo_root / "agents" / "cognitive_agent" / "config" / "config.yaml",
        repo_root / "config" / "ai-config.yaml",
    ]

    updated_configs = []

    for config_path in config_paths:
        if config_path.exists():
            print(f"Обработка конфигурационного файла: {config_path}")

            # Читаем текущий конфиг
            with open(config_path, encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            # Обновляем пути к логам и отчетам
            if "logging" in config_data:
                if "log_directory" in config_data["logging"]:
                    config_data["logging"]["log_directory"] = "./logs"
                if "log_file" in config_data["logging"]:
                    current_file = config_data["logging"]["log_file"]
                    config_data["logging"]["log_file"] = f"./logs/{current_file}"
            else:
                # Добавляем секцию логирования, если её нет
                config_data["logging"] = {
                    "log_directory": "./logs",
                    "log_level": "INFO",
                    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }

            # Обновляем пути к отчетам
            if "reports" in config_data:
                if "output_directory" in config_data["reports"]:
                    config_data["reports"]["output_directory"] = "./reports"
            elif "output" in config_data:
                if "reports_directory" in config_data["output"]:
                    config_data["output"]["reports_directory"] = "./reports"
            else:
                # Добавляем секцию отчетов, если её нет
                if "output" not in config_data:
                    config_data["output"] = {}
                config_data["output"]["reports_directory"] = "./reports"

            # Сохраняем обновленный конфиг
            with open(config_path, "w", encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

            updated_configs.append(str(config_path))
            print(f"Конфигурация обновлена: {config_path}")

    return updated_configs


def create_agent_file_manager_config():
    """
    Создает конфигурацию для менеджера файлов агента
    """
    repo_root = Path(__file__).parent.parent
    agent_config_dir = repo_root / "agents" / "cognitive_agent" / "config"
    agent_config_dir.mkdir(exist_ok=True)

    file_manager_config = {
        "directories": {
            "logs": "./logs",
            "reports": "./reports",
            "temp": "./temp",
            "data": "./data",
            "models": "./models",
            "config": "./config",
        },
        "file_types": {
            "logs": [".log", ".txt"],
            "reports": [".json", ".txt", ".csv", ".md"],
            "critical_indicators": ["CRITICAL", "URGENT", "IMPORTANT"],
        },
        "retention_policy": {"logs_days": 30, "reports_days": 90},
        "priority_keywords": ["CRITICAL", "URGENT", "IMPORTANT", "HIGH_PRIORITY", "ATTENTION_REQUIRED", "BLOCKER"],
    }

    config_path = agent_config_dir / "file_manager_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(file_manager_config, f, indent=2, ensure_ascii=False)

    print(f"Создана конфигурация менеджера файлов: {config_path}")
    return str(config_path)


def create_priority_notification_system():
    """
    Создает базовую систему уведомлений о приоритетных файлах
    """
    repo_root = Path(__file__).parent.parent

    notification_script = '''#!/usr/bin/env python3
"""
Система уведомлений о приоритетных файлах
Проверяет наличие файлов с высоким приоритетом и создает уведомления
"""

import os
import json
from pathlib import Path
from datetime import datetime


def check_priority_files():
    """
    Проверяет наличие приоритетных файлов и возвращает список
    """
    repo_root = Path(__file__).parent.parent

    # Загружаем конфигурацию агента
    agent_config_path = repo_root / "agents" / "cognitive_agent" / "config" / "file_manager_config.json"

    if not agent_config_path.exists():
        print("Конфигурация агента не найдена")
        return []

    with open(agent_config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    priority_keywords = config.get("priority_keywords", [])

    priority_files = []

    # Проверяем директории с отчетами и логами
    for dir_name in ["reports", "logs"]:
        dir_path = repo_root / dir_name

        if not dir_path.exists():
            continue

        for file_path in dir_path.iterdir():
            if file_path.is_file():
                # Проверяем имя файла на наличие ключевых слов
                file_name_lower = file_path.name.lower()

                for keyword in priority_keywords:
                    if keyword.lower() in file_name_lower:
                        priority_files.append({
                            "file": str(file_path),
                            "keyword": keyword,
                            "timestamp": datetime.now().isoformat(),
                            "type": dir_name
                        })

                # Проверяем содержимое файла на наличие ключевых слов
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()

                        for keyword in priority_keywords:
                            if keyword.lower() in content:
                                priority_files.append({
                                    "file": str(file_path),
                                    "keyword": keyword,
                                    "timestamp": datetime.now().isoformat(),
                                    "type": dir_name,
                                    "in_content": True
                                })
                except:
                    # Если не удалось прочитать файл, пропускаем
                    continue

    return priority_files


def create_notification_summary(priority_files):
    """
    Создает сводку уведомлений о приоритетных файлах
    """
    if not priority_files:
        print("Нет приоритетных файлов для обработки")
        return

    summary_path = repo_root / "notifications" / f"priority_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.parent.mkdir(exist_ok=True)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_priority_files": len(priority_files),
        "files": priority_files
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Создана сводка уведомлений: {summary_path}")
    print(f"Найдено приоритетных файлов: {len(priority_files)}")

    for pf in priority_files:
        print(f"  - {pf['file']} ({pf['keyword']})")


if __name__ == "__main__":
    priority_files = check_priority_files()
    create_notification_summary(priority_files)
'''

    notification_path = repo_root / "scripts" / "check_priority_notifications.py"
    with open(notification_path, "w", encoding="utf-8") as f:
        f.write(notification_script)

    print(f"Создана система уведомлений: {notification_path}")
    return str(notification_path)


if __name__ == "__main__":
    print("Запуск скрипта обновления конфигурации агента...")
    print("=" * 60)

    # Обновляем существующие конфиги
    updated_configs = update_agent_config()

    # Создаем новую конфигурацию для менеджера файлов
    file_manager_config = create_agent_file_manager_config()

    # Создаем систему уведомлений
    notification_system = create_priority_notification_system()

    print(f"\nОбновлено конфигурационных файлов: {len(updated_configs)}")
    print("Создано новых конфигурационных файлов: 2")
    print("Создано новых скриптов: 1")

    print("\nНовые функции:")
    print("- Агент теперь знает, где искать логи и отчеты")
    print("- Добавлена система приоритетов для файлов")
    print("- Создана система уведомлений о критичных файлах")
    print("- Автоматическая проверка наличия важных файлов")
