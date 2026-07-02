#!/usr/bin/env python3
"""
Memory Integrity Checker module for cognitive agent

Проверяет целостность памяти агента:
- Актуальность ChromaDB индекса
- Срок жизни кэша
- Автоматическое снижение автономности при проблемах
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import structlog

if TYPE_CHECKING:
    from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

logger = structlog.get_logger(__name__)


class MemoryIntegrityChecker:
    """
    Проверка целостности памяти агента

    Интегрируется с агентом для проверки:
    - Актуальности ChromaDB индекса
    - Срока жизни кэша
    - Автоматического снижения автономности при проблемах
    """

    def __init__(
        self,
        agent: "AutonomousCognitiveAgent",
        cache_ttl: int = 3600,
        chromadb_max_age_hours: int = 24,
        config_dir: Optional[str] = None,
    ):
        """
        Инициализация MemoryIntegrityChecker.

        Args:
            agent: Ссылка на агента (AutonomousCognitiveAgent)
            cache_ttl: Время жизни кэша в секундах (по умолчанию 1 час)
            chromadb_max_age_hours: Максимальный возраст индекса ChromaDB в часах (по умолчанию 24)
            config_dir: Путь к директории конфигурации (опционально)
        """
        self.agent = agent
        self.cache_ttl = timedelta(seconds=cache_ttl)
        self.chromadb_max_age = timedelta(hours=chromadb_max_age_hours)
        self.config_dir = Path(config_dir) if config_dir else agent.project_path / "config"
        self.last_check: Optional[datetime] = None
        self._integrity_cache: dict[str, Any] = {}

        logger.info(
            "Memory integrity checker initialized",
            agent_id=agent.agent_id,
            cache_ttl=cache_ttl,
            chromadb_max_age_hours=chromadb_max_age_hours,
        )

    def check_integrity(self) -> list[str]:
        """
        Проверить целостность памяти агента.

        Returns:
            Список обнаруженных проблем (пустой если всё OK)
        """
        issues: list[str] = []

        # Проверка ChromaDB
        if not self.check_chromadb_freshness():
            issues.append("ChromaDB index is stale or unavailable")

        # Проверка кэша
        if not self.check_cache_validity():
            issues.append("Cache is expired or corrupted")

        # Проверка файлов конфигурации
        config_issues = self._check_config_files()
        if config_issues:
            issues.extend(config_issues)

        # Если есть проблемы — снизить автономность
        if issues:
            self._degrade_capabilities(issues)

        self.last_check = datetime.now()

        # Логирование через TransparencyLogger
        self._log_transparency(issues)

        logger.info(
            "Memory integrity check completed",
            agent_id=self.agent.agent_id,
            issues_count=len(issues),
            issues=issues,
        )

        return issues

    def check_chromadb_freshness(self) -> bool:
        """
        Проверить актуальность ChromaDB индекса.

        Проверяет:
        - Доступность ChromaDB
        - Время последнего обновления индекса
        - Количество документов в индексе

        Returns:
            True если индекс актуален, False если устарел или недоступен
        """
        if not self.agent._is_chroma_available():
            logger.warning("ChromaDB not available (optional dependency)")
            return False

        try:
            # Инициализация ChromaDB если не инициализирована
            if not self.agent._chromadb_initialized:
                self.agent._init_chromadb()

            if not self.agent.chroma_indexer:
                logger.warning("ChromaDB indexer not initialized")
                return False

            # Проверить статистику индекса
            stats = self.agent.chroma_indexer.get_stats()

            # Проверить время последнего обновления
            last_update = stats.get("last_update", None)

            if last_update is None:
                logger.warning("ChromaDB index has no update timestamp")
                return False

            # Проверить количество документов
            doc_count = stats.get("collection_count", 0)
            if doc_count == 0:
                logger.warning("ChromaDB index is empty")
                return False

            # Проверить возраст индекса
            if isinstance(last_update, datetime):
                index_age = datetime.now() - last_update
                if index_age > self.chromadb_max_age:
                    logger.warning(
                        "ChromaDB index is too old",
                        age_hours=index_age.total_seconds() / 3600,
                        max_age_hours=self.chromadb_max_age.total_seconds() / 3600,
                    )
                    return False

            logger.info(
                "ChromaDB index is fresh",
                doc_count=doc_count,
                last_update=last_update,
            )

            return True

        except Exception as e:
            logger.error(f"ChromaDB freshness check failed: {e}")
            return False

    def check_cache_validity(self) -> bool:
        """
        Проверить срок жизни кэша.

        Проверяет:
        - Существование кэш-директории
        - Время последнего обновления кэша
        - Валидность кэш-файлов

        Returns:
            True если кэш валиден, False если устарел
        """
        try:
            # Путь к кэшу
            cache_dir = self.agent.project_path / ".agent_data" / "cache"

            if not cache_dir.exists():
                logger.warning(f"Cache directory does not exist: {cache_dir}")
                return False

            # Проверить время последнего обновления
            last_cache_file = None
            last_mtime = None

            for cache_file in cache_dir.rglob("*"):
                if cache_file.is_file():
                    mtime = cache_file.stat().st_mtime
                    if last_mtime is None or mtime > last_mtime:
                        last_mtime = mtime
                        last_cache_file = cache_file

            if last_mtime is None:
                logger.warning("Cache directory is empty")
                return False

            # Проверить возраст кэша
            cache_age = datetime.now() - datetime.fromtimestamp(last_mtime)

            if cache_age > self.cache_ttl:
                logger.warning(
                    "Cache is expired",
                    age_seconds=cache_age.total_seconds(),
                    ttl_seconds=self.cache_ttl.total_seconds(),
                    last_file=str(last_cache_file),
                )
                return False

            # Проверить валидность кэш-файлов
            valid_files = 0
            invalid_files = 0

            for cache_file in cache_dir.rglob("*.json"):
                try:
                    with open(cache_file, encoding="utf-8") as f:
                        data = f.read()
                        if data.strip():
                            valid_files += 1
                        else:
                            invalid_files += 1
                            logger.warning(f"Empty cache file: {cache_file}")
                except Exception as e:
                    invalid_files += 1
                    logger.error(f"Invalid cache file {cache_file}: {e}")

            logger.info(
                "Cache validation completed",
                valid_files=valid_files,
                invalid_files=invalid_files,
                total_age_seconds=cache_age.total_seconds(),
            )

            return invalid_files == 0

        except Exception as e:
            logger.error(f"Cache validity check failed: {e}")
            return False

    def _check_config_files(self) -> list[str]:
        """
        Проверить файлы конфигурации.

        Returns:
            Список проблем с конфигурацией
        """
        issues: list[str] = []

        # Проверить наличие guardrails.yaml
        guardrails_path = self.config_dir / "guardrails.yaml"
        if not guardrails_path.exists():
            issues.append("guardrails.yaml not found")

        # Проверить наличие safe_mode.yaml
        safe_mode_path = self.config_dir / "safe_mode.yaml"
        if not safe_mode_path.exists():
            issues.append("safe_mode.yaml not found")

        # Проверить наличие agent-config.yaml
        agent_config_path = self.config_dir / "agent-config.yaml"
        if not agent_config_path.exists():
            issues.append("agent-config.yaml not found")

        return issues

    def _degrade_capabilities(self, issues: list[str]) -> None:
        """
        Снизить автономность агента при обнаружении проблем.

        Args:
            issues: Список обнаруженных проблем
        """
        logger.warning(
            "Memory integrity issues detected, degrading agent capabilities",
            issues=issues,
        )

        # Снизить уровень автономности
        if not hasattr(self.agent, "autonomy_level"):
            self.agent.autonomy_level = "full"

        if self.agent.autonomy_level != "low":
            logger.info("Degrading agent autonomy level to 'low'")
            self.agent.autonomy_level = "low"

        # Включить требование подтверждения
        if not hasattr(self.agent, "require_approval"):
            self.agent.require_approval = False

        if not self.agent.require_approval:
            logger.info("Enabling require_approval due to memory issues")
            self.agent.require_approval = True

        # Логирование
        logger.warning(
            "Agent capabilities degraded",
            agent_id=self.agent.agent_id,
            autonomy_level=self.agent.autonomy_level,
            require_approval=self.agent.require_approval,
            issues_count=len(issues),
            issues=issues,
        )

    def _log_transparency(self, issues: list[str]) -> None:
        """
        Логировать проверку через TransparencyLogger.

        Args:
            issues: Список обнаруженных проблем
        """
        # Проверить наличие TransparencyLogger
        if not hasattr(self.agent, "transparency_logger") or self.agent.transparency_logger is None:
            logger.info("TransparencyLogger not available, skipping integration")
            return

        try:
            action_data = {
                "planned": f"Check memory integrity (cache_ttl={self.cache_ttl}, chromadb_max_age={self.chromadb_max_age})",
                "executed": f"Checked memory integrity, found {len(issues)} issues",
                "status": "warning" if issues else "success",
                "confidence": 1.0,
                "user_approval": False,
            }

            self.agent.transparency_logger.log_action(action_data)

            # Логировать каждую проблему
            for issue in issues:
                action_data = {
                    "planned": "No issues expected",
                    "executed": issue,
                    "status": "warning",
                    "confidence": 0.8,
                    "user_approval": False,
                }
                self.agent.transparency_logger.log_action(action_data)
        except Exception as e:
            logger.warning(f"Failed to log transparency: {e}")

    def get_status(self) -> dict[str, Any]:
        """
        Получить статус проверки целостности памяти.

        Returns:
            Словарь с информацией о состоянии
        """
        return {
            "agent_id": self.agent.agent_id,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "cache_ttl_seconds": self.cache_ttl.total_seconds(),
            "chromadb_max_age_hours": self.chromadb_max_age.total_seconds() / 3600,
            "autonomy_level": getattr(self.agent, "autonomy_level", "full"),
            "require_approval": getattr(self.agent, "require_approval", False),
        }
