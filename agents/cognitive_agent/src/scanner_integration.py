#!/usr/bin/env python
"""
Интеграция Project Scanner с Cognitive Agent.

Этот модуль позволяет вызывать сканер из других компонентов агента.

Использование:
    from agents.cognitive_agent.src.scanner_integration import scan_project

    # Базовое сканирование
    results = scan_project("C:\\my-project")

    # С настройками
    results = scan_project(
        "C:\\my-project",
        mode="git_diff",
        cache=True,
        export_path="results.json"
    )
"""

import logging
from pathlib import Path
from typing import Any

from agents.cognitive_agent.src.project_scanner import ProjectScanner, ScannerConfig

logger = logging.getLogger(__name__)


def scan_project(
    project_path: str,
    mode: str = "full",
    paths: list[str] | None = None,
    config_path: str | None = None,
    export_path: str | None = None,
    export_format: str = "json",
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Сканировать проект и вернуть результаты.

    Args:
        project_path: Путь к проекту для сканирования
        mode: Режим сканирования ("full", "git_diff", "paths")
        paths: Список путей для выборочного сканирования (для mode="paths")
        config_path: Путь к файлу конфигурации (опционально)
        export_path: Путь для экспорта результатов (опционально)
        export_format: Формат экспорта ("json" или "csv")
        use_cache: Использовать кэш (по умолчанию True)

    Returns:
        Словарь с результатами сканирования

    Raises:
        ValueError: Если путь не существует или некорректен
        FileNotFoundError: Если файл конфигурации не найден
    """
    # Валидация входных данных
    project_path = Path(project_path).resolve()

    if not project_path.exists():
        raise ValueError(f"Путь не найден: {project_path}")

    if not project_path.is_dir():
        raise ValueError(f"Путь не является директорией: {project_path}")

    if mode not in ["full", "git_diff", "paths"]:
        raise ValueError(f"Некорректный режим: {mode}. Используйте: full, git_diff, paths")

    if mode == "paths" and not paths:
        raise ValueError("Режим 'paths' требует указания путей через параметр 'paths'")

    # Загрузка конфигурации
    config = None
    if config_path:
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")
        config = ProjectScanner.load_config(str(config_path))
        logger.info(f"✅ Конфигурация загружена: {config_path}")
    else:
        config = ScannerConfig()

    # Отключение кэша если нужно
    if not use_cache:
        # Удаляем файл кэша если существует
        cache_file = project_path / config.cache_file
        if cache_file.exists():
            cache_file.unlink()
            logger.info("🗑️  Кэш удалён")

    # Создание сканера
    logger.info(f"🔍 Запуск сканирования: {project_path} (режим: {mode})")
    scanner = ProjectScanner(str(project_path), config)

    # Выполнение сканирования
    if mode == "full":
        results = scanner.scan_full()
    elif mode == "git_diff":
        results = scanner.scan_git_diff()
    else:  # paths
        results = scanner.scan_paths(paths)

    # Экспорт результатов если указан путь
    if export_path:
        export_path = Path(export_path)
        scanner.export_results(results, str(export_path), export_format)
        logger.info(f"✅ Результаты экспортированы: {export_path}")

    logger.info(f"✅ Сканирование завершено за {results['duration']:.2f} сек")

    return results


def get_scan_summary(results: dict[str, Any]) -> str:
    """
    Создать краткую текстовую сводку результатов сканирования.

    Args:
        results: Результаты сканирования от scan_project()

    Returns:
        Форматированная строка со сводкой
    """
    lines = [
        "=" * 60,
        "📊 СТАТИСТИКА СКАНИРОВАНИЯ",
        "=" * 60,
        f"Режим:           {results['mode']}",
        f"Длительность:    {results['duration']:.2f} сек",
    ]

    if results["mode"] == "full":
        lines.extend(
            [
                f"Всего файлов:    {results['total_files']}",
                f"Сканировано:     {results['scanned_files']}",
                f"Игнорировано:    {results['ignored_files']}",
            ]
        )
    elif results["mode"] == "git_diff":
        lines.extend(
            [
                f"Изменённых:      {results['changed_files']}",
                f"Сканировано:     {results['scanned_files']}",
                f"Пропущено:       {results['skipped_files']}",
            ]
        )
    else:
        lines.extend(
            [
                f"Для проверки:    {results['total_files']}",
                f"Сканировано:     {results['scanned_files']}",
            ]
        )

    lines.append("=" * 60)

    return "\n".join(lines)


class ProjectScannerService:
    """
    Сервис для работы со сканером проектов.

    Предоставляет высокоуровневый API для интеграции с Cognitive Agent.
    """

    def __init__(self, default_project_path: str | None = None, default_config_path: str | None = None):
        """
        Инициализировать сервис.

        Args:
            default_project_path: Путь к проекту по умолчанию
            default_config_path: Путь к конфигурации по умолчанию
        """
        self.default_project_path = default_project_path
        self.default_config_path = default_config_path
        self._last_results: dict[str, Any] | None = None

    def scan(
        self,
        project_path: str | None = None,
        mode: str = "full",
        paths: list[str] | None = None,
        export_path: str | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Выполнить сканирование проекта.

        Args:
            project_path: Путь к проекту (используется default если не указан)
            mode: Режим сканирования
            paths: Пути для выборочного сканирования
            export_path: Путь для экспорта результатов
            use_cache: Использовать кэш

        Returns:
            Результаты сканирования
        """
        path = project_path or self.default_project_path
        if not path:
            raise ValueError("Путь к проекту не указан")

        results = scan_project(
            project_path=path,
            mode=mode,
            paths=paths,
            config_path=self.default_config_path,
            export_path=export_path,
            use_cache=use_cache,
        )

        self._last_results = results
        return results

    def get_last_summary(self) -> str | None:
        """
        Получить сводку последнего сканирования.

        Returns:
            Текстовая сводка или None если сканирование не выполнялось
        """
        if self._last_results is None:
            return None
        return get_scan_summary(self._last_results)

    def export_last_results(self, export_path: str, export_format: str = "json") -> Path:
        """
        Экспортировать результаты последнего сканирования.

        Args:
            export_path: Путь для экспорта
            export_format: Формат экспорта

        Returns:
            Путь к экспортированному файлу

        Raises:
            ValueError: Если последнее сканирование не выполнялось
        """
        if self._last_results is None:
            raise ValueError("Нет результатов для экспорта. Сначала выполните сканирование.")

        export_path = Path(export_path)

        # Создаём сканер для экспорта (нужен для доступа к методу export_results)
        if self.default_project_path:
            scanner = ProjectScanner(self.default_project_path)
            scanner.export_results(self._last_results, str(export_path), export_format)

        return export_path


# Утилита для вызова из command-line
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Project Scanner Integration")
    parser.add_argument("project_path", help="Путь к проекту")
    parser.add_argument("--mode", choices=["full", "git_diff", "paths"], default="full")
    parser.add_argument("--paths", nargs="*", default=[])
    parser.add_argument("--export", help="Путь для экспорта")
    parser.add_argument("--format", choices=["json", "csv"], default="json")

    args = parser.parse_args()

    results = scan_project(
        args.project_path,
        mode=args.mode,
        paths=args.paths if args.paths else None,
        export_path=args.export,
        export_format=args.format,
    )

    print(get_scan_summary(results))
