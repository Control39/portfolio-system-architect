#!/usr/bin/env python3
"""Assistant Orchestrator — система анализа зрелости архитектуры
"""
import argparse
import logging
import sys
from pathlib import Path

from assistant_orchestrator.core.analyzer import AssistantOrchestrator
from assistant_orchestrator.core.reporter import Reporter


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO

    # Clear any existing handlers
    logging.getLogger().handlers.clear()

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("orchestrator.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Suppress noisy logs from dependencies
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(
        description="Assistant Orchestrator — анализ экосистемы проекта",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m assistant_orchestrator                    # Анализ текущей директории
  python -m assistant_orchestrator --root ./myproject --format json
  python -m assistant_orchestrator --output reports --verbose
        """,
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Корень проекта (по умолчанию: текущая директория)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Формат отчёта (по умолчанию: text)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="Папка для отчётов (по умолчанию: reports)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Подробный вывод (debug уровень логирования)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Показать версию и выйти",
    )

    args = parser.parse_args()

    if args.version:
        from assistant_orchestrator import __version__
        print(f"Assistant Orchestrator v{__version__}")
        sys.exit(0)

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("🚀 Запуск Assistant Orchestrator")
    logger.info(f"Корень проекта: {args.root}")
    logger.info(f"Формат отчёта: {args.format}")
    logger.info(f"Выходная папка: {args.output}")
    logger.info("=" * 60)

    try:
        # Проверяем существование корневой директории
        root_path = Path(args.root).resolve()
        if not root_path.exists():
            logger.error(f"Корневая директория не существует: {root_path}")
            sys.exit(1)

        # Создаём оркестратор и запускаем анализ
        orchestrator = AssistantOrchestrator(project_root=str(root_path))
        analysis = orchestrator.run_full_analysis()

        # Создаём папку для отчётов
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)

        # Генерируем имя файла с timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Map format to file extension
        format_ext = {
            "text": "txt",
            "json": "json",
            "html": "html",
        }
        ext = format_ext.get(args.format, args.format)
        filename = f"analysis_{timestamp}.{ext}"
        output_path = output_dir / filename

        # Сохраняем отчёт
        reporter = Reporter(analysis)
        reporter.save(output_path)

        # Выводим краткую сводку
        print("\n" + "=" * 60)
        print("✅ Анализ завершён успешно!")
        print(f"📄 Отчёт сохранён: {output_path}")
        print("=" * 60)

        # Показываем краткую статистику
        services = analysis.microservices.get("services", [])
        skills = analysis.skill_markers.get("total_count", 0)
        docs = len(analysis.architecture_docs)
        commits = analysis.git_stats.get("total_commits", 0)

        print("\n📊 Краткая статистика:")
        print(f"  • Микросервисы: {len(services)}")
        print(f"  • Навыки (маркеры): {skills}")
        print(f"  • Архитектурные документы: {docs}")
        print(f"  • Коммитов в Git: {commits}")

        logger.info("Анализ успешно завершён")

    except KeyboardInterrupt:
        logger.warning("Анализ прерван пользователем")
        print("\n⚠️  Анализ прерван")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Критическая ошибка при анализе: {e}")
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

