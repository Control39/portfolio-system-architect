"""
Оптимизированный сканер проекта для Cognitive Agent

Функции:
1. Уважение .gitignore (исключение node_modules, .venv, __pycache__ и т.д.)
2. Git diff режим: сканировать только изменённые файлы
3. Инкрементальное сканирование по хэшам
4. Выборочное сканирование по директориям

Использование:
    # Полный скан (с игнорированием .gitignore)
    scan = ProjectScanner("C:/repo")
    results = scan.scan_full()

    # Git diff скан (только изменённые файлы)
    results = scan.scan_git_diff()

    # Скан конкретных директорий
    results = scan.scan_paths(["apps/cognitive_agent", ".agents"])
"""

import os
import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

try:
    import pathspec

    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "pathspec не установлен. .gitignore игнорируется. Установите: pip install pathspec"
    )

logger = logging.getLogger(__name__)


class ProjectScanner:
    """Оптимизированный сканер проекта"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.gitignore_spec = None
        self.last_scan_cache: Dict[str, str] = {}
        self.cache_file = self.project_path / ".cognitive_agent_scan_cache.json"

        # Загрузка .gitignore
        self._load_gitignore()

        # Загрузка кэша
        self._load_cache()

    def _load_gitignore(self):
        """Загрузить правила .gitignore"""
        if not HAS_PATHSPEC:
            return

        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                patterns = f.read().splitlines()

            # Фильтрация пустых строк и комментариев
            patterns = [p.strip() for p in patterns if p.strip() and not p.startswith("#")]

            try:
                self.gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
                logger.info(f"✅ Загружено {len(patterns)} правил из .gitignore")
            except Exception as e:
                logger.error(f"Ошибка загрузки .gitignore: {e}")
        else:
            logger.warning(".gitignore не найден")

    def _load_cache(self):
        """Загрузить кэш хэшей файлов"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.last_scan_cache = json.load(f)
                logger.info(f"✅ Кэш загружен: {len(self.last_scan_cache)} файлов")
            except Exception as e:
                logger.error(f"Ошибка загрузки кэша: {e}")
                self.last_scan_cache = {}

    def _save_cache(self):
        """Сохранить кэш хэшей"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.last_scan_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычислить MD5 хэш файла"""
        try:
            hash_md5 = hashlib.md5(usedforsecurity=False)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Не удалось вычислить хэш {file_path}: {e}")
            return ""

    def _is_ignored(self, path: Path) -> bool:
        """Проверить, игнорируется ли файл через .gitignore"""
        if not self.gitignore_spec:
            return False

        rel_path = path.relative_to(self.project_path)
        rel_path_str = str(rel_path).replace("\\", "/")

        return self.gitignore_spec.match_file(rel_path_str)

    def _get_changed_files(self) -> List[Path]:
        """Получить список изменённых файлов через git diff"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.warning(f"Git diff failed: {result.stderr}")
                return []

            changed = [Path(p) for p in result.stdout.strip().split("\n") if p.strip()]
            logger.info(f"🔍 Найдено {len(changed)} изменённых файлов")
            return changed
        except Exception as e:
            logger.error(f"Ошибка git diff: {e}")
            return []

    def _get_staged_files(self) -> List[Path]:
        """Получить список зафиксированных файлов"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            staged = [Path(p) for p in result.stdout.strip().split("\n") if p.strip()]
            logger.info(f"🔍 Найдено {len(staged)} staged файлов")
            return staged
        except Exception as e:
            logger.error(f"Ошибка git diff --cached: {e}")
            return []

    def scan_git_diff(self) -> Dict[str, Any]:
        """Сканировать только изменённые файлы (git diff)"""
        logger.info("🔄 Запуск инкрементального сканирования (git diff)...")
        start_time = datetime.now()

        # Получаем изменённые файлы
        changed_files = self._get_changed_files()
        staged_files = self._get_staged_files()

        # Объединяем списки
        all_changed = list(set(changed_files + staged_files))

        if not all_changed:
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

        scanned = []
        for file_path in all_changed:
            full_path = self.project_path / file_path

            if not full_path.exists():
                continue

            if not full_path.is_file():
                continue

            # Проверка .gitignore
            if self._is_ignored(full_path):
                logger.debug(f"⏭️  Игнорируется: {file_path}")
                continue

            # Вычисляем хэш
            current_hash = self._calculate_file_hash(full_path)
            last_hash = self.last_scan_cache.get(str(file_path))

            if current_hash == last_hash:
                logger.debug(f"⏭️  Без изменений: {file_path}")
                continue

            # Файл изменился — сканируем
            scanned.append(
                {
                    "path": str(file_path),
                    "hash": current_hash,
                    "size": full_path.stat().st_size,
                    "status": "modified" if file_path in changed_files else "staged",
                }
            )

            # Обновляем кэш
            self.last_scan_cache[str(file_path)] = current_hash

        # Сохраняем кэш
        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Сканирование завершено за {duration:.2f}s")
        logger.info(f"   Изменённых файлов: {len(all_changed)}")
        logger.info(f"   Сканировано: {len(scanned)}")
        logger.info(f"   Пропущено (без изменений): {len(all_changed) - len(scanned)}")

        return {
            "mode": "git_diff",
            "changed_files": len(all_changed),
            "scanned_files": len(scanned),
            "skipped_files": len(all_changed) - len(scanned),
            "duration": duration,
            "files": scanned,
            "timestamp": start_time.isoformat(),
        }

    def scan_full(self) -> Dict[str, Any]:
        """Полное сканирование проекта (с уважением .gitignore)"""
        logger.info("🔄 Запуск полного сканирования проекта...")
        start_time = datetime.now()

        total_files = 0
        scanned_files = 0
        ignored_files = 0
        file_details = []

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)

            # Проверка директории на игнорирование
            if self._is_ignored(root_path):
                dirs.clear()  # Не спускаться в игнорируемые директории
                ignored_files += len(files)
                continue

            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(self.project_path)
                rel_path_str = str(rel_path).replace("\\", "/")

                total_files += 1

                # Проверка .gitignore
                if self._is_ignored(file_path):
                    ignored_files += 1
                    continue

                # Вычисляем хэш
                current_hash = self._calculate_file_hash(file_path)
                last_hash = self.last_scan_cache.get(str(rel_path))

                # Обновляем кэш
                self.last_scan_cache[str(rel_path)] = current_hash

                # Добавляем в результаты
                file_details.append(
                    {"path": rel_path_str, "hash": current_hash, "size": file_path.stat().st_size}
                )

                scanned_files += 1

        # Сохраняем кэш
        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Полное сканирование завершено за {duration:.2f}s")
        logger.info(f"   Всего файлов: {total_files}")
        logger.info(f"   Сканировано: {scanned_files}")
        logger.info(f"   Игнорировано: {ignored_files}")

        return {
            "mode": "full",
            "total_files": total_files,
            "scanned_files": scanned_files,
            "ignored_files": ignored_files,
            "duration": duration,
            "files": file_details,
            "timestamp": start_time.isoformat(),
        }

    def scan_paths(self, paths: List[str]) -> Dict[str, Any]:
        """Сканировать только указанные директории/файлы"""
        logger.info(f"🔄 Запуск выборочного сканирования: {paths}")
        start_time = datetime.now()

        scanned_files = 0
        file_details = []

        for path_pattern in paths:
            target_path = self.project_path / path_pattern

            if not target_path.exists():
                logger.warning(f"Путь не найден: {path_pattern}")
                continue

            if target_path.is_file():
                # Одиночный файл
                if not self._is_ignored(target_path):
                    current_hash = self._calculate_file_hash(target_path)
                    file_details.append(
                        {
                            "path": str(target_path.relative_to(self.project_path)),
                            "hash": current_hash,
                            "size": target_path.stat().st_size,
                        }
                    )
                    scanned_files += 1
            elif target_path.is_dir():
                # Директория
                for file_path in target_path.rglob("*"):
                    if file_path.is_file() and not self._is_ignored(file_path):
                        current_hash = self._calculate_file_hash(file_path)
                        rel_path = file_path.relative_to(self.project_path)
                        file_details.append(
                            {
                                "path": str(rel_path),
                                "hash": current_hash,
                                "size": file_path.stat().st_size,
                            }
                        )
                        scanned_files += 1

        self._save_cache()

        duration = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Выборочное сканирование завершено за {duration:.2f}s")
        logger.info(f"   Сканировано файлов: {scanned_files}")

        return {
            "mode": "paths",
            "paths": paths,
            "scanned_files": scanned_files,
            "duration": duration,
            "files": file_details,
            "timestamp": start_time.isoformat(),
        }
