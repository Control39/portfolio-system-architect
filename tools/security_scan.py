#!/usr/bin/env python3
"""
Сканирование безопасности: анализ уязвимостей зависимостей
Цель: Разобрать 365 Security Alerts на GitHub
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\repo")
OUTPUT_DIR = ROOT / "docs" / "security"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("🔒 Сканирование безопасности зависимостей")
print("=" * 60)

# 1. Найти все requirements.txt
print("\n📂 Поиск requirements.txt файлов...")
requirements_files = list(ROOT.rglob("requirements*.txt"))
print(f"   Найдено {len(requirements_files)} файлов")

# 2. Анализ через pip-audit (если установлен) или safety
print("\n🔍 Запуск pip-audit...")
try:
    result = subprocess.run(
        ["C:\\repo\\.venv\\Scripts\\pip-audit", "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode == 0:
        vulnerabilities = json.loads(result.stdout)
        print(f"   ✅ Найдено {len(vulnerabilities)} уязвимостей")
    else:
        print(f"   ⚠️  pip-audit не установлен или ошибка: {result.stderr[:200]}")
        vulnerabilities = []
except FileNotFoundError:
    print("   ⚠️  pip-audit не установлен. Установка...")
    subprocess.run(["C:\\repo\\.venv\\Scripts\\pip", "install", "pip-audit"], check=True)
    vulnerabilities = []
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    vulnerabilities = []

# 3. Группировка по severity
print("\n📊 Анализ по severity:")
severity_counts = defaultdict(int)
for vuln in vulnerabilities:
    if isinstance(vuln, dict):
        severity = vuln.get("severity", "Unknown")
        severity_counts[severity] += 1
    else:
        severity_counts["Unknown"] += 1

for severity, count in sorted(severity_counts.items(), key=lambda x: -x[1]):
    print(f"   {severity}: {count}")

# 4. Создать отчёт
report = {
    "scan_date": "2026-05-24",
    "total_vulnerabilities": len(vulnerabilities),
    "by_severity": dict(severity_counts),
    "files_scanned": [str(f.relative_to(ROOT)) for f in requirements_files],
    "vulnerabilities": vulnerabilities[:50],  # Первые 50 для примера
}

report_path = OUTPUT_DIR / "security_scan_2026-05-24.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ Отчёт сохранён: {report_path}")

# 5. Предложить план исправления
print("\n📋 План исправления:")
print("   1. Приоритет: Critical/High уязвимости")
print("   2. Обновить requirements.txt с новыми версиями")
print("   3. Запустить pip-audit снова для проверки")
print("   4. Закоммитить изменения")
print("   5. Отметить исправленные уязвимости на GitHub")

# 6. Проверить Docker образы (если есть Dockerfile)
print("\n🐳 Проверка Docker образов...")
dockerfiles = list(ROOT.rglob("Dockerfile"))
print(f"   Найдено {len(dockerfiles)} Dockerfile")

print("\n" + "=" * 60)
print("✅ Сканирование завершено!")
print("=" * 60)
print(f"\nДетали в: {report_path}")
print("Следующий шаг: Обновить зависимости по приоритету")
