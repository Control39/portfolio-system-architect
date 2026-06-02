import os
import shutil
from pathlib import Path

def clean_root():
    """
    Скрипт для очистки корневой директории проекта.
    Переносит утилиты в /tools, объединяет конфиги.
    """
    repo_root = Path.cwd()
    tools_dir = repo_root / 'tools'

    # Список скриптов для переноса в /tools
    scripts_to_move = [
        'analyze_logs.py',
        'check_skills.py',
        'find_plans.py',
        'move_agent_plans.py',
        'consolidate_cases.py',
        'copy_codeassistant_backup.py',
        'check_duplicates.py',
        'check_rules.py',
        'check_skills_duplicates.py',
        'check_teacher_duplicates.py',
        'delete_duplicates.py',
        'security_scan.py',
        'setup_jekyll.py',
        'setup_ollama.py',
        'migrate_codeassistant.py'
    ]

    # Создаем папку tools, если её нет
    tools_dir.mkdir(exist_ok=True)

    # Переносим скрипты в tools
    for script in scripts_to_move:
        src = repo_root / script
        dst = tools_dir / script
        if src.exists():
            print(f'Перемещаем {script} в /tools')
            shutil.move(str(src), str(dst))

    # Объединяем .coveragerc и .coveragerc.cd
    # Основной конфиг
    coveragerc_main = repo_root / '.coveragerc'
    coveragerc_cd = repo_root / '.coveragerc.cd'

    if coveragerc_cd.exists():
        print('Объединяем .coveragerc и .coveragerc.cd')
        # Читаем дополнительные настройки
        with open(coveragerc_cd, 'r', encoding='utf-8') as f:
            cd_content = f.read()

        # Добавляем исключения из cd в основной конфиг
        with open(coveragerc_main, 'a', encoding='utf-8') as f:
            f.write('\n\n# Добавлено из .coveragerc.cd\n')
            f.write(cd_content)

        # Удаляем временный конфиг
        coveragerc_cd.unlink()
        print('Удален .coveragerc.cd')

    print('Очистка корня завершена.')

if __name__ == '__main__':
    clean_root()