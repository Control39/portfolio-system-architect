#!/usr/bin/env python3
"""
Обновление зависимостей для исправления уязвимостей
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(r"C:\repo")
VULN_FILE = ROOT / "vulnerabilities.json"
REQUIREMENTS_FILE = ROOT / "requirements.txt"

# Загрузить уязвимости
with open(VULN_FILE, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Собрать пакеты для обновления
deps_to_update = {}
for dep in data.get("dependencies", []):
    name = dep.get("name")
    version = dep.get("version")
    vulns = dep.get("vulns", [])
    
    if vulns:
        fix_versions = set()
        for vuln in vulns:
            fix_versions.update(vuln.get("fix_versions", []))
        
        if fix_versions:
            deps_to_update[name] = {
                "current": version,
                "fix_versions": sorted(fix_versions, key=lambda x: [int(i) for i in x.split(".")])
            }

print("="*60)
print("📦 Обновление зависимостей для исправления уязвимостей")
print("="*60)

print(f"\nНайдено {len(deps_to_update)} пакетов с уязвимостями:\n")

# Сортировка по критичности (примерная)
priority_packages = {
    "aiohttp": 1,
    "cryptography": 2,
    "dulwich": 3,
    "langchain": 4,
    "tornado": 5,
    "pyjwt": 6,
    "python-multipart": 7,
    "starlette": 8,
    "torch": 9,
    "pip": 10,
    "pydantic-settings": 11,
    "langsmith": 12,
    "msgpack": 13,
}

sorted_deps = sorted(
    deps_to_update.items(),
    key=lambda x: priority_packages.get(x[0], 999)
)

for name, info in sorted_deps:
    current = info["current"]
    best_fix = info["fix_versions"][-1]  # Самая новая версия
    print(f"  {name}: {current} → {best_fix} ({len(info['fix_versions'])} версий доступно)")

print("\n" + "="*60)
print("🚀 Запуск обновлений...")
print("="*60)

# Обновление пакетов
for name, info in sorted_deps:
    best_fix = info["fix_versions"][-1]
    version_spec = f"{name}=={best_fix}"
    
    print(f"\n📦 Обновление {name}=={best_fix}...")
    try:
        result = subprocess.run(
            ["python", "-m", "pip", "install", "--upgrade", version_spec],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=ROOT
        )
        
        if result.returncode == 0:
            print(f"   ✅ {name} обновлён до {best_fix}")
        else:
            print(f"   ❌ Ошибка обновления {name}: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

print("\n" + "="*60)
print("📝 Обновление requirements.txt...")
print("="*60)

# Обновить requirements.txt
try:
    result = subprocess.run(
        ["python", "-m", "pip", "freeze", "--all"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=ROOT
    )
    
    if result.returncode == 0:
        with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        print(f"✅ requirements.txt обновлён: {REQUIREMENTS_FILE}")
    else:
        print(f"❌ Ошибка обновления requirements.txt: {result.stderr[:200]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*60)
print("🔍 Проверка уязвимостей после обновления...")
print("="*60)

# Перепроверить уязвимости
try:
    result = subprocess.run(
        ["python", "-m", "pip_audit", "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=ROOT
    )
    
    if result.returncode == 0:
        new_data = json.loads(result.stdout)
        new_vulnerable = [d for d in new_data.get("dependencies", []) if d.get("vulns")]
        
        print(f"\nПосле обновления найдено {len(new_vulnerable)} пакетов с уязвимостями")
        
        if new_vulnerable:
            print("\nОставшиеся уязвимости:")
            for dep in new_vulnerable:
                print(f"  - {dep['name']}: {len(dep['vulns'])} уязвимостей")
        else:
            print("\n✅ Все уязвимости исправлены!")
    else:
        print(f"❌ Ошибка проверки: {result.stderr[:200]}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*60)
print("✅ Скрипт завершён!")
print("="*60)
