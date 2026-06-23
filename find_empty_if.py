#!/usr/bin/env python3
"""
Скрипт для поиска всех файлов с if без тела
"""

from pathlib import Path


def find_files_with_empty_if(repo_root: Path):
    """Найти все файлы с if без тела"""
    bad_files = []

    for py_file in repo_root.rglob("*.py"):
        # Исключаем виртуальные окружения и кэш
        if any(part in str(py_file) for part in [".venv", "__pycache__", ".git", ".cache", "venv"]):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                lines = f.readlines()
        except:
            continue

        for i, line in enumerate(lines):
            # Ищем if без тела (строка заканчивается на : и следующая строка не indented)
            stripped = line.rstrip()
            if stripped.endswith(":") and not stripped.endswith("##"):  # не комментарий
                # Проверяем следующую строку
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_stripped = next_line.lstrip()
                    # Если следующая строка не пустая и не commen
                    if next_stripped and not next_stripped.startswith("#"):
                        # Проверяем уровень отступа
                        current_indent = len(line) - len(line.lstrip())
                        next_indent = len(next_line) - len(next_line.lstrip())

                        # Если следующая строка имеет тот же или меньший отступ - это ошибка
                        if next_indent <= current_indent:
                            bad_files.append(
                                {
                                    "file": str(py_file),
                                    "line": i + 1,
                                    "content": stripped,
                                    "next_line": i + 2,
                                    "next_content": next_stripped.strip()[:50],
                                }
                            )
                            break  # только одна ошибка на файл
        # Продолжить, но не слишком часто
        if len(bad_files) >= 50:
            break

    return bad_files


if __name__ == "__main__":
    repo_root = Path("C:/repo")
    bad = find_files_with_empty_if(repo_root)
    print(f"Найдено {len(bad)} файлов с if без тела")
    for item in bad[:20]:
        print(f"\n{item['file']}:{item['line']}")
        print(f"  {item['content']}")
        print(f"  -> {item['next_content']}")
