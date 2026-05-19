import subprocess
import sys
import os

os.chdir(r"C:\repo\apps\ai_config_manager")

print("=== Установка пакета в development режиме ===")
result = subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n=== Запуск тестов ===")
result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Сохраняем результат в файл
with open(r"C:\repo\test_results.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\nSTDERR:\n")
        f.write(result.stderr)

print(f"\n=== Результат сохранён в test_results.txt (Exit code: {result.returncode}) ===")
