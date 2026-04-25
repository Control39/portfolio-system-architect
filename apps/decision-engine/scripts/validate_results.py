#!/usr/bin/env python3
"""Проверка корректности конвертации файлов в UTF-8.
Валидирует, что все файлы действительно в UTF-8 и читаются без ошибок.
"""
import json
import logging
from pathlib import Path

import chardet


def setup_logging() -> None:
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "validation.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

def is_valid_utf8_file(file_path: Path) -> dict:
    """Проверка, является ли файл корректным UTF-8"""
    result = {
        "path": str(file_path.relative_to(Path().resolve())),
        "is_utf8": False,
        "readable": False,
        "has_mojibake": False,
        "encoding_detection": None,
        "error": None,
    }

    try:
        # Попытка прочитать как UTF-8
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            result["readable"] = True

        # Проверка на корректность UTF-8
        try:
            file_path.read_bytes().decode("utf-8")
            result["is_utf8"] = True
        except UnicodeDecodeError:
            result["is_utf8"] = False

        # Проверка на "кракозябры" (mojibake)
        # Ищем распространенные признаки неправильной кодировки
        mojibake_patterns = [
            "�",  # REPLACEMENT CHARACTER
            "Ñ\n",
            "Ð\n",
            "Å\n",
            "Ã\n",
            "Â\n",
            "Ä\n",
            "Æ\n",
            "Ç\n",
            "È\n",
            "É\n",
            "Ë\n",
            "Ì\n",
            "Ï\n",
            "Î\n",
            "Ö\n",
            "Ô\n",
            "Õ\n",
            "×\n",
            "Ø\n",
            "Ù\n",
            "Ü\n",
            "Û\n",
            "Ý\n",
            "Þ\n",
            "ß\n",
            "à\n",
            "á\n",
            "â\n",
            "ã\n",
            "ä\n",
            "å\n",
            "æ\n",
            "ç\n",
            "è\n",
            "é\n",
            "ê\n",
            "ë\n",
            "ì\n",
            "í\n",
            "î\n",
            "ï\n",
            "ð\n",
            "ñ\n",
            "ò\n",
            "ó\n",
            "ô\n",
            "õ\n",
            "ö\n",
            "÷\n",
            "ø\n",
            "ù\n",
            "ú\n",
            "û\n",
            "ü\n",
            "ý\n",
            "þ\n",
            "ÿ\n",
            "—\n",
            "–\n",
            "“\n",
            "”\n",
            "„\n",
            "…\n",
            "†\n",
            "‡\n",
            "‰\n",
            "‹\n",
            "›\n",
            "€\n",
            "\u20ac\n",  # €
            "\u201c\n",  # "
            "\u201d\n",  # "
            "\u2018\n",  # '
            "\u2019\n",  # '
            "\u2013\n",  # --
            "\u2014\n",  # ---
            "™\n",  # ™
            "©\n",  # ©
            "®\n",  # ®
            "±\n",  # ±
            "²\n",  # ²
            "³\n",  # ³
            "µ\n",  # µ
            "¶\n",  # ¶
            "·\n",  # ·
            "¸\n",  # ¸
            "¹\n",  # ¹
            "º\n",  # º
            "¼\n",  # ¼
            "½\n",  # ½
            "¾\n",  # ¾
            "Ä\n",
            "Ö\n",
            "Ü\n",
            "ä\n",
            "ö\n",
            "ü\n",
            "ß\n",
            "ñ\n",
            "Ñ\n",
            "Ç\n",
            "ç\n",
            "Š\n",
            "š\n",
            "Ž\n",
            "ž\n",
            "À\n",
            "Á\n",
            "Â\n",
            "Ã\n",
            "Ä\n",
            "Å\n",
            "Æ\n",
            "È\n",
            "É\n",
            "Ê\n",
            "Ë\n",
            "Ì\n",
            "Í\n",
            "Î\n",
            "Ï\n",
            "Ð\n",
            "Ñ\n",
            "Ò\n",
            "Ó\n",
            "Ô\n",
            "Õ\n",
            "Ö\n",
            "×\n",
            "Ø\n",
            "Ù\n",
            "Ú\n",
            "Û\n",
            "Ü\n",
            "Ý\n",
            "Þ\n",
            "ß\n",
            "à\n",
            "á\n",
            "â\n",
            "ã\n",
            "ä\n",
            "å\n",
            "æ\n",
            "ç\n",
            "è\n",
            "é\n",
            "ê\n",
            "ë\n",
            "ì\n",
            "í\n",
            "î\n",
            "ï\n",
            "ð\n",
            "ñ\n",
            "ò\n",
            "ó\n",
            "ô\n",
            "õ\n",
            "ö\n",
            "÷\n",
            "ø\n",
            "ù\n",
            "ú\n",
            "û\n",
            "ü\n",
            "ý\n",
            "þ\n",
            "ÿ\n",
        ]

        result["has_mojibake"] = any(pattern in content for pattern in mojibake_patterns)

        # Проверка детектирования кодировки
        detection = chardet.detect(content.encode("utf-8", errors="ignore"))
        result["encoding_detection"] = {
            "encoding": detection["encoding"],
            "confidence": detection["confidence"],
        }

    except Exception as e:
        result["error"] = str(e)

    return result

def should_validate_file(file_path: Path) -> bool:
    """Определяет, нужно ли проверять файл"""
    text_extensions = {
        ".txt", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv",
        ".md", ".rst", ".ini", ".cfg", ".conf", ".yml", ".yaml",
        ".sh", ".bat", ".ps1", ".sql", ".log", ".properties",
    }

    ignore_dirs = {"node_modules", "__pycache__", ".git", ".vscode", "logs", "backups"}

    if file_path.suffix.lower() not in text_extensions:
        return False

    for part in file_path.parts:
        if part in ignore_dirs:
            return False

    return True

def validate_all(start_path: str = ".") -> dict:
    """Валидация всех файлов после конвертации"""
    start_path = Path(start_path).resolve()
    results = []
    summary = {
        "total_files": 0,
        "validated_files": 0,
        "valid_utf8": 0,
        "readable": 0,
        "has_mojibake": 0,
        "errors": 0,
    }

    logging.info(f"Начало валидации UTF-8: {start_path}")

    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    for file_path in start_path.rglob("*"):
        if file_path.is_file() and should_validate_file(file_path):
            summary["total_files"] += 1

            file_result = is_valid_utf8_file(file_path)

            # Обновляем статистику
            if file_result["error"]:
                summary["errors"] += 1
            else:
                summary["validated_files"] += 1
                if file_result["is_utf8"]:
                    summary["valid_utf8"] += 1
                if file_result["readable"]:
                    summary["readable"] += 1
                if file_result["has_mojibake"]:
                    summary["has_mojibake"] += 1

            results.append(file_result)

    # Финальный отчет
    final_result = {
        "summary": summary,
        "files": results,
        "timestamp": str(Path(__file__).stat().st_mtime),
    }

    # Сохраняем результаты
    output_file = log_dir / "validation_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    logging.info(f"Валидация завершена. Результаты сохранены в {output_file}")
    logging.info(f"Всего файлов: {summary['total_files']}, Ошибок: {summary['errors']}, Кракозябр: {summary['has_mojibake']}")

    return final_result

def print_summary(results: dict) -> None:
    """Вывод краткого отчета в консоль"""
    summary = results["summary"]
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ВАЛИДАЦИИ UTF-8")
    print("="*60)
    print(f"Всего файлов: {summary['total_files']}")
    print(f"Проверено: {summary['validated_files']}")
    print(f"Корректный UTF-8: {summary['valid_utf8']}")
    print(f"Читаемые: {summary['readable']}")
    print(f"С кракозябрами: {summary['has_mojibake']}")
    print(f"Ошибок: {summary['errors']}")

    # Показываем файлы с проблемами
    if summary["has_mojibake"] > 0:
        print("\nФайлы с кракозябрами (mojibake):")
        for file_result in results["files"]:
            if file_result["has_mojibake"]:
                print(f"  {file_result['path']}")

    if summary["errors"] > 0:
        print("\nФайлы с ошибками:")
        for file_result in results["files"]:
            if file_result["error"]:
                print(f"  {file_result['path']}: {file_result['error']}")

    print("="*60)

def main():
    """Основная функция"""
    setup_logging()

    try:
        results = validate_all()
        print_summary(results)

        # Возвращаем код ошибки, если были проблемы
        if results["summary"]["errors"] > 0 or results["summary"]["has_mojibake"] > 0:
            exit(1)

    except Exception as e:
        logging.exception(f"Ошибка при выполнении валидации: {e}")
        exit(1)

if __name__ == "__main__":
    main()


