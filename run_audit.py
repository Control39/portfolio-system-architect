#!/usr/bin/env python3
"""Запуск pip-audit и анализ результатов."""
import subprocess
import sys
import json

def run_audit():
    print("🔍 Запуск pip-audit...")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pip-audit', 'pyproject.toml', '--format', 'json'],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0 and result.returncode != 1:
        print(f"❌ Ошибка запуска: {result.stderr}")
        return
    
    # Парсим вывод
    try:
        # pip-audit возвращает массив объектов
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("⚠️ Не JSON вывод, показываем сырой:")
        print(result.stdout[:1000])
        return
    
    if not data:
        print("✅ Уязвимостей не найдено!")
        return
    
    print(f"\n🚨 Найдено {len(data)} уязвимостей:\n")
    
    packages = {}
    for item in data:
        pkg = item.get('package', {}).get('name', 'unknown')
        if pkg not in packages:
            packages[pkg] = []
        packages[pkg].append(item)
    
    for pkg_name, pkg_vulns in packages.items():
        print(f"\n📦 {pkg_name} ({len(pkg_vulns)} уязвимостей):")
        for v in pkg_vulns:
            vuln_id = v.get('vulnerability', {}).get('id', 'N/A')
            severity = v.get('vulnerability', {}).get('severity', 'unknown')
            desc = v.get('vulnerability', {}).get('description', 'N/A')[:80]
            print(f"  [{severity.upper():7}] {vuln_id}: {desc}...")
    
    print(f"\n💡 Рекомендация:")
    print("   pip install --upgrade " + " ".join(packages.keys()))

if __name__ == '__main__':
    run_audit()