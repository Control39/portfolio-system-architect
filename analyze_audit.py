#!/usr/bin/env python3
"""Анализ результатов pip-audit."""
import json
import sys

def analyze_audit():
    try:
        with open('audit_results.json', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Обработка ошибок в выводе
        if 'ERROR' in content or 'error:' in content:
            print("❌ Ошибка при запуске pip-audit:")
            print(content)
            return
        
        # Пытаемся распарсить JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ Результат не в формате JSON, показываем сырой вывод:")
            print(content[:2000])
            return
        
        if not data or 'vulnerabilities' not in data:
            print("✅ Уязвимостей не найдено!")
            return
        
        vulnerabilities = data['vulnerabilities']
        if not vulnerabilities:
            print("✅ Уязвимостей не найдено!")
            return
        
        print(f"🚨 Найдено {len(vulnerabilities)} уязвимостей:\n")
        
        # Группировка по пакетам
        packages = {}
        for vuln in vulnerabilities:
            pkg = vuln.get('package', {}).get('name', 'unknown')
            if pkg not in packages:
                packages[pkg] = []
            packages[pkg].append(vuln)
        
        for pkg_name, pkg_vulns in packages.items():
            print(f"\n📦 {pkg_name} ({len(pkg_vulns)} уязвимостей):")
            for v in pkg_vulns:
                vuln_id = v.get('vulnerability', {}).get('id', 'N/A')
                severity = v.get('vulnerability', {}).get('severity', 'unknown')
                desc = v.get('vulnerability', {}).get('description', 'N/A')[:100]
                print(f"  [{severity.upper()}] {vuln_id}: {desc}...")
        
        print(f"\n💡 Рекомендация: Обновите уязвимые пакеты через:")
        print("   pip install --upgrade <package_name>")
        
    except FileNotFoundError:
        print("❌ Файл audit_results.json не найден. Запустите:")
        print("   .venv\\Scripts\\pip-audit requirements.txt > audit_results.json")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    analyze_audit()
