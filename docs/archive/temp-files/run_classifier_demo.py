"""
Демо-скрипт для запуска классификатора монорепозитория
"""

import subprocess  # nosec B404
import sys
from pathlib import Path


# Путь к проекту
project_root = Path(__file__).parent
script_path = project_root / "classify_v4.py"
output_file = project_root / "docs" / "reports" / "classifier-demo-output.txt"

# Запуск классификатора
print("🚀 Запуск классификатора...")
result = subprocess.run(  # nosec B603
    [sys.executable, str(script_path), "."],
    cwd=project_root,
    capture_output=True,
    text=True,
    encoding="utf-8",
)

# Сохранение вывода
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)

print(f"✅ Лог сохранён в: {output_file}")
print("\n--- Содержание лога ---\n")
print(result.stdout)
if result.stderr:
    print("\n--- STDERR ---\n")
    print(result.stderr)
