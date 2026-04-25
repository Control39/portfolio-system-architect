#!/usr/bin/env python3
"""Подготовка коммитов для Git после конвертации кодировок.
Создает корректные коммиты, сохраняя историю изменений.
"""
import datetime
import json
import logging
import subprocess
from pathlib import Path


def setup_logging() -> None:
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "git_commit.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

def is_git_repository() -> bool:
    """Проверка, находится ли в Git репозитории"""
    try:
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                              capture_output=True, text=True, cwd=Path().resolve())
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception as e:
        logging.exception(f"Ошибка при проверке Git репозитория: {e}")
        return False

def get_git_status() -> dict:
    """Получение текущего статуса Git"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True, cwd=Path().resolve())

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

            status = {
                "modified": [],
                "untracked": [],
                "deleted": [],
                "renamed": [],
            }

            for line in lines:
                if not line:
                    continue

                status_code = line[:2].strip()
                file_path = line[3:].strip()

                if status_code == "M":
                    status["modified"].append(file_path)
                elif status_code == "??":
                    status["untracked"].append(file_path)
                elif status_code == "D":
                    status["deleted"].append(file_path)
                elif status_code == "R":
                    status["renamed"].append(file_path)

            return status

    except Exception as e:
        logging.exception(f"Ошибка при получении статуса Git: {e}")

    return { "modified": [], "untracked": [], "deleted": [], "renamed": [] }

def create_commit(commit_message: str, files: list[str] = None) -> bool:
    """Создание коммита в Git"""
    try:
        # Добавляем файлы в индекс
        if files:
            result = subprocess.run(["git", "add"] + files,
                                  capture_output=True, text=True, cwd=Path().resolve())
        else:
            result = subprocess.run(["git", "add", "--all"],
                                  capture_output=True, text=True, cwd=Path().resolve())

        if result.returncode != 0:
            logging.error(f"Ошибка при добавлении файлов в индекс: {result.stderr}")
            return False

        # Создаем коммит
        result = subprocess.run(["git", "commit", "-m", commit_message],
                              capture_output=True, text=True, cwd=Path().resolve())

        if result.returncode == 0:
            logging.info(f"Коммит создан: {commit_message}")
            return True
        logging.error(f"Ошибка при создании коммита: {result.stderr}")
        return False

    except Exception as e:
        logging.exception(f"Ошибка при создании коммита: {e}")
        return False

def create_encoding_commit() -> dict:
    """Создание коммита с изменениями кодировок"""
    result = {
        "success": False,
        "commit_created": False,
        "files_committed": [],
        "message": None,
        "error": None,
    }

    try:
        if not is_git_repository():
            result["error"] = "Не найден Git репозиторий"
            logging.error(result["error"])
            return result

        # Получаем статус изменений
        status = get_git_status()
        all_changed_files = status["modified"] + status["untracked"]

        if not all_changed_files:
            result["success"] = True
            result["message"] = "Нет изменений для коммита"
            logging.info(result["message"])
            return result

        # Фильтруем файлы для коммита (только текстовые)
        text_extensions = {
            ".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv",
            ".md", ".rst", ".ini", ".cfg", ".conf", ".yml", ".yaml",
            ".sh", ".bat", ".ps1", ".sql", ".log", ".properties",
        }

        files_to_commit = []
        for file_path in all_changed_files:
            path_obj = Path(file_path)
            if path_obj.suffix.lower() in text_extensions:
                files_to_commit.append(file_path)

        if not files_to_commit:
            result["success"] = True
            result["message"] = "Нет текстовых файлов для коммита"
            logging.info(result["message"])
            return result

        # Создаем сообщение коммита
        commit_message = "[encoding] Convert files to UTF-8 encoding"

        # Добавляем детали в сообщение, если файлов немного
        if len(files_to_commit) <= 10:
            commit_message += "\n\nFiles updated:\n" + "\n".join([f"- {f}" for f in files_to_commit])
        else:
            commit_message += f"\n\nUpdated {len(files_to_commit)} files to UTF-8 encoding."

        # Создаем коммит
        success = create_commit(commit_message, files_to_commit)

        result["success"] = success
        result["commit_created"] = success
        result["files_committed"] = files_to_commit

        if success:
            result["message"] = f"Коммит успешно создан с {len(files_to_commit)} файлами"
        else:
            result["error"] = "Не удалось создать коммит"

    except Exception as e:
        result["error"] = str(e)
        logging.exception(f"Неожиданная ошибка: {e}")

    return result

def create_backup_commit() -> dict:
    """Создание коммита с резервными копиями"""
    result = {
        "success": False,
        "commit_created": False,
        "files_committed": [],
        "message": None,
        "error": None,
    }

    try:
        if not is_git_repository():
            result["error"] = "Не найден Git репозиторий"
            return result

        # Проверяем наличие директории backups
        backup_dir = Path("backups")
        if not backup_dir.exists():
            result["success"] = True
            result["message"] = "Нет директории backups для коммита"
            return result

        # Находим последнюю резервную копию
        backup_dirs = [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith("pre_utf8_conversion_")]
        if not backup_dirs:
            result["success"] = True
            result["message"] = "Нет резервных копий для коммита"
            return result

        # Сортируем по времени создания и берем последнюю
        latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)

        # Добавляем резервную копию в Git
        result_add = subprocess.run(["git", "add", str(latest_backup)],
                                  capture_output=True, text=True, cwd=Path().resolve())

        if result_add.returncode != 0:
            result["error"] = f"Ошибка при добавлении резервной копии: {result_add.stderr}"
            return result

        # Создаем коммит
        commit_message = "[backup] Add backup before UTF-8 conversion"
        result_commit = subprocess.run(["git", "commit", "-m", commit_message],
                                     capture_output=True, text=True, cwd=Path().resolve())

        if result_commit.returncode == 0:
            result["success"] = True
            result["commit_created"] = True
            result["files_committed"] = [str(latest_backup)]
            result["message"] = f"Коммит резервной копии создан: {latest_backup}"
        else:
            result["error"] = f"Ошибка при создании коммита резервной копии: {result_commit.stderr}"

    except Exception as e:
        result["error"] = str(e)

    return result

def fix_git_history() -> dict:
    """Основная функция для подготовки коммитов в Git"""
    logging.info("Начало подготовки коммитов для Git")

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    results = {
        "backup_commit": None,
        "encoding_commit": None,
        "success": False,
        "timestamp": str(datetime.datetime.now()),
    }

    try:
        # Сначала создаем коммит с резервной копией (если нужно)
        results["backup_commit"] = create_backup_commit()

        # Затем создаем коммит с изменениями кодировок
        results["encoding_commit"] = create_encoding_commit()

        # Определяем общий успех
        results["success"] = results["encoding_commit"]["success"]

        # Сохраняем результаты
        output_file = log_dir / "git_commit_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logging.info(f"Подготовка коммитов завершена. Результаты сохранены в {output_file}")

    except Exception as e:
        logging.exception(f"Ошибка при подготовке коммитов: {e}")
        results["success"] = False

    return results

def print_summary(results: dict) -> None:
    """Вывод краткого отчета"""
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ПОДГОТОВКИ КОММИТОВ GIT")
    print("="*60)

    if results["backup_commit"]:
        print("КОММИТ РЕЗЕРВНОЙ КОПИИ:")
        if results["backup_commit"]["commit_created"]:
            print("  Статус: УСПЕШНО\n")

