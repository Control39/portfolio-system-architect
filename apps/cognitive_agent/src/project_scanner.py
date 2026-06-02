import os
import hashlib
import json
import logging
import subprocess
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from tqdm import tqdm  # Для прогресс‑бара

try:
    import pathspec

    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

logger = logging.getLogger(__name__)


@dataclass
class ScannerConfig:
    """Конфигурация сканера"""

    timeout: int = 10
    max_workers: int = 4
    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    include_extensions: List[str] = None
    extra_ignores: List[str] = None
    cache_file: str = ".cognitive_agent_scan_cache.json"

    def __post_init__(self):
        if self.include_extensions is None:
            self.include_extensions = [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".json",
                ".yml",
                ".yaml",
                ".md",
            ]
        if self.extra_ignores is None:
            self.extra_ignores = ["node_modules", ".venv", "__pycache__", ".git"]


class ProjectScanner:
    """Оптимизированный сканер проекта с улучшенной производительностью и гибкостью"""

    def __init__(self, project_path: str, config: Optional[ScannerConfig] = None):
        self.project_path = Path(project_path)
        self.config = config or ScannerConfig()
        self.gitignore_spec = None
        self.last_scan_cache: Dict[str, str] = {}
        self.cache_file = self.project_path / self.config.cache_file

        # Загрузка .gitignore
        self._load_gitignore()

        # Загрузка кэша
        self._load_cache()

    def _load_gitignore(self):
        """Загрузить правила .gitignore"""
        if not HAS_PATHSPEC:
            logger.warning(
                "pathspec не установлен. .gitignore игнорируется. Установите: pip install pathspec"
            )
            return

        gitignore_path = self.project_path / ".gitignore"
        patterns = []

        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                patterns = f.read().splitlines()

            # Фильтрация пустых строк и комментариев
            patterns = [p.strip() for p in patterns if p.strip() and not p.startswith("#")]

        # Добавляем дополнительные игнорируемые директории
        patterns.extend(self.config.extra_ignores)

        try:
            self.gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
            logger.info(f"✅ Загружено {len(patterns)} правил из .gitignore и конфигурации")
        except Exception as e:
            logger.error(f"Ошибка загрузки .gitignore: {e}")

    def _load_cache(self):
        """Загрузить кэш хэшей файлов"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.last_scan_cache = json.load(f)
                logger.info(f"✅ Кэш загружен: {len(self.last_scan_cache)} файлов")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Ошибка загрузки кэша: {e}")
                self.last_scan_cache = {}

    def _save_cache(self):
        """Сохранить кэш хэшей"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.last_scan_cache, f, indent=2)
        except IOError as e:
            logger.error(f"Ошибка сохранения кэша: {e}")

    def _cleanup_cache(self):
        """Удалить записи для несуществующих файлов"""
        existing_files = set()

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            if self._is_ignored(root_path):
                dirs.clear()
                continue
            for file in files:
                file_path = (root_path / file).relative_to(self.project_path)
                existing_files.add(str(file_path))

        # Удаляем из кэша записи для удалённых файлов
        to_remove = [k for k in self.last_scan_cache if k not in existing_files]
        for key in to_remove:
            del self.last_scan_cache[key]

        logger.info(f"🗑️  Удалено {len(to_remove)} устаревших записей из кэша")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычислить MD5 хэш файла с учётом ограничений по размеру"""
        file_size = file_path.stat().st_size
        if file_size > self.config.max_file_size:
            logger.debug(f"Пропускаем большой файл: {file_path} ({file_size} байт)")
            return ""

        try:
            hash_md5 = hashlib.md5(usedforsecurity=False)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, IOError) as e:
            logger.warning(f"Не удалось вычислить хэш {file_path}: {e}")
            return ""

    def _is_ignored(self, path: Path) -> bool:
        """Проверить, игнорируется ли файл через .gitignore"""
        if not self.gitignore_spec:
            return False

        try:
            rel_path = path.relative_to(self.project_path)
            rel_path_str = rel_path.as_posix()  # Гарантированно Unix‑стиль
            return self.gitignore_spec.match_file(rel_path_str)
        except ValueError:
            # Если путь не внутри проекта
            return False

    def _is_git_repo(self) -> bool:
        """Проверить, является ли проект Git-репозиторием"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5,  # Добавлен таймаут для предотвращения зависаний
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warning("Git check timed out after 5 seconds")
            return False
        except (FileNotFoundError, OSError):
            return False

    def _get_all_changed_files(self) -> List[Path]:
        """Получить все изменённые файлы (working tree + staged + untracked)"""
        if not self._is_git_repo():
            logger.warning("Проект не является Git-репозиторием")
            return []

        try:
            # Изменённые и staged файлы
            result_changed = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )

            # Untracked файлы (новые, ещё не добавленные в git)
            result_untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )

            changed = []
            if result_changed.returncode == 0:
                changed = [Path(p) for p in result_changed.stdout.strip().split("\n") if p.strip()]

            untracked = []
            if result_untracked.returncode == 0:
                untracked = [Path(p) for p in result_untracked.stdout.strip().split("\n") if p.strip()]

            # Объединить и логировать
            all_files = changed + untracked
            logger.info(
                f"🔍 Найдено {len(changed)} изменённых + {len(untracked)} новых файлов"
            )
            return all_files

        except subprocess.TimeoutExpired as e:
            logger.error(f"Git command timed out: {e}")
            return []
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error(f"Ошибка git: {e}")
            return []

    def _filter_by_extension(self, file_path: Path) -> bool:
        """Проверить, соответствует ли файл разрешённым расширениям"""
        return (
            not self.config.include_extensions or file_path.suffix in self.config.include_extensions
        )

    def _process_file(self, file_path: Path, rel_path: Path) -> Optional[Dict[str, Any]]:
        """Обработать один файл — вычислить хэш и собрать информацию"""
        if not file_path.is_file():
            return None

        # Проверка расширения
        if not self._filter_by_extension(file_path):
            logger.debug(f"⏭️  Игнорируется по расширению: {file_path}")
            return None

        # Проверка .gitignore
        if self._is_ignored(file_path):
            logger.debug(f"⏭️  Игнорируется: {file_path}")
            return None

        try:
            # Получаем текущий хэш
            current_hash = self._calculate_file_hash(file_path)
            if not current_hash:  # Файл слишком большой или ошибка
                return None

            # Получаем предыдущий хэш из кэша
            last_hash = self.last_scan_cache.get(str(rel_path))

            # Если файл не изменился, пропускаем
            if current_hash == last_hash:
                logger.debug(f"⏭️  Без изменений: {file_path}")
                return None

            # Собираем информацию о файле
            file_stat = file_path.stat()
            return {
                "path": str(rel_path),
                "hash": current_hash,
                "size": file_stat.st_size,
                "mtime": file_stat.st_mtime,
            }

        except (OSError, IOError) as e:
            logger.warning(f"Ошибка обработки файла {file_path}: {e}")
            return None

    def _parallel_scan_files(self, file_list: List[Path]) -> List[Dict[str, Any]]:
        """Параллельное сканирование файлов с прогресс-баром"""
        results = []
        total_files = len(file_list)

        if total_files == 0:
            return results

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Создаём прогресс-бар
            with tqdm(total=total_files, desc="Сканирование файлов", unit="file") as pbar:
                # Подготавливаем задачи
                tasks = []
                for file_path in file_list:
                    try:
                        rel_path = file_path.relative_to(self.project_path)
                        tasks.append(executor.submit(self._process_file, file_path, rel_path))
                    except ValueError:
                        continue

                # Собираем результаты
                for future in concurrent.futures.as_completed(tasks):
                    result = future.result()
                    pbar.update(1)  # Обновляем прогресс-бар ВСЕГДА, не только для результатов
                    if result:
                        results.append(result)

        return results

    def scan_git_diff(self) -> Dict[str, Any]:
        """Сканировать только изменённые файлы (git diff)"""
        logger.info("🔄 Запуск инкрементального сканирования (git diff)...")
        start_time = datetime.now()

        # Получаем изменённые файлы
        changed_files = self._get_all_changed_files()

        if not changed_files:
            logger.info("✅ Нет изменённых файлов. Скан не требуется.")
            return {
                "mode": "git_diff",
                "changed_files": 0,
                "scanned_files": 0,
                "skipped_files": 0,
                "duration": (datetime.now() - start_time).total_seconds(),
                "files": [],
                "summary": "Нет изменений",
            }

        # Параллельное сканирование
        scanned = self._parallel_scan_files(changed_files)

        # Обновляем кэш только для отсканированных файлов
        for file_info in scanned:
            self.last_scan_cache[file_info["path"]] = file_info["hash"]

        # Сохраняем кэш
        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()
        skipped = len(changed_files) - len(scanned)

        logger.info(f"✅ Сканирование завершено за {duration:.2f}s")
        logger.info(f"   Изменённых файлов: {len(changed_files)}")
        logger.info(f"   Сканировано: {len(scanned)}")
        logger.info(f"   Пропущено (без изменений/ошибки): {skipped}")

        return {
            "mode": "git_diff",
            "changed_files": len(changed_files),
            "scanned_files": len(scanned),
            "skipped_files": skipped,
            "duration": duration,
            "files": scanned,
            "timestamp": start_time.isoformat(),
        }

    def scan_full(self) -> Dict[str, Any]:
        """Полное сканирование проекта (с уважением .gitignore)"""
        logger.info("🔄 Запуск полного сканирования проекта...")
        start_time = datetime.now()

        all_files = []

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)

            # Проверка директории на игнорирование
            if self._is_ignored(root_path):
                dirs.clear()  # Не спускаться в игнорируемые директории
                continue

            for file in files:
                file_path = root_path / file
                all_files.append(file_path)

        # Параллельное сканирование всех файлов
        scanned = self._parallel_scan_files(all_files)

        # Обновляем кэш
        for file_info in scanned:
            self.last_scan_cache[file_info["path"]] = file_info["hash"]

        # Очистка кэша от устаревших записей
        self._cleanup_cache()
        # Сохраняем кэш
        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Полное сканирование завершено за {duration:.2f}s")
        logger.info(f"   Всего файлов для проверки: {len(all_files)}")
        logger.info(f"   Сканировано: {len(scanned)}")

        return {
            "mode": "full",
            "total_files": len(all_files),
            "scanned_files": len(scanned),
            "ignored_files": len(all_files) - len(scanned),
            "duration": duration,
            "files": scanned,
            "timestamp": start_time.isoformat(),
        }

    def scan_paths(self, paths: List[str]) -> Dict[str, Any]:
        """Сканировать только указанные директории/файлы"""
        logger.info(f"🔄 Запуск выборочного сканирования: {paths}")
        start_time = datetime.now()

        target_files = []

        for path_pattern in paths:
            target_path = self.project_path / path_pattern

            if not target_path.exists():
                logger.warning(f"Путь не найден: {path_pattern}")
                continue

            if target_path.is_file():
                target_files.append(target_path)
            elif target_path.is_dir():
                # Рекурсивно добавляем все файлы в директории
                target_files.extend(target_path.rglob("*"))

        # Фильтруем только файлы
        file_list = [f for f in target_files if f.is_file()]

        # Параллельное сканирование
        scanned = self._parallel_scan_files(file_list)

        # Обновляем кэш
        for file_info in scanned:
            self.last_scan_cache[file_info["path"]] = file_info["hash"]
        # Сохраняем кэш
        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Выборочное сканирование завершено за {duration:.2f}s")
        logger.info(f"   Всего файлов для проверки: {len(file_list)}")
        logger.info(f"   Сканировано: {len(scanned)}")

        return {
            "mode": "paths",
            "paths": paths,
            "total_files": len(file_list),
            "scanned_files": len(scanned),
            "duration": duration,
            "files": scanned,
            "timestamp": start_time.isoformat(),
        }

    def export_results(
        self, results: Dict[str, Any], output_file: str, format: str = "json"
    ) -> None:
        """Экспортировать результаты в указанный формат"""
        try:
            if format == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Результаты экспортированы в JSON: {output_file}")

            elif format == "csv":
                import csv

                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["path", "hash", "size", "mtime"])
                    writer.writeheader()
                    for file_info in results.get("files", []):
                        # Конвертируем mtime в читаемый формат, если есть
                        if "mtime" in file_info:
                            file_info["mtime"] = datetime.fromtimestamp(
                                file_info["mtime"]
                            ).isoformat()
                        writer.writerow(file_info)
                logger.info(f"✅ Результаты экспортированы в CSV: {output_file}")

            else:
                logger.error(f"Неподдерживаемый формат экспорта: {format}")
        except (IOError, csv.Error) as e:
            logger.error(f"Ошибка экспорта в {format}: {e}")

    @classmethod
    def load_config(cls, config_file: str) -> ScannerConfig:
        """Загрузить конфигурацию из файла"""
        if not Path(config_file).exists():
            logger.warning(
                f"Файл конфигурации не найден: {config_file}. Используются настройки по умолчанию."
            )
            return ScannerConfig()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return ScannerConfig(**config_data)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return ScannerConfig()


# CLI-интерфейс
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Оптимизированный сканер проекта для Cognitive Agent"
    )
    parser.add_argument("project_path", help="Путь к проекту")
    parser.add_argument(
        "--mode", choices=["full", "git_diff", "paths"], default="full", help="Режим сканирования"
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Пути для выборочного сканирования (используется с --mode paths)",
    )
    parser.add_argument("--config", help="Файл конфигурации сканера")
    parser.add_argument("--export", help="Файл для экспорта результатов")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Формат экспорта")

    args = parser.parse_args()

    # Загрузка конфигурации
    config = ProjectScanner.load_config(args.config) if args.config else ScannerConfig()

    # Создание сканера
    scanner = ProjectScanner(args.project_path, config)

    # Выполнение сканирования
    if args.mode == "full":
        results = scanner.scan_full()
    elif args.mode == "git_diff":
        results = scanner.scan_git_diff()
    else:  # paths
        if not args.paths:
            parser.error("--paths требуется для режима paths")
        results = scanner.scan_paths(args.paths)

    # Экспорт результатов
    if args.export:
        scanner.export_results(results, args.export, args.format)

    # Вывод краткой статистики
    print("\n📊 Статистика сканирования:")
    print(f"Режим: {results['mode']}")
    print(f"Длительность: {results['duration']:.2f} сек")
    if results["mode"] == "full":
        print(f"Всего файлов: {results['total_files']}")
        print(f"Сканировано: {results['scanned_files']}")
        print(f"Игнорировано: {results['ignored_files']}")
    elif results["mode"] == "git_diff":
        print(f"Изменённых файлов: {results['changed_files']}")
        print(f"Сканировано: {results['scanned_files']}")
        print(f"Пропущено: {results['skipped_files']}")
    else:
        print(f"Всего для проверки: {results['total_files']}")
        print(f"Сканировано: {results['scanned_files']}")


if __name__ == "__main__":
    main()
