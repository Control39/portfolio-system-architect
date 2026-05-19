#!/usr/bin/env python3
"""Детальная проверка it_compass README"""

import re

content = open('apps/it_compass/README.md', encoding='utf-8').read()

patterns = {
    'title': r'^#\s+.+',
    'purpose': r'(##\s*[\u2700-\u27BF\s]*Назначение|##\s*Назначение)',
    'features': r'(##\s*Ключевые возможности|##\s*Features|\[\s*x\s*\])',
    'api': r'(/api/|##\s*API|###\s*Endpoints)',
    'dependencies': r'(requirements|Dependencies|pip install|##\s*Зависимости)',
    'deployment': r'(docker|Docker|compose|localhost:\d+|##\s*Запуск)',
    'contributing': r'(Contributing|contributing|Вклад|CONTRIBUTING)',
}

print("Детальная проверка it_compass README:\n")
for name, pattern in patterns.items():
    matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
    if matches:
        print(f"✓ {name:<15} НАЙДЕНО ({len(matches)} раз)")
        for m in matches[:2]:
            print(f"    '{m.group().strip()}'")
    else:
        print(f"✗ {name:<15} НЕ НАЙДЕНО")

# Проверю конкретный заголовок
print("\n\nСоседние строки после '## 🎯':")
lines = content.split('\n')
for i, line in enumerate(lines):
    if '##' in line and '🎯' in line:
        print(f"  Строка {i}: {line}")
        if i+1 < len(lines):
            print(f"  Строка {i+1}: {lines[i+1]}")
