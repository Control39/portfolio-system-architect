"""Тесты MemoryIntegrityChecker (src/memory_integrity.py)

Service Tier: UNIT
Purpose: Unit testing for MemoryIntegrityChecker class
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.cognitive_agent.src.memory_integrity import MemoryIntegrityChecker


class MockAgent:
    """Мок агента для тестов"""

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.agent_id = "test-agent"
        self._chromadb_initialized = False
        self._chromadb_client = None
        self.chroma_indexer = None
        self.autonomy_level = "full"
        self.require_approval = False
        self.transparency_logger = None

        # Создать директорию .agent_data/cache
        self._agent_data_dir = self.project_path / ".agent_data" / "cache"
        self._agent_data_dir.mkdir(parents=True, exist_ok=True)

    def _is_chroma_available(self) -> bool:
        return True

    def _init_chromadb(self):
        self._chromadb_initialized = True


class MockChromaIndexer:
    """Мок ChromaDB индексера"""

    def __init__(self, doc_count: int = 100, last_update: datetime = None):
        self.doc_count = doc_count
        self.last_update = last_update or datetime.now()

    def get_stats(self) -> dict:
        return {
            "collection_count": self.doc_count,
            "last_update": self.last_update,
        }


class TestMemoryIntegrityCheckerInitialization:
    """Тесты инициализации MemoryIntegrityChecker"""

    def test_initialization_with_defaults(self):
        """Тест инициализации с дефолтными параметрами"""
        agent = MockAgent()

        checker = MemoryIntegrityChecker(agent)

        assert checker.agent == agent
        assert checker.cache_ttl.total_seconds() == 3600
        assert checker.chromadb_max_age.total_seconds() == 24 * 3600
        assert checker.last_check is None

    def test_initialization_with_custom_ttl(self):
        """Тест инициализации с кастомным cache_ttl"""
        agent = MockAgent()

        checker = MemoryIntegrityChecker(agent, cache_ttl=7200)

        assert checker.cache_ttl.total_seconds() == 7200

    def test_initialization_with_custom_config_dir(self):
        """Тест инициализации с кастомным config_dir"""
        agent = MockAgent()

        with tempfile.TemporaryDirectory() as tmpdir:
            checker = MemoryIntegrityChecker(agent, config_dir=tmpdir)

            assert checker.config_dir == Path(tmpdir)


class TestMemoryIntegrityCheckerCheckIntegrity:
    """Тесты метода check_integrity"""

    def test_check_integrity_no_issues(self):
        """Тест check_integrity без проблем"""
        agent = MockAgent()

        # Инициализировать TransparencyLogger
        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        agent.transparency_logger = TransparencyLogger(agent_id=agent.agent_id)

        # Мокать ChromaDB и кэш
        with patch.object(agent, "_is_chroma_available", return_value=True):
            with patch.object(agent, "_init_chromadb"):
                agent.chroma_indexer = MockChromaIndexer(
                    doc_count=100,
                    last_update=datetime.now() - timedelta(hours=1),
                )

                # Создать валидный кэш-файл
                cache_file = agent._agent_data_dir / "test_cache.json"
                cache_file.write_text('{"data": "test"}')

                checker = MemoryIntegrityChecker(agent, cache_ttl=3600)

                issues = checker.check_integrity()

                assert len(issues) == 0
                assert checker.last_check is not None

    def test_check_integrity_with_chromadb_issues(self):
        """Тест check_integrity с проблемами ChromaDB"""
        agent = MockAgent()
        agent.transparency_logger = None  # Явно установить в None

        # Мокать ChromaDB недоступной
        with patch.object(agent, "_is_chroma_available", return_value=False):
            checker = MemoryIntegrityChecker(agent)

            issues = checker.check_integrity()

            assert len(issues) > 0
            assert any("ChromaDB" in issue for issue in issues)

    def test_check_integrity_with_cache_issues(self):
        """Тест check_integrity с проблемами кэша"""
        agent = MockAgent()
        agent.transparency_logger = None  # Явно установить в None

        # Мокать ChromaDB доступной
        with patch.object(agent, "_is_chroma_available", return_value=True):
            agent.chroma_indexer = MockChromaIndexer(
                doc_count=100,
                last_update=datetime.now() - timedelta(hours=1),
            )

            # Кэш-директория пустая
            if agent._agent_data_dir.exists():
                for f in agent._agent_data_dir.glob("*"):
                    f.unlink()

            checker = MemoryIntegrityChecker(agent, cache_ttl=3600)

            issues = checker.check_integrity()

            assert len(issues) > 0
            assert any("Cache" in issue for issue in issues)


class TestMemoryIntegrityCheckerCheckChromaDbFreshness:
    """Тесты метода check_chromadb_freshness"""

    def test_check_chromadb_freshness_success(self):
        """Тест check_chromadb_freshness успешный случай"""
        agent = MockAgent()

        with patch.object(agent, "_is_chroma_available", return_value=True):
            agent.chroma_indexer = MockChromaIndexer(
                doc_count=100,
                last_update=datetime.now() - timedelta(hours=1),
            )

            checker = MemoryIntegrityChecker(agent)

            result = checker.check_chromadb_freshness()

            assert result is True

    def test_check_chromadb_freshness_stale(self):
        """Тест check_chromadb_freshness с устаревшим индексом"""
        agent = MockAgent()

        with patch.object(agent, "_is_chroma_available", return_value=True):
            agent.chroma_indexer = MockChromaIndexer(
                doc_count=100,
                last_update=datetime.now() - timedelta(days=2),  # Старше 24 часов
            )

            checker = MemoryIntegrityChecker(agent)

            result = checker.check_chromadb_freshness()

            assert result is False

    def test_check_chromadb_freshness_empty(self):
        """Тест check_chromadb_freshness с пустым индексом"""
        agent = MockAgent()

        with patch.object(agent, "_is_chroma_available", return_value=True):
            agent.chroma_indexer = MockChromaIndexer(
                doc_count=0,  # Пустой индекс
                last_update=datetime.now(),
            )

            checker = MemoryIntegrityChecker(agent)

            result = checker.check_chromadb_freshness()

            assert result is False

    def test_check_chromadb_freshness_not_available(self):
        """Тест check_chromadb_freshness когда ChromaDB недоступна"""
        agent = MockAgent()

        with patch.object(agent, "_is_chroma_available", return_value=False):
            checker = MemoryIntegrityChecker(agent)

            result = checker.check_chromadb_freshness()

            assert result is False


class TestMemoryIntegrityCheckerCheckCacheValidity:
    """Тесты метода check_cache_validity"""

    def test_check_cache_validity_success(self):
        """Тест check_cache_validity успешный случай"""
        agent = MockAgent()

        # Создать валидный кэш-файл
        cache_file = agent._agent_data_dir / "test_cache.json"
        cache_file.write_text('{"data": "test"}')

        checker = MemoryIntegrityChecker(agent, cache_ttl=3600)

        result = checker.check_cache_validity()

        assert result is True

    def test_check_cache_validity_expired(self):
        """Тест check_cache_validity с устаревшим кэшем"""
        agent = MockAgent()

        # Создать кэш-файл
        cache_file = agent._agent_data_dir / "test_cache.json"
        cache_file.write_text('{"data": "test"}')

        # Изменить время модификации
        old_time = datetime.now().timestamp() - 7200  # 2 часа назад
        import os

        os.utime(cache_file, (old_time, old_time))

        checker = MemoryIntegrityChecker(agent, cache_ttl=3600)

        result = checker.check_cache_validity()

        assert result is False

    def test_check_cache_validity_empty(self):
        """Тест check_cache_validity с пустым кэшем"""
        agent = MockAgent()

        # Удалить все файлы
        for f in agent._agent_data_dir.glob("*"):
            f.unlink()

        checker = MemoryIntegrityChecker(agent, cache_ttl=3600)

        result = checker.check_cache_validity()

        assert result is False


class TestMemoryIntegrityCheckerDegradeCapabilities:
    """Тесты метода degrade_capabilities"""

    def test_degrade_capabilities(self):
        """Тест degrade_capabilities"""
        agent = MockAgent()

        checker = MemoryIntegrityChecker(agent)

        issues = ["Test issue 1", "Test issue 2"]

        checker._degrade_capabilities(issues)

        assert agent.autonomy_level == "low"
        assert agent.require_approval is True


class TestMemoryIntegrityCheckerConfigCheck:
    """Тесты проверки конфигурации"""

    def test_check_config_files_success(self):
        """Тест _check_config_files успешный случай"""
        agent = MockAgent()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Создать файлы конфигурации
            (config_dir / "guardrails.yaml").write_text("{}")
            (config_dir / "safe_mode.yaml").write_text("{}")
            (config_dir / "agent-config.yaml").write_text("{}")

            checker = MemoryIntegrityChecker(agent, config_dir=str(config_dir))

            issues = checker._check_config_files()

            assert len(issues) == 0

    def test_check_config_files_missing(self):
        """Тест _check_config_files с отсутствующими файлами"""
        agent = MockAgent()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Создать только один файл
            (config_dir / "guardrails.yaml").write_text("{}")

            checker = MemoryIntegrityChecker(agent, config_dir=str(config_dir))

            issues = checker._check_config_files()

            assert len(issues) == 2  # Отсутствуют safe_mode.yaml и agent-config.yaml
            assert any("safe_mode.yaml" in issue for issue in issues)
            assert any("agent-config.yaml" in issue for issue in issues)


class TestMemoryIntegrityCheckerGetStatus:
    """Тесты метода get_status"""

    def test_get_status(self):
        """Тест get_status"""
        agent = MockAgent()

        checker = MemoryIntegrityChecker(agent)

        status = checker.get_status()

        assert status["agent_id"] == "test-agent"
        assert status["last_check"] is None
        assert status["cache_ttl_seconds"] == 3600
        assert status["autonomy_level"] == "full"
        assert status["require_approval"] is False


class TestMemoryIntegrityCheckerIntegration:
    """Тесты интеграции с TransparencyLogger"""

    def test_transparency_logger_integration(self):
        """Тест интеграции с TransparencyLogger"""
        agent = MockAgent()

        from agents.cognitive_agent.src.transparency_logger import TransparencyLogger

        agent.transparency_logger = TransparencyLogger(agent_id=agent.agent_id)

        # Мокать ChromaDB недоступной
        with patch.object(agent, "_is_chroma_available", return_value=False):
            checker = MemoryIntegrityChecker(agent)

            issues = checker.check_integrity()

            assert len(issues) > 0

            # Проверить статус прозрачности
            status = agent.transparency_logger.get_status()
            assert status["total_actions"] > 0
