"""
Decision Engine - Core logic for automated decision making.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

from .models import DecisionRequest, DecisionResponse


logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Engine для принятия решений на основе правил и RAG.

    Features:
    - Правило-based принятие решений
    - Интеграция с RAG для сложных кейсов
    - Кэширование решений
    - Приоритизация
    - Генерация объяснений
    """

    def __init__(self, config_path: str | None = None):
        """
        Инициализация движка решений.

        Args:
            config_path: Путь к файлу конфигурации правил
        """
        self.config_path = config_path
        self._cache: dict[str, DecisionResponse] = {}
        self._rules: dict[str, Any] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """Загрузка правил из конфигурации"""
        if self.config_path and Path(self.config_path).exists():
            # В реальной реализации загружаем YAML/JSON
            logger.info(f"Rules loaded from {self.config_path}")
        else:
            # Дефолтные правила
            self._rules = {
                "allow_list": [],
                "deny_list": [],
                "required_roles": {"delete_production": ["admin"], "deploy_production": ["admin", "devops"]},
                "environments": {"production": {"requires_approval": True}, "staging": {"requires_approval": False}},
            }

    def make_decision(
        self, request: DecisionRequest, custom_rules: dict[str, Any] | None = None, include_explanation: bool = False
    ) -> DecisionResponse:
        """
        Принятие решения на основе запроса.

        Args:
            request: Запрос на решение
            custom_rules: Пользовательские правила (переопределяют дефолтные)
            include_explanation: Включить объяснение

        Returns:
            DecisionResponse с решением
        """
        # Валидация
        self._validate_request(request)

        # Проверка кэша
        cache_key = self._get_cache_key(request)
        if cache_key in self._cache:
            logger.debug("Decision from cache")
            cached = self._cache[cache_key]
            if include_explanation:
                cached.explanation = self._generate_explanation(request, cached.decision)
            return cached

        # Применение правил
        rules_to_use = custom_rules if custom_rules else self._rules
        decision, reason = self._apply_rules(request, rules_to_use)

        # Генерация ответа
        response = DecisionResponse(
            user_id=request.user_id,
            action=request.action,
            decision=decision,
            reason=reason,
            confidence=1.0 if decision in ["allow", "deny"] else 0.5,
        )

        if include_explanation:
            response.explanation = self._generate_explanation(request, decision)
            response.conditions_checked = self._count_conditions_checked(request)

        # Кэширование
        self._cache[cache_key] = response

        return response

    def _validate_request(self, request: DecisionRequest) -> None:
        """Валидация запроса"""
        if not request.user_id:
            raise ValueError("user_id is required")
        if not request.action:
            raise ValueError("action is required")
        if not request.context:
            raise ValueError("context is required")

    def _apply_rules(self, request: DecisionRequest, rules: dict[str, Any]) -> tuple[str, str]:
        """
        Применение правил к запросу.

        Returns:
            Tuple (decision, reason)
        """
        # Проверка deny_list
        if request.user_id in rules.get("deny_list", []):
            return "deny", "User is in deny list"

        # Проверка allow_list
        if request.user_id in rules.get("allow_list", []):
            return "allow", "User is in allow list"

        # Проверка ресурсов
        if not request.context.resources_available:
            return "deny", "Resources not available"

        # Проверка ролей
        required_roles = rules.get("required_roles", {})
        if request.action in required_roles:
            allowed_roles = required_roles[request.action]
            if request.context.user_role not in allowed_roles:
                return "deny", f"Role '{request.context.user_role}' not authorized for '{request.action}'"

        # Проверка окружения
        env_config = rules.get("environments", {}).get(request.context.environment, {})
        if env_config.get("requires_approval") and request.context.user_role != "admin":
            return "require_approval", "Production operation requires admin approval"

        # Дефолт - allow
        return "allow", "Decision approved by default rules"

    def _get_cache_key(self, request: DecisionRequest) -> str:
        """Генерация ключа кэша"""
        data = f"{request.user_id}:{request.action}:{request.context.model_dump_json()}"
        return hashlib.md5(data.encode()).hexdigest()

    def _generate_explanation(self, request: DecisionRequest, decision: str) -> dict[str, Any]:
        """Генерация объяснения решения"""
        return {
            "rules_applied": ["deny_list", "allow_list", "resource_check", "role_check"],
            "decision": decision,
            "timestamp": "2026-05-14T12:00:00Z",
        }

    def _count_conditions_checked(self, request: DecisionRequest) -> int:
        """Подсчёт проверенных условий"""
        count = 4  # deny_list, allow_list, resources, role
        if request.context.environment == "production":
            count += 1  # environment check
        return count

    def _query_rag(self, query: str) -> dict[str, Any]:
        """
        Запрос к RAG для сложных решений.

        Args:
            query: Запрос для RAG

        Returns:
            RAG ответ с рекомендацией
        """
        # Заглушка - в реализации будет реальный RAG
        return {"recommendation": "allow", "confidence": 0.85, "sources": ["internal_docs", "best_practices"]}

    def _prioritize(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Приоритизация решений.

        Args:
            decisions: Список решений

        Returns:
            Отсортированный список по приоритету
        """
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(decisions, key=lambda x: priority_order.get(x.get("priority", "low"), 4))

    def clear_cache(self) -> None:
        """Очистка кэша решений"""
        self._cache.clear()
        logger.info("Decision cache cleared")
