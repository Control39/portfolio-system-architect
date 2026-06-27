#!/usr/bin/env python3
"""fix_shell_scripts.py - Исправить shell скрипты для Windows/Linux совместимости"""

from pathlib import Path


def fix_shell_script(filepath: Path) -> None:
    """Исправить shell скрипт"""
    # Прочитать как бинарный
    content_bytes = filepath.read_bytes()

    # Убрать CR (\r)
    content_bytes = content_bytes.replace(b"\r\n", b"\n")
    content_bytes = content_bytes.replace(b"\r", b"\n")

    # Декодировать
    content = content_bytes.decode("utf-8")

    # Изменить shebang
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("#!/bin/bash"):
            lines[i] = "#!/usr/bin/env bash"
        elif line.startswith("#!/bin/sh"):
            lines[i] = "#!/usr/bin/env sh"
        elif line.startswith("cd /c/repo"):
            lines[i] = 'cd "$(dirname "$0")/.."'

    content = "\n".join(lines)

    # Сохранить
    filepath.write_text(content, encoding="utf-8")


def main():
    """Main entry point"""
    scripts_dir = Path("scripts")
    shell_scripts = list(scripts_dir.glob("*.sh"))

    for script in shell_scripts:
        fix_shell_script(script)
        print(f"✅ Исправлен: {script}")

    print(f"\nВсего исправлено: {len(shell_scripts)} скриптов")


if __name__ == "__main__":
    main()
