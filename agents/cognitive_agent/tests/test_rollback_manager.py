"""Тесты RollbackManager (src/rollback_manager.py)

Service Tier: UNIT
Purpose: Unit testing for RollbackManager class
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from agents.cognitive_agent.src.rollback_manager import RollbackManager


class TestRollbackManagerInitialization:
    """Тесты инициализации RollbackManager"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        manager = RollbackManager()

        assert len(manager.snapshots) == 0
        assert manager.snapshots_dir.exists()
        assert manager.snapshots_dir == Path(".agent_data/snapshots")

    def test_initialization_with_transparency_logger(self):
        """Тест инициализации с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        manager = RollbackManager(transparency_logger=logger)

        assert manager.transparency_logger == logger


class TestRollbackManagerCreateSnapshot:
    """Тесты метода create_snapshot"""

    def test_create_snapshot_returns_id(self):
        """Тест, что create_snapshot возвращает ID"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("original content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test snapshot")

            assert snapshot_id is not None
            assert isinstance(snapshot_id, str)
            assert len(snapshot_id) > 0
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_create_snapshot_saves_file(self):
        """Тест, что create_snapshot сохраняет файл"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("original content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test snapshot")

            # Проверить, что снимок сохранён
            assert snapshot_id in manager.snapshots

            snapshot_dir = manager.snapshots_dir / snapshot_id
            assert snapshot_dir.exists()

            metadata_file = snapshot_dir / "metadata.json"
            assert metadata_file.exists()
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_create_snapshot_file_content(self):
        """Тест содержимого снимка"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("original content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test snapshot")

            # Загрузить метаданные
            metadata = manager.snapshots[snapshot_id]

            assert metadata["id"] == snapshot_id
            assert metadata["file_name"] == Path(test_file).name
            assert metadata["description"] == "Test snapshot"
            assert metadata["file_size"] == len("original content")
            assert "snapshot_file" in metadata
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_create_snapshot_nonexistent_file(self):
        """Тест create_snapshot с несуществующим файлом"""
        manager = RollbackManager()

        with pytest.raises(FileNotFoundError) as exc_info:
            manager.create_snapshot("nonexistent_file.txt", "Test")

        assert "File not found" in str(exc_info.value)


class TestRollbackManagerRollback:
    """Тесты метода rollback"""

    def test_rollback_restores_content(self):
        """Тест, что rollback восстанавливает содержимое"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("original content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Before modification")

            # Изменить файл
            Path(test_file).write_text("modified content")
            assert Path(test_file).read_text() == "modified content"

            # Откатиться
            rolled_back = manager.rollback(snapshot_id)

            assert rolled_back is True
            assert Path(test_file).read_text() == "original content"
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_rollback_nonexistent_id(self):
        """Тест rollback с несуществующим ID"""
        manager = RollbackManager()

        rolled_back = manager.rollback("non-existent-id")

        assert rolled_back is False

    def test_rollback_nonexistent_snapshot_file(self):
        """Тест rollback с отсутствующим файлом снимка"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("original")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test")

            # Удалить файл снимка
            metadata = manager.snapshots[snapshot_id]
            snapshot_file = Path(metadata["snapshot_file"])
            snapshot_file.unlink()

            rolled_back = manager.rollback(snapshot_id)

            assert rolled_back is False
        finally:
            Path(test_file).unlink(missing_ok=True)


class TestRollbackManagerListSnapshots:
    """Тесты метода list_snapshots"""

    def test_list_snapshots_empty(self):
        """Тест list_snapshots с пустыми снимками"""
        manager = RollbackManager()

        snapshots = manager.list_snapshots()

        assert snapshots == []

    def test_list_snapshots_with_filter(self):
        """Тест list_snapshots с фильтрацией"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f1:
            f1.write("file1")
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f2:
            f2.write("file2")
            file2 = f2.name

        try:
            sid1 = manager.create_snapshot(file1, "Snapshot 1")
            sid2 = manager.create_snapshot(file2, "Snapshot 2")

            # Фильтровать по файлу
            snapshots_for_file1 = manager.list_snapshots(file1)
            snapshots_for_file2 = manager.list_snapshots(file2)

            assert len(snapshots_for_file1) == 1
            assert snapshots_for_file1[0]["id"] == sid1
            assert len(snapshots_for_file2) == 1
            assert snapshots_for_file2[0]["id"] == sid2
        finally:
            Path(file1).unlink(missing_ok=True)
            Path(file2).unlink(missing_ok=True)


class TestRollbackManagerGetSnapshot:
    """Тесты метода get_snapshot"""

    def test_get_snapshot_exists(self):
        """Тест get_snapshot с существующим ID"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test")

            snapshot = manager.get_snapshot(snapshot_id)

            assert snapshot is not None
            assert snapshot["id"] == snapshot_id
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_get_snapshot_not_found(self):
        """Тест get_snapshot с несуществующим ID"""
        manager = RollbackManager()

        snapshot = manager.get_snapshot("non-existent-id")

        assert snapshot is None


class TestRollbackManagerCleanup:
    """Тесты метода cleanup_old_snapshots"""

    def test_cleanup_no_old_snapshots(self):
        """Тест cleanup с новыми снимками"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "New snapshot")

            removed = manager.cleanup_old_snapshots(max_age_hours=24)

            assert removed == 0
            assert snapshot_id in manager.snapshots
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_cleanup_old_snapshots(self):
        """Тест cleanup со старыми снимками"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Old snapshot")

            # Изменить время создания в метаданных
            metadata = manager.snapshots[snapshot_id]
            old_time = (datetime.now() - timedelta(hours=48)).isoformat()
            metadata["created_at"] = old_time

            removed = manager.cleanup_old_snapshots(max_age_hours=24)

            assert removed == 1
            assert snapshot_id not in manager.snapshots
        finally:
            Path(test_file).unlink(missing_ok=True)


class TestRollbackManagerDirectorySnapshot:
    """Тесты метода create_snapshot_dir"""

    def test_create_snapshot_dir_returns_id(self):
        """Тест, что create_snapshot_dir возвращает ID"""
        manager = RollbackManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Создать файл в директории
            Path(tmpdir, "file1.txt").write_text("content1")
            Path(tmpdir, "file2.txt").write_text("content2")

            snapshot_id = manager.create_snapshot_dir(tmpdir, "Dir snapshot")

            assert snapshot_id is not None
            assert isinstance(snapshot_id, str)

    def test_create_snapshot_dir_nonexistent(self):
        """Тест create_snapshot_dir с несуществующей директорией"""
        manager = RollbackManager()

        with pytest.raises(FileNotFoundError):
            manager.create_snapshot_dir("nonexistent_dir", "Test")

    def test_create_snapshot_dir_not_directory(self):
        """Тест create_snapshot_dir с файлом вместо директории"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                manager.create_snapshot_dir(test_file, "Test")

            assert "not a directory" in str(exc_info.value)
        finally:
            Path(test_file).unlink(missing_ok=True)


class TestRollbackManagerGetters:
    """Тесты методов получения"""

    def test_get_snapshot_file(self):
        """Тест get_snapshot_file"""
        manager = RollbackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test")

            snapshot_file = manager.get_snapshot_file(snapshot_id)

            assert snapshot_file is not None
            assert snapshot_file.exists()
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_get_stats(self):
        """Тест get_stats"""
        manager = RollbackManager()

        stats = manager.get_stats()

        assert "total" in stats
        assert "total_size" in stats
        assert "snapshots_dir" in stats


class TestRollbackManagerIntegration:
    """Тесты интеграции с TransparencyLogger"""

    def test_transparency_logger_integration(self):
        """Тест интеграции с TransparencyLogger"""
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        logger = TransparencyLogger(agent_id="test-agent")
        manager = RollbackManager(transparency_logger=logger)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content")
            test_file = f.name

        try:
            snapshot_id = manager.create_snapshot(test_file, "Test")

            # Проверить статус прозрачности
            status = logger.get_status()
            assert status["total_actions"] > 0
        finally:
            Path(test_file).unlink(missing_ok=True)


class TestRollbackManagerFilePaths:
    """Тесты работы с путями"""

    def test_snapshots_dir_path(self):
        """Тест snapshots_dir"""
        manager = RollbackManager()

        assert manager.snapshots_dir == Path(".agent_data/snapshots")
        assert manager.snapshots_dir.exists()
