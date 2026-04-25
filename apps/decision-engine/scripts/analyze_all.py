#!/usr/bin/env python3
"""Анализ всех текстовых файлов в проекте на предмет кодировки.
Поддерживает кириллицу в путях и названиях файлов.
"""
import json
import logging
import os
from pathlib import Path

import chardet


def setup_logging() -> None:
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/encoding_analysis.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

def detect_encoding(file_path: Path) -> dict[str, str]:
    """Определение кодировки файла с помощью chardet"""
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()

        if len(raw_data) == 0:
            return {"encoding": "empty", "confidence": "1.0", "error": None}

        result = chardet.detect(raw_data)
        encoding = result["encoding"]
        confidence = result["confidence"]

        # Нормализация названий кодировок
        if encoding:
            encoding = encoding.lower().replace("-", "_")

        return {
            "encoding": encoding,
            "confidence": confidence,
            "error": None,
        }

    except Exception as e:
        return {
            "encoding": None,
            "confidence": None,
            "error": str(e),
        }

def analyze_file(file_path: Path, relative_path: Path) -> dict:
    """Анализ одного файла"""
    logging.info(f"Анализ файла: {relative_path}")

    result = {
        "path": str(relative_path),
        "size": os.path.getsize(file_path),
        "analysis": detect_encoding(file_path),
    }

    return result

def should_process_file(file_path: Path) -> bool:
    """Определяет, нужно ли обрабатывать файл"""
    text_extensions = {
        ".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv",
        ".md", ".rst", ".ini", ".cfg", ".conf", ".yml", ".yaml",
        ".sh", ".bat", ".ps1", ".sql", ".log", ".properties",
    }

    ignore_dirs = {"node_modules", "__pycache__", ".git", ".vscode", "logs", "backups"}

    # Проверяем расширение
    if file_path.suffix.lower() not in text_extensions:
        return False

    # Проверяем директории
    for part in file_path.parts:
        if part in ignore_dirs:
            return False

    return True

def analyze_all(start_path: str = ".") -> dict:
    """Анализ всех текстовых файлов в указанной директории"""
    start_path = Path(start_path).resolve()
    results = []
    summary = {
        "total_files": 0,
        "processed_files": 0,
        "errors": 0,
        "encoding_distribution": {},
    }

    logging.info(f"Начало анализа кодировок в: {start_path}")

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    for file_path in start_path.rglob("*"):
        if file_path.is_file() and should_process_file(file_path):
            summary["total_files"] += 1

            relative_path = file_path.relative_to(start_path)
            file_result = analyze_file(file_path, relative_path)

            # Обновляем статистику
            if file_result["analysis"]["error"]:
                summary["errors"] += 1
            else:
                encoding = file_result["analysis"]["encoding"]
                if encoding:
                    summary["encoding_distribution"][encoding] = summary["encoding_distribution"].get(encoding, 0) + 1

            results.append(file_result)
            summary["processed_files"] += 1

    # Финальный отчет
    final_result = {
        "summary": summary,
        "files": results,
        "timestamp": str(Path(__file__).stat().st_mtime),
    }

    # Сохраняем результаты
    output_file = log_dir / "encoding_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    logging.info(f"Анализ завершен. Результаты сохранены в {output_file}")
    logging.info(f"Всего файлов: {summary['total_files']}, Ошибок: {summary['errors']}")

    return final_result

def print_summary(results: dict) -> None:
    """Вывод краткого отчета в консоль"""
    summary = results["summary"]
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА КОДИРОВОК")
    print("="*60)
    print(f"Всего файлов найдено: {summary['total_files']}")
    print(f"Обработано файлов: {summary['processed_files']}")
    print(f"Ошибок при анализе: {summary['errors']}")

    print("\nРаспределение кодировок:")
    for encoding, count in sorted(summary["encoding_distribution"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {encoding}: {count} файлов")

    # Показываем файлы с проблемами
    if summary["errors"] > 0:
        print("\nФайлы с ошибками:")
        for file_result in results["files"]:
            if file_result["analysis"]["error"]:
                print(f"  {file_result['path']}: {file_result['analysis']['error']}")

    print("="*60)

def main():
    """Основная функция"""
    setup_logging()

    try:
        results = analyze_all()
        print_summary(results)

        # Возвращаем код ошибки, если были проблемы
        if results["summary"]["errors"] > 0:
            exit(1)

    except Exception as e:
        logging.exception(f"Ошибка при выполнении анализа: {e}")
        exit(1)

if __name__ == "__main__":
    main()

