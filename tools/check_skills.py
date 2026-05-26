#!/usr/bin/env python3
"""Скрипт проверки перенесённых скиллов"""
from pathlib import Path

skills_dir = Path('.agents/skills')
missing = []

print("=" * 60)
print("🔍 ПРОВЕРКА ПЕРЕНЕСЁННЫХ СКИЛЛОВ")
print("=" * 60)

for skill_dir in sorted(skills_dir.iterdir()):
    if not skill_dir.is_dir():
        continue
    
    print(f"\n{skill_dir.name}/")
    
    # Проверка SKILL.md
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        print(f'  ✅ SKILL.md')
    else:
        print(f'  ❌ SKILL.md')
        missing.append(f'{skill_dir.name}/SKILL.md')
    
    # Поиск скриптов
    py_files = list(skill_dir.glob('*.py'))
    ps_files = list(skill_dir.glob('*.ps1'))
    
    if py_files:
        for f in py_files[:3]:  # Показать первые 3
            print(f'  ✅ {f.name}')
    else:
        print(f'  ⚠️  Нет .py файлов')
        missing.append(f'{skill_dir.name}/ (нет скриптов)')
    
    if ps_files:
        for f in ps_files:
            print(f'  ✅ {f.name}')
    
    # Проверка конфигов
    config_files = list(skill_dir.glob('*.yaml')) + list(skill_dir.glob('*.json'))
    if config_files:
        for f in config_files[:2]:
            print(f'  ✅ {f.name}')

print("\n" + "=" * 60)
print("📊 ИТОГИ")
print("=" * 60)
print(f"Всего скиллов: {len(list(skills_dir.iterdir()))}")
print(f"Отсутствующих файлов: {len(missing)}")

if missing:
    print("\n❌ НЕДОСТАЮЩИЕ ФАЙЛЫ:")
    for item in missing:
        print(f"  - {item}")
else:
    print("✅ Все файлы на месте!")
