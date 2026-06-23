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
print(f"Found {len(py_files)} Python files")

bad_files = []
for f in py_files:
    try:
        with open(f, encoding="utf-8") as file:
            content = file.read()
        compile(content, f, "exec")
    except SyntaxError as e:
        bad_files.append((f, str(e)))
        print(f"  BAD: {f} - {e}")

print(f"\nBad files: {len(bad_files)}")
for f, err in bad_files:
    print(f"  {f}: {err}")
