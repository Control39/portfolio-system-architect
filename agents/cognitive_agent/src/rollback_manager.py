#!/usr/bin/env python3
"""
Rollback Manager module for cognitive agent

Менеджер отката изменений через снимки файлов.

Ключевые принципы:
- Создание снимков перед изменением файлов
- Возможность отката к любому снимку
- Хранение снимков в .agent_data/snapshots/
- Интеграция с TransparencyLogger для прозрачности
- Автоматическая очистка старых снимков
"""

import json
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class RollbackManager:
    """
    Менеджер отката изменений через снимки файлов

    Использование:
        manager = RollbackManager(transparency_logger=logger)

        # Создать снимок перед изменением
        snapshot_id = manager.create_snapshot("config.yaml", "Before config change")

        # Изменить файл
        Path("config.yaml").write_text("new content")

        # Откатиться при проблеме
        manager.rollback(snapshot_id)
    """

    def __init__(self, transparency_logger: Any = None):
        """
        Инициализация RollbackManager.

        Args:
            transparency_logger: Экземпляр TransparencyLogger для логирования (опционально)
        """
        self.snapshots: dict[str, dict[str, Any]] = {}
        self.snapshots_dir = Path(".agent_data/snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.transparency_logger = transparency_logger

        logger.info(
            "RollbackManager initialized",
            snapshots_dir=str(self.snapshots_dir),
        )

    def create_snapshot(self, file_path: str, description: str = "") -> str:
        """
        Создать снимок файла.

        Args:
            file_path: Путь к файлу
            description: Описание снимка (опционально)

        Returns:
            ID созданного снимка

        Raises:
            FileNotFoundError: Если файл не найден
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        snapshot_id = str(uuid.uuid4())
        snapshot_dir = self.snapshots_dir / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Скопировать файл
        saved_file = snapshot_dir / path.name
        shutil.copy2(path, saved_file)

        # Сохранить метаданные
        metadata = {
            "id": snapshot_id,
            "file_path": str(path.resolve()),
            "file_name": path.name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "file_size": path.stat().st_size,
            "snapshot_file": str(saved_file),
        }

        metadata_file = snapshot_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        self.snapshots[snapshot_id] = metadata

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": f"Snapshot of {file_path}",
                    "executed": f"Snapshot {snapshot_id} created",
                    "status": "executed",
                    "confidence": 1.0,
                    "user_approval": False,
                }
            )

        logger.info(
            "Snapshot created",
            snapshot_id=snapshot_id,
            file_path=file_path,
            file_size=metadata["file_size"],
        )

        return snapshot_id

    def create_snapshot_dir(self, dir_path: str, description: str = "") -> str:
        """
        Создать снимок директории (рекурсивно).

        Args:
            dir_path: Путь к директории
            description: Описание снимка (опционально)

        Returns:
            ID созданного снимка

        Raises:
            FileNotFoundError: Если директория не найдена
        """
        path = Path(dir_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")

        snapshot_id = str(uuid.uuid4())
        snapshot_dir = self.snapshots_dir / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Скопировать директорию рекурсивно
        snapshot_target = snapshot_dir / path.name
        shutil.copytree(path, snapshot_target)

        # Подсчитать общее количество файлов и размер
        file_count = 0
        total_size = 0
        for f in path.rglob("*"):
            if f.is_file():
                file_count += 1
                total_size += f.stat().st_size

        # Сохранить метаданные
        metadata = {
            "id": snapshot_id,
            "dir_path": str(path.resolve()),
            "dir_name": path.name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "file_count": file_count,
            "total_size": total_size,
            "snapshot_dir": str(snapshot_dir),
        }

        metadata_file = snapshot_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        self.snapshots[snapshot_id] = metadata

        # Логирование через TransparencyLogger
        if self.transparency_logger:
            self.transparency_logger.log_action(
                {
                    "planned": f"Snapshot of directory {dir_path}",
                    "executed": f"Snapshot {snapshot_id} created",
                    "status": "executed",
                    "confidence": 1.0,
                    "user_approval": False,
                }
            )

        logger.info(
            "Directory snapshot created",
            snapshot_id=snapshot_id,
            dir_path=dir_path,
            file_count=file_count,
            total_size=total_size,
        )

        return snapshot_id

    def rollback(self, snapshot_id: str) -> bool:
        """
        Откатить файл к снимку.

        Args:
            snapshot_id: ID снимка

        Returns:
            True если откат успешен, False если не найдено
        """
        if snapshot_id not in self.snapshots:
            # Попробовать загрузить из файла
            self._load_snapshot(snapshot_id)

        if snapshot_id not in self.snapshots:
            logger.warning("Snapshot not found", snapshot_id=snapshot_id)
            return False

        metadata = self.snapshots[snapshot_id]
        original_path = Path(metadata["file_path"])
        snapshot_file = Path(metadata["snapshot_file"])

        if not snapshot_file.exists():
            logger.warning("Snapshot file not found", snapshot_file=str(snapshot_file))
            return False

        # Восстановить файл
        try:
            shutil.copy2(snapshot_file, original_path)

            # Логирование через TransparencyLogger
            if self.transparency_logger:
                self.transparency_logger.log_action(
                    {
                        "planned": f"Rollback {metadata['file_name']}",
                        "executed": f"Rolled back to snapshot {snapshot_id}",
                        "status": "executed",
                        "confidence": 1.0,
                        "user_approval": False,
                    }
                )

            logger.info(
                "Rollback completed",
                snapshot_id=snapshot_id,
                file_path=str(original_path),
            )

            return True
        except Exception as e:
            logger.error("Rollback failed", snapshot_id=snapshot_id, error=str(e))
            return False

    def list_snapshots(self, file_path: str = None) -> list[dict[str, Any]]:
        """
        Список снимков (опционально фильтр по файлу).

        Args:
            file_path: Путь к файлу для фильтрации (опционально)

        Returns:
            Список снимков
        """
        if file_path:
            resolved_path = str(Path(file_path).resolve())
            return [s for s in self.snapshots.values() if s["file_path"] == resolved_path]
        return list(self.snapshots.values())

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        """
        Получить информацию о снимке.

        Args:
            snapshot_id: ID снимка

        Returns:
            Данные снимка или None если не найдено
        """
        if snapshot_id not in self.snapshots:
            self._load_snapshot(snapshot_id)
        return self.snapshots.get(snapshot_id)

    def cleanup_old_snapshots(self, max_age_hours: int = 24) -> int:
        """
        Удалить старые снимки.

        Args:
            max_age_hours: Максимальный возраст снимка в часах

        Returns:
            Количество удалённых снимков
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0

        for snapshot_id, metadata in list(self.snapshots.items()):
            created_at = datetime.fromisoformat(metadata["created_at"])
            if created_at < cutoff:
                snapshot_dir = self.snapshots_dir / snapshot_id
                if snapshot_dir.exists():
                    shutil.rmtree(snapshot_dir)
                del self.snapshots[snapshot_id]
                removed += 1
                logger.info(
                    "Old snapshot removed",
                    snapshot_id=snapshot_id,
                    created_at=metadata["created_at"],
                )

        logger.info(
            "Cleanup completed",
            removed=removed,
            max_age_hours=max_age_hours,
        )

        return removed

    def _load_snapshot(self, snapshot_id: str) -> None:
        """
        Загрузить снимок из файла.

        Args:
            snapshot_id: ID снимка
        """
        snapshot_dir = self.snapshots_dir / snapshot_id
        metadata_file = snapshot_dir / "metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                self.snapshots[snapshot_id] = metadata
                logger.debug(
                    "Snapshot loaded from file",
                    snapshot_id=snapshot_id,
                )
            except Exception as e:
                logger.error(
                    "Failed to load snapshot",
                    snapshot_id=snapshot_id,
                    error=str(e),
                )
        else:
            logger.warning(
                "Snapshot file not found",
                snapshot_id=snapshot_id,
                file_path=str(metadata_file),
            )

    def get_snapshot_file(self, snapshot_id: str) -> Optional[Path]:
        """
        Получить путь к файлу снимка.

        Args:
            snapshot_id: ID снимка

        Returns:
            Path к файлу или None если не найдено
        """
        metadata = self.get_snapshot(snapshot_id)
        if not metadata:
            return None

        return Path(metadata["snapshot_file"])

    def get_stats(self) -> dict[str, Any]:
        """
        Получить статистику снимков.

        Returns:
            Словарь со статистикой
        """
        total = len(self.snapshots)

        # Подсчитать общий размер
        total_size = 0
        for metadata in self.snapshots.values():
            total_size += metadata.get("file_size", 0)

        return {
            "total": total,
            "total_size": total_size,
            "snapshots_dir": str(self.snapshots_dir),
        }
