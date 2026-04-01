#!/usr/bin/env python3
"""
Скрипт для поиска CJK (китайских, японских, корейских) иероглифов в файлах репозитория.
Используется для очистки текстовых файлов от случайно попавших иероглифов.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Регулярное выражение для поиска CJK иероглифов
# Диапазоны Unicode:
# - Основные китайские иероглифы: U+4E00 - U+9FFF
# - Расширенные китайские: U+3400 - U+4DBF
# - Совместимые иероглифы: U+F900 - U+FAFF
# - Хирагана (японская): U+3040 - U+309F
# - Катакана (японская): U+30A0 - U+30FF
# - Корейские хангыль: U+AC00 - U+D7AF
CJK_PATTERN = re.compile(
    r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+'
)

# Расширения текстовых файлов для проверки
TEXT_EXTENSIONS = {
    '.md', '.txt', '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
    '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.csv', '.tsv',
    '.rst', '.tex', '.sql', '.sh', '.bash', '.ps1', '.bat', '.cfg', '.ini',
    '.toml', '.env', '.gitignore', '.dockerignore', '.editorconfig'
}

# Папки для игнорирования
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
    '.idea', '.vscode', 'build', 'dist', 'target', 'out'
}

# Файлы для игнорирования
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    '*.pyc', '*.pyo', '*.so', '*.dll', '*.exe',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico',
    '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
    '*.zip', '*.tar', '*.gz', '*.7z', '*.rar'
}

def should_ignore_file(file_path: Path) -> bool:
    """Проверить, нужно ли игнорировать файл"""
    # Игнорируем скрытые файлы (начинающиеся с точки, кроме некоторых)
    if file_path.name.startswith('.') and file_path.name not in {'.gitignore', '.dockerignore', '.editorconfig'}:
        return True
    
    # Игнорируем файлы в игнорируемых папках
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return True
    
    # Игнорируем файлы с игнорируемыми расширениями
    if file_path.suffix.lower() in {'.pyc', '.pyo', '.so', '.dll', '.exe', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico'}:
        return True
    
    # Игнорируем определенные имена файлов
    if file_path.name in IGNORE_FILES:
        return True
    
    return False

def find_cjk_characters(file_path: Path) -> List[Dict[str, Any]]:
    """Найти CJK иероглифы в файле"""
    try:
        # Пробуем разные кодировки
        for encoding in ['utf-8', 'cp1251', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            # Если ни одна кодировка не подошла, пропускаем файл
            return []
    except (IOError, PermissionError) as e:
        print(f"⚠️  Ошибка чтения файла {file_path}: {e}", file=sys.stderr)
        return []
    
    matches = []
    lines = content.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        for match in CJK_PATTERN.finditer(line):
            start = max(0, match.start() - 20)
            end = min(len(line), match.end() + 20)
            context = line[start:end]
            if start > 0:
                context = '...' + context
            if end < len(line):
                context = context + '...'
            
            matches.append({
                'line': line_num,
                'column': match.start() + 1,
                'text': match.group(),
                'context': context,
                'full_line': line
            })
    
    return matches

def scan_repository(root_dir: str = '.') -> Dict[str, List[Dict[str, Any]]]:
    """Рекурсивно сканировать репозиторий на наличие CJK иероглифов"""
    root_path = Path(root_dir).resolve()
    results = {}
    
    print(f"🔍 Сканирование репозитория: {root_path}")
    print(f"📁 Игнорируемые папки: {', '.join(sorted(IGNORE_DIRS))}")
    print(f"📄 Проверяемые расширения: {', '.join(sorted(TEXT_EXTENSIONS))}")
    print()
    
    total_files = 0
    scanned_files = 0
    
    for file_path in root_path.rglob('*'):
        if file_path.is_dir():
            continue
        
        total_files += 1
        
        # Пропускаем игнорируемые файлы
        if should_ignore_file(file_path):
            continue
        
        # Проверяем только текстовые файлы с нужными расширениями
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        
        scanned_files += 1
        matches = find_cjk_characters(file_path)
        
        if matches:
            # Сохраняем относительный путь для удобства чтения
            rel_path = file_path.relative_to(root_path)
            results[str(rel_path)] = matches
    
    print(f"📊 Статистика:")
    print(f"   Всего файлов: {total_files}")
    print(f"   Проверено файлов: {scanned_files}")
    print(f"   Файлов с иероглифами: {len(results)}")
    print()
    
    return results

def print_results(results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Вывести результаты поиска"""
    if not results:
        print("✅ Иероглифы не найдены!")
        return
    
    print(f"🔍 Найдено {len(results)} файлов с иероглифами:\n")
    
    for file_path, matches in sorted(results.items()):
        print(f"📄 {file_path}")
        print(f"   Всего совпадений: {len(matches)}")
        
        # Показываем первые 3 совпадения для каждого файла
        for i, match in enumerate(matches[:3], 1):
            print(f"   {i}. Строка {match['line']}, колонка {match['column']}:")
            print(f"      Иероглифы: '{match['text']}'")
            print(f"      Контекст: {match['context']}")
        
        if len(matches) > 3:
            print(f"   ... и еще {len(matches) - 3} совпадений")
        
        print("-" * 80)

def suggest_replacements(text: str) -> str:
    """Предложить замены для часто встречающихся иероглифов"""
    # Часто встречающиеся иероглифы и их возможные замены
    common_replacements = {
        '常见': 'распространен',  # китайский: часто встречающийся
        '问题': 'проблема',       # китайский: проблема
        '答案': 'ответ',          # китайский: ответ
        '帮助': 'помощь',         # китайский: помощь
        '错误': 'ошибка',         # китайский: ошибка
        '成功': 'успех',          # китайский: успех
        '测试': 'тест',           # китайский: тест
        '开发': 'разработка',     # китайский: разработка
        '用户': 'пользователь',   # китайский: пользователь
        '系统': 'система',        # китайский: система
    }
    
    for cjk, replacement in common_replacements.items():
        if cjk in text:
            text = text.replace(cjk, replacement)
    
    return text

def generate_report(results: Dict[str, List[Dict[str, Any]]], report_file: str = 'cjk_scan_report.md') -> None:
    """Сгенерировать отчет в формате Markdown"""
    if not results:
        return
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Отчет по поиску CJK иероглифов\n\n")
        f.write(f"**Найдено файлов с иероглифами:** {len(results)}\n\n")
        
        for file_path, matches in sorted(results.items()):
            f.write(f"## 📄 {file_path}\n\n")
            f.write(f"**Всего совпадений:** {len(matches)}\n\n")
            
            for match in matches:
                f.write(f"### Строка {match['line']}, колонка {match['column']}\n")
                f.write(f"**Иероглифы:** `{match['text']}`\n\n")
                f.write(f"**Контекст:**\n```\n{match['full_line']}\n```\n\n")
                
                suggested = suggest_replacements(match['text'])
                if suggested != match['text']:
                    f.write(f"**Предлагаемая замена:** `{match['text']}` → `{suggested}`\n\n")
            
            f.write("---\n\n")
        
        f.write("## Рекомендации\n\n")
        f.write("1. Проверьте каждый файл вручную перед заменой\n")
        f.write("2. Убедитесь, что замена сохраняет смысл текста\n")
        f.write("3. Для технических терминов используйте английские эквиваленты\n")
        f.write("4. Сохраняйте исходный текст в комментариях при необходимости\n")
    
    print(f"📝 Отчет сохранен в файл: {report_file}")

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Поиск CJK (китайских, японских, корейских) иероглифов в файлах репозитория'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к корневой директории репозитория (по умолчанию: текущая директория)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Сгенерировать отчет в формате Markdown'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Предложить автоматические исправления (экспериментально)'
    )
    
    args = parser.parse_args()
    
    # Сканируем репозиторий
    results = scan_repository(args.path)
    
    # Выводим результаты
    print_results(results)
    
    # Генерируем отчет если нужно
    if args.report and results:
        generate_report(results)
    
    # Предлагаем исправления если нужно
    if args.fix and results:
        print("\n🔧 Экспериментальная функция автоматических исправлений:")
        print("   Для каждого файла будут предложены замены часто встречающихся иероглифов")
        print("   ВНИМАНИЕ: Всегда проверяйте изменения вручную!\n")
        
        for file_path, matches in sorted(results.items()):
            print(f"📄 {file_path}")
            for match in matches[:2]:  # Показываем для первых двух совпадений
                suggested = suggest_replacements(match['text'])
                if suggested != match['text']:
                    print(f"   '{match['text']}' → '{suggested}' (строка {match['line']})")
            if len(matches) > 2:
                print(f"   ... и еще {len(matches) - 2} совпадений для проверки")
    
    # Возвращаем код выхода
    if results:
        print(f"\n❌ Найдены файлы с иероглифами. Код выхода: 1")
        sys.exit(1)
    else:
        print(f"\n✅ Проверка завершена успешно. Код выхода: 0")
        sys.exit(0)

if __name__ == '__main__':
    main()
