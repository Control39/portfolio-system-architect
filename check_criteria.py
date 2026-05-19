#!/usr/bin/env python3
"""Диагностика критериев README"""

import re

content = open('apps/it_compass/README.md', encoding='utf-8').read()

patterns = {
    'title': r'^#\s+.+',
    'purpose': r'(##\s*Назначение|##\s*Purpose|###\s*Что делает|##\s*Overview|##\s*Описание|###\s*Цель)',
    'features': r'(##\s*Ключевые возможности|##\s*Features|##\s*Основные возможности|Ключевые возможности|##\s*Функции|\[\s*x\s*\])',
    'api': r'(/api/|##\s*API|###\s*Endpoints|endpoints)',
    'dependencies': r'(requirements|Dependencies|dependencies|pip install|##\s*Установка|###\s*Зависимости)',
    'deployment': r'(docker|Docker|compose|localhost:\d+|##\s*Запуск)',
    'contributing': r'(Contributing|contributing|Вклад|CONTRIBUTING)',
}

print("Детальная проверка критериев:\n")
for name, pattern in patterns.items():
    match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
    status = "✓" if match else "✗"
    found = match.group()[:50] if match else "НЕ НАЙДЕНО"
    print(f"{name:<15} {status} - {found}")
