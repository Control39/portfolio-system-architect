#!/usr/bin/env python3
import os
import subprocess

# Получаем все измененные файлы
result = subprocess.run(["git", "diff", "HEAD", "--name-only"], capture_output=True, text=True)
modified = result.stdout.strip().split("\n") if result.stdout.strip() else []

# Получаем новые файлы
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
for line in result.stdout.strip().split("\n"):
    if line.startswith("?? ") or line.startswith("A  "):
        fname = line[3:].strip()
        if fname and fname not in modified:
            modified.append(fname)

py_files = [f for f in modified if f.endswith(".py") and os.path.exists(f)]

# Проверяем файлы построчно
bad_files = []
for f in py_files:
    try:
        with open(f, encoding="utf-8") as file:
            content = file.read()
        compile(content, f, "exec")
    except SyntaxError as e:
        bad_files.append(
            (f, str(e), e.lineno, content.split("\n")[e.lineno - 1] if e.lineno <= len(content.split("\n")) else "N/A")
        )

print(f"Bad files: {len(bad_files)}")
for f, err, lineno, line in bad_files:
    print(f"\n{f}:")
    print(f"  Line {lineno}: {err}")
    print(f"  Content: {repr(line)}")

    # Показать контекст
    lines = content.split("\n")
    start = max(0, lineno - 4)
    end = min(len(lines), lineno + 2)
    print("  Context:")
    for i in range(start, end):
        marker = ">>>" if i == lineno - 1 else "   "
        print(f"    {marker} {i+1}: {repr(lines[i])}")
