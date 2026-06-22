"""Security module for cognitive agent."""

from pathlib import Path
from typing import Any


class SecurityManager:
    """Менеджер безопасности и guardrails"""

    def __init__(self, guardrails_path: Path = None):
        self.guardrails = None
        self.guardrails_loaded = True
        self.allowed_paths = []
        self.blocked_patterns = []
        self.safe_actions = []
        self._load_guardrails(guardrails_path)

    def _load_guardrails(self, guardrails_path: Path):
        """Загрузить правила безопасности с валидацией схемы"""
        try:
            import yaml

            with open(guardrails_path, encoding="utf-8") as f:
                self.guardrails = yaml.safe_load(f)

            # Валидация схемы
            required_keys = ["allowed_paths", "blocked_patterns", "safe_actions", "rules"]
            for key in required_keys:
                if key not in self.guardrails:
                    raise ValueError(f"Missing required key in guardrails: {key}")

            # Валидация правил
            for rule in self.guardrails["rules"]:
                if "pattern" not in rule or "action" not in rule:
                    raise ValueError(f"Invalid rule format: {rule}")

            self.allowed_paths = self.guardrails.get("allowed_paths", [])
            self.blocked_patterns = self.guardrails.get("blocked_patterns", [])
            self.safe_actions = self.guardrails.get("safe_actions", ["read", "scan", "analyze"])

        except Exception as e:
            self.guardrails_loaded = False
            self._load_default_guardrails()

    def _load_default_guardrails(self):
        """Загрузить безопасные значения guardrails по умолчанию"""
        self.guardrails = {
            "allowed_paths": ["^apps/", "^agents/", "^config/"],
            "blocked_patterns": [r"../", r"/etc/", r"~/", r"\.env", r"\.pem", r"\.key"],
            "safe_actions": ["read", "scan", "analyze", "list"],
            "rules": [
                {"pattern": ".*\\.(key|pem|env)$", "action_pattern": ".*", "action": "block"}
            ],
        }
        self.allowed_paths = self.guardrails["allowed_paths"]
        self.blocked_patterns = self.guardrails["blocked_patterns"]
        self.safe_actions = self.guardrails["safe_actions"]

    def is_path_allowed(self, path: str) -> bool:
        """Проверить, разрешен ли путь"""
        import re

        for pattern in self.allowed_paths:
            if re.match(pattern, path):
                return True
        return False

    def is_action_safe(self, action: str) -> bool:
        """Проверить, безопасно ли действие"""
        return action in self.safe_actions
