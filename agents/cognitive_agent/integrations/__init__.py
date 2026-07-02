"""Integration module for cognitive agent."""

from typing import Any


class JobAgentIntegration:
    """Интеграция с Job Automation Agent (с ленивой загрузкой)"""

    def __init__(self):
        self._job_agent = None
        self.available = False

    def _load_job_agent(self):
        """Ленивая загрузка Job Agent"""
        if self._job_agent is None:
            try:
                from apps.job_automation_agent.job_agent import (
                    analyze_requirements,
                    generate_resume,
                    job_search,
                    process_request_sync,
                )

                self._job_agent = {
                    "analyze_requirements": analyze_requirements,
                    "generate_resume": generate_resume,
                    "job_search": job_search,
                    "process_request_sync": process_request_sync,
                }
                self.available = True
            except ImportError:
                self.available = False

    def is_available(self) -> bool:
        """Проверить доступность Job Agent"""
        if self._job_agent is None:
            self._load_job_agent()
        return self.available

    # Proxy methods for backward compatibility
    @property
    def job_agent_available(self) -> bool:
        return self.is_available()

    @property
    def analyze_requirements(self):
        self._load_job_agent()
        return self._job_agent.get("analyze_requirements") if self._job_agent else None

    @property
    def generate_resume(self):
        self._load_job_agent()
        return self._job_agent.get("generate_resume") if self._job_agent else None

    @property
    def job_search(self):
        self._load_job_agent()
        return self._job_agent.get("job_search") if self._job_agent else None

    @property
    def process_request_sync(self):
        self._load_job_agent()
        return self._job_agent.get("process_request_sync") if self._job_agent else None


class AIProviderIntegration:
    """Интеграция с AI Provider Manager"""

    def __init__(self):
        self._provider_manager = None

        try:
            from apps.ai_provider_manager.src.ai_provider_manager import (
                chat_with_fallback,
                get_provider_manager,
            )

            self.chat_with_fallback = chat_with_fallback
            self._get_provider_manager_func = get_provider_manager
        except ImportError:
            pass

    def get_chat_function(self):
        """Получить функцию чата"""
        return getattr(self, "chat_with_fallback", None)

    def get_provider_manager(self):
        """Получить менеджер провайдеров"""
        return getattr(self, "_get_provider_manager_func", None)
