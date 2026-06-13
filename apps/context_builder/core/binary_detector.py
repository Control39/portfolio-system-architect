from pathlib import Path


def is_binary_file(file_path: Path) -> bool:
    """
    Определяет, является ли файл бинарным.
    Использует несколько методов для надёжности.
    """
    # Метод 1: пробуем прочитать как текст с разных кодировках
    encodings_to_try = ["utf-8", "cp1251", "latin-1"]

    for encoding in encodings_to_try:
        try:
            with open(file_path, encoding=encoding) as f:
                f.read(1024)
            # Если успешно прочитали хоть одну кодировку — вероятно, текст
            return False
        except (OSError, UnicodeDecodeError):
            continue

    # Метод 2: проверка на нулевые байты (признак бинарника)
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except Exception:
        pass

    # Метод 3: проверка на распространённые бинарные сигнатуры
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            # PDF, PNG, JPEG, ZIP, ELF, etc.
            binary_signatures = [
                b"%PDF",
                b"\x89PNG",
                b"\xff\xd8",
                b"PK\x03\x04",
                b"\x7fELF",
                b"MZ",
                b"GIF8",
            ]
            if any(header.startswith(sig) for sig in binary_signatures):
                return True
    except Exception:
        pass

    # Если ничего не сработало — считаем бинарным (консервативно)
    return True
