#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Wrapper-скрипт для запуска Project Scanner из корня проекта.

Использование:
    python scripts/run_project_scanner.py <project_path> [options]

Примеры:
    # Полное сканирование
    python scripts/run_project_scanner.py C:\my-project --mode full

    # Только изменённые файлы (git diff)
    python scripts/run_project_scanner.py C:\my-project --mode git_diff

    # Конкретные пути
    python scripts/run_project_scanner.py C:\my-project --mode paths --paths src/ tests/

    # С экспортом результатов
    python scripts/run_project_scanner.py C:\my-project --mode full --export results.json --format json
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем корень проекта в sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from apps.cognitive_agent.src.project_scanner import ProjectScanner, ScannerConfig

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Оптимизированный сканер проекта для Cognitive Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Полное сканирование
  python scripts/run_project_scanner.py C:\\my-project --mode full

  # Только изменённые файлы (git diff)
  python scripts/run_project_scanner.py C:\\my-project --mode git_diff

  # Конкретные пути
  python scripts/run_project_scanner.py C:\\my-project --mode paths --paths src/ tests/

  # С экспортом результатов
  python scripts/run_project_scanner.py C:\\my-project --mode full --export results.json --format json
        """
    )

    parser.add_argument(
        "project_path",
        help="Путь к проекту для сканирования"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "git_diff", "paths"],
        default="full",
        help="Режим сканирования (по умолчанию: full)"
    )

    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Пути для выборочного сканирования (используется с --mode paths)"
    )

    parser.add_argument(
        "--config",
        help="Файл конфигурации сканера (JSON)"
    )

    parser.add_argument(
        "--export",
        help="Файл для экспорта результатов"
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Формат экспорта (по умолчанию: json)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Включить подробный вывод отладочной информации"
    )

    args = parser.parse_args()

    # Настройка уровня логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Проверка пути к проекту
    project_path = Path(args.project_path)
    if not project_path.exists():
        logger.error(f"❌ Путь не найден: {project_path}")
        sys.exit(1)

    if not project_path.is_dir():
        logger.error(f"❌ Путь не является директорией: {project_path}")
        sys.exit(1)

    # Загрузка конфигурации
    config = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"❌ Файл конфигурации не найден: {config_path}")
            sys.exit(1)
        config = ProjectScanner.load_config(str(config_path))
        logger.info(f"✅ Конфигурация загружена: {config_path}")
    else:
        config = ScannerConfig()

    # Создание сканера
    logger.info(f"🔍 Запуск сканирования проекта: {project_path}")
    scanner = ProjectScanner(str(project_path), config)

    # Выполнение сканирования
    if args.mode == "full":
        logger.info("📋 Режим: полное сканирование")
        results = scanner.scan_full()
    elif args.mode == "git_diff":
        logger.info("📋 Режим: инкрементальное сканирование (git diff)")
        results = scanner.scan_git_diff()
    else:  # paths
        if not args.paths:
            logger.error("❌ Ошибка: --paths требуется для режима 'paths'")
            parser.print_help()
            sys.exit(1)
        logger.info(f"📋 Режим: выборочное сканирование путей: {args.paths}")
        results = scanner.scan_paths(args.paths)

    # Экспорт результатов
    if args.export:
        export_path = Path(args.export)
        scanner.export_results(results, str(export_path), args.format)
        logger.info(f"✅ Результаты экспортированы: {export_path}")

    # Вывод краткой статистики
    print(f"\n{'='*60}")
    print("📊 СТАТИСТИКА СКАНИРОВАНИЯ")
    print(f"{'='*60}")
    print(f"Режим:              {results['mode']}")
    print(f"Длительность:       {results['duration']:.2f} сек")

    if results['mode'] == 'full':
        print(f"Всего файлов:       {results['total_files']}")
        print(f"Сканировано:        {results['scanned_files']}")
        print(f"Игнорировано:       {results['ignored_files']}")
    elif results['mode'] == 'git_diff':
        print(f"Изменённых файлов:  {results['changed_files']}")
        print(f"Сканировано:        {results['scanned_files']}")
        print(f"Пропущено:          {results['skipped_files']}")
    else:
        print(f"Всего для проверки: {results['total_files']}")
        print(f"Сканировано:        {results['scanned_files']}")

    print(f"{'='*60}")

    # Вывод первых нескольких файлов (если есть)
    files = results.get('files', [])
    if files:
        print(f"\n📁 Первые 5 отсканированных файлов:")
        for i, file_info in enumerate(files[:5], 1):
            print(f"  {i}. {file_info['path']} ({file_info['size']} байт)")

    if len(files) > 5:
        print(f"  ... и ещё {len(files) - 5} файлов")

    print()
    sys.exit(0)


if __name__ == "__main__":
    main()
