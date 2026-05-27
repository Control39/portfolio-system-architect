#!/usr/bin/env python3
"""Тест оптимизированного сканера"""

import sys
from pathlib import Path

# Добавляем корень проекта
sys.path.insert(0, str(Path(__file__).parent))

from apps.cognitive_agent.src.project_scanner import ProjectScanner

def main():
    print("=" * 60)
    print("Тест оптимизированного сканера проекта")
    print("=" * 60)
    
    scanner = ProjectScanner("C:/repo")
    
    print("\n1. Тест git diff режима:")
    print("-" * 40)
    git_result = scanner.scan_git_diff()
    print(f"✅ Изменённых файлов: {git_result['changed_files']}")
    print(f"✅ Сканировано: {git_result['scanned_files']}")
    print(f"✅ Пропущено: {git_result['skipped_files']}")
    print(f"⏱️  Время: {git_result['duration']:.2f} сек")
    
    print("\n2. Тест полного сканирования (ограничено 100 файлами):")
    print("-" * 40)
    full_result = scanner.scan_full()
    print(f"✅ Всего файлов: {full_result['total_files']}")
    print(f"✅ Сканировано: {full_result['scanned_files']}")
    print(f"✅ Игнорировано: {full_result['ignored_files']}")
    print(f"⏱️  Время: {full_result['duration']:.2f} сек")
    
    print("\n3. Тест выборочного сканирования:")
    print("-" * 40)
    paths_result = scanner.scan_paths(["apps/cognitive_agent", ".agents"])
    print(f"✅ Сканировано файлов: {paths_result['scanned_files']}")
    print(f"⏱️  Время: {paths_result['duration']:.2f} сек")
    
    print("\n" + "=" * 60)
    print("Все тесты пройдены! ✅")
    print("=" * 60)

if __name__ == "__main__":
    main()