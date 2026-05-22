#!/usr/bin/env python3
"""Проверка уязвимостей в Python зависимостях."""
import subprocess
import sys
import json

def check_python_vulnerabilities():
    """Проверка уязвимостей через pip-audit."""
    print("🔍 Проверка уязвимостей в requirements.txt...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip-audit', '--format', 'json', 'requirements.txt'],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if not data or 'vulnerabilities' not in data or not data['vulnerabilities']:
                print("✅ Уязвимостей не найдено!")
            else:
                print(f"⚠️ Найдено {len(data['vulnerabilities'])} уязвимостей:")
                for vuln in data['vulnerabilities']:
                    print(f"  - {vuln.get('package', 'unknown')}: {vuln.get('description', 'N/A')[:80]}...")
        else:
            print(f"❌ Ошибка проверки: {result.stderr}")
            
    except FileNotFoundError:
        print("⚠️ pip-audit не установлен. Установка...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pip-audit', '-q'])
        check_python_vulnerabilities()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_github_alerts():
    """Вывод ссылки на Dependabot алерты."""
    print("\n📋 Проверь Dependabot алерты вручную:")
    print("   https://github.com/Control39/portfolio-system-architect/security/dependabot")

if __name__ == '__main__':
    check_python_vulnerabilities()
    check_github_alerts()
