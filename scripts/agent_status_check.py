#!/usr/bin/env python3
"""
Модуль проверки статуса Cognitive Agent
"""

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from pydantic import BaseModel

# Добавляем корень репозитория в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Импортируем enterprise версию агента

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgentStatus(BaseModel):
    """Модель статуса агента"""
    agent_id: str
    running: bool
    project_path: str
    last_scan: Optional[str]
    scan_interval_seconds: int
    ai_provider: Optional[str]
    ai_providers_status: Dict[str, Any]
    total_scans: int
    total_recommendations: int
    guardrails_loaded: bool
    ai_calls_today: int
    memory_success_rate: float
    operation_limits: Dict[str, Any]
    ai_call_timeout: int
    audit_log_path: Optional[str]
    chroma_available: bool
    job_agent_available: bool
    enterprise_guardrails_active: bool
    authenticated_as: Optional[str]
    performance_metrics: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    chroma_stats: Optional[Dict[str, Any]] = None


class AgentStatusChecker:
    """Класс для проверки статуса агента"""

    def __init__(self, agent: AutonomousCognitiveAgent):
        self.agent = agent

    def get_local_status(self) -> AgentStatus:
        """Получить локальный статус агента"""
        status = self.agent.get_status()
        return AgentStatus(**status)

    async def check_api_status(self, url: str = "http://localhost:8000/health") -> Dict[str, Any]:
        """Проверить статус API агента"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    return {
                        "status_code": response.status,
                        "healthy": response.status == 200,
                        "response_time": 0,  # Will be calculated with timing
                        "content": await response.text()
                    }
        except Exception as e:
            return {
                "status_code": None,
                "healthy": False,
                "error": str(e),
                "content": None
            }

    def check_file_system_status(self) -> Dict[str, Any]:
        """Проверить статус файловой системы агента"""
        project_path = Path(self.agent.project_path)

        return {
            "project_exists": project_path.exists(),
            "scan_dir_exists": (project_path / "cognitive_agent" / "scans").exists(),
            "log_dir_exists": Path("logs").exists(),
            "config_dir_exists": (project_path / "agents" / "cognitive_agent" / "config").exists(),
            "total_files": self.agent._count_files(),
            "total_directories": self.agent._count_directories(),
            "languages_detected": self.agent._detect_languages(),
            "frameworks_detected": self.agent._detect_frameworks(),
        }


def main():
    """Основная функция проверки статуса агента"""
    print("🔍 Проверка статуса Cognitive Enterprise Agent...")

    try:
        # Создаем экземпляр enterprise агента
        agent = AutonomousCognitiveAgent()
        checker = AgentStatusChecker(agent)

        print("\n📋 Локальный статус агента:")
        print("="*50)

        local_status = checker.get_local_status()
        print(f"ID агента: {local_status.agent_id}")
        print(f"Запущен: {local_status.running}")
        print(f"Путь проекта: {local_status.project_path}")
        print(f"Последнее сканирование: {local_status.last_scan}")
        print(
            f"Интервал сканирования: {local_status.scan_interval_seconds} сек")
        print(f"AI провайдер: {local_status.ai_provider}")
        print(f"Всего сканирований: {local_status.total_scans}")
        print(f"Всего рекомендаций: {local_status.total_recommendations}")
        print(f"Guardrails загружены: {local_status.guardrails_loaded}")
        print(f"AI вызовов сегодня: {local_status.ai_calls_today}")
        print(f"Уровень успеха памяти: {local_status.memory_success_rate:.2%}")
        print(
            f"Enterprise guardrails активны: {local_status.enterprise_guardrails_active}")

        if local_status.performance_metrics:
            print(f"\n📊 Метрики производительности:")
            perf = local_status.performance_metrics
            print(
                f"  Успешность задач: {perf.get('task_success_rate', 0):.2%}")
            print(
                f"  Успешность AI вызовов: {perf.get('ai_call_success_rate', 0):.2%}")
            if 'avg_scan_duration' in perf:
                print(
                    f"  Средняя длительность сканирования: {perf['avg_scan_duration']:.2f}с")
            if 'avg_response_time' in perf:
                print(
                    f"  Среднее время ответа: {perf['avg_response_time']:.2f}с")
            print(
                f"  Среднее использование CPU: {perf.get('avg_cpu_usage', 0):.2f}%")
            print(
                f"  Среднее использование памяти: {perf.get('avg_memory_usage', 0):.2f}%")

        print(f"\n💾 Статус файловой системы:")
        print("="*50)
        fs_status = checker.check_file_system_status()
        for key, value in fs_status.items():
            print(f"{key}: {value}")

        print(f"\n🌐 Проверка API (если запущен):")
        print("="*50)
        try:
            api_status = asyncio.run(checker.check_api_status())
            print(
                f"Статус API: {'✅ Здоров' if api_status.get('healthy') else '❌ Проблемы'}")
            print(f"Код ответа: {api_status.get('status_code', 'N/A')}")
            if 'error' in api_status:
                print(f"Ошибка: {api_status['error']}")
        except Exception as e:
            print(f"Ошибка проверки API: {e}")

        print(f"\n🎯 Сводка по безопасности:")
        print("="*50)
        print(
            f"AI вызовы ограничены: {local_status.operation_limits.get('max_ai_calls_per_hour')}")
        print(f"Таймаут AI вызовов: {local_status.ai_call_timeout}с")
        print(
            f"Максимальный размер файла: {local_status.operation_limits.get('max_file_size_mb')}MB")
        print(
            f"Максимальное количество файлов за сканирование: {local_status.operation_limits.get('files_per_scan')}")

        print(f"\n📋 Статус AI провайдеров:")
        for provider, status in local_status.ai_providers_status.items():
            print(f"  {provider}: {status.get('status', 'unknown')}")

        if local_status.chroma_stats:
            print(f"\n🔍 Статус ChromaDB:")
            for key, value in local_status.chroma_stats.items():
                print(f"  {key}: {value}")

        print(f"\n✅ Проверка статуса завершена")

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что все зависимости установлены:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Ошибка проверки статуса агента: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
