import os
import glob
from collections import defaultdict

# Настройки
ROOT_DIR = '.'  # Корневая директория репозитория
MARKDOWN_PATTERN = '**/*.md' # ** нужен для рекурсивного поиска в glob

# Словарь для хранения статистики (объявлен до использования)
stats = defaultdict(int)
keywords = ['# ', '## ', '### ']

# 1. Сначала объявляем функцию
def analyze_file(file_path, stats_dict):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            stats_dict['files_processed'] += 1
            stats_dict['total_chars'] += len(content)
            stats_dict['total_words'] += len(content.split())
            for keyword in keywords:
                stats_dict[f'{keyword}_count'] += content.count(keyword)
    except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
        # Системный подход: не падаем из-за одного файла, а логируем и идём дальше
        print(f"⚠️ Пропуск файла {file_path}: {e}")

# 2. Затем выполняем основной цикл (оставили только один, самый надёжный вариант с glob)
print("🔍 Начинаю анализ Markdown-файлов...")
for md_file in glob.glob(os.path.join(ROOT_DIR, MARKDOWN_PATTERN), recursive=True):
    # Исключаем скрытые директории (например, .venv, .git), если нужно
    if '/.' not in md_file.replace('\\', '/'): 
        analyze_file(md_file, stats)

# 3. Вывод результатов
print("\n📋 Summary Report:")
print(f"- Total markdown files processed: {stats['files_processed']}")
print(f"- Total characters analyzed: {stats['total_chars']:,}")
print(f"- Total words counted: {stats['total_words']:,}")
for keyword in keywords:
    print(f"- Count of '{keyword.strip()}' headers: {stats[f'{keyword}_count']:,}")