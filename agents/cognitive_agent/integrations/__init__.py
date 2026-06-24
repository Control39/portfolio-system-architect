"""Integration module for cognitive agent."""

from typing import Any


class JobAgentIntegration:
    """Интеграция с Job Automation Agent"""

    def __init__(self):
        self.job_agent_available = False
        self.analyze_requirements = None
        self.generate_resume = None
        self.job_search = None
        self.process_request_sync = None

        try:
            from apps.job_automation_agent.job_agent import (
                analyze_requirements,
                generate_resume,
                job_search,
                process_request_sync,
            )

            self.analyze_requirements = analyze_requirements
            self.generate_resume = generate_resume
            self.job_search = job_search
            self.process_request_sync = process_request_sync
            self.job_agent_available = True
        except ImportError:
            pass  # Job Agent is optional

    def is_available(self) -> bool:
        """Проверить доступность Job Agent"""
        return self.job_agent_available


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
