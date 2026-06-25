#!/usr/bin/env python3
"""Проверка уязвимостей зависимостей"""

import json
from pathlib import Path

ROOT = Path(r"C:\repo")
VULN_FILE = ROOT / "vulnerabilities.json"

with open(VULN_FILE, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

deps = data.get("dependencies", [])
vulnerable = [d for d in deps if d.get("vulns")]

print(f"Found {len(vulnerable)} packages with vulnerabilities:\n")

for p in vulnerable:
    print(f"📦 {p['name']}=={p['version']}")
    for vuln in p["vulns"]:
        print(f"   ❌ {vuln['id']}: {vuln['description'][:100]}...")
        if vuln.get("fix_versions"):
            print(f"      ➕ Fix: {', '.join(vuln['fix_versions'])}")
    print()

print("\n" + "=" * 60)
print("Рекомендации:")
print("=" * 60)
print("1. Обновить критические уязвимости (aiohttp, cryptography, chromadb)")
print("2. Запустить pip install --upgrade <package>")
print("3. Обновить requirements.txt")
print("4. Перезапустить pip-audit для проверки")
