# Исправление импортов в тестах
import os
import re

tests_dir = r"C:\repo\apps\ai_config_manager\tests"

# Шаблоны для замены
replacements = [
    (r'from src\.(\w+) import', r'from ai_config_manager.src.\1 import'),
    (r'import src\.(\w+)', r'import ai_config_manager.src.\1'),
]

# Обработка всех тестовых файлов
for filename in os.listdir(tests_dir):
    if not filename.endswith('.py') or filename == '__init__.py':
        continue
    
    filepath = os.path.join(tests_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Исправлено: {filename}')
    else:
        print(f'Без изменений: {filename}')

print('\nГотово!')
