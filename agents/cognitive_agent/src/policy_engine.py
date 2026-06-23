from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from agents.cognitive_agent.enterprise_guardrails import AccessLevel, EnterpriseGuardrails


class PolicyDecisionType(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    PENDING_APPROVAL = "pending_approval"


@dataclass(frozen=True)
class PolicyDecision:
    decision: PolicyDecisionType
    allowed: bool
    requires_approval: bool
    requires_two_factor: bool
    reason: str
    meta: dict[str, Any]


@dataclass(frozen=True)
class PolicyRequest:
    action: str
    target: str
    context: dict[str, Any] | None = None
    # Если используется enterprise guardrails
    token: str | None = None


class PolicyEngine:
    """Единая точка принятия решений (source of truth) для guardrails.

    На текущем этапе engine:
    - нормализует решения между enterprise guardrails и локальными dangerous patterns
    - возвращает унифицированный PolicyDecision

    В следующих этапах engine будет расширен для execution шагов.
    """

    def __init__(self, enterprise_guardrails: EnterpriseGuardrails | None = None):
        self._enterprise = enterprise_guardrails or EnterpriseGuardrails()

        # Базовые опасные паттерны для target (упрощенно; более глубокая валидация уже есть в BaseCognitiveAgent)
        self._blocked_target_patterns = [
            r"\.\./",
            r"~/",
            r"/etc/",
            r"/root/",
            r"\\Windows",
            r"\.env",
            r"\.pem",
            r"\.key",
        ]

        self._code_ext = (".py", ".js", ".ts")

    @staticmethod
    def _normalize_action(action: str) -> str:
        return (action or "").strip().lower()

    def decide(self, req: PolicyRequest) -> PolicyDecision:
        action = self._normalize_action(req.action)
        target = (req.target or "").strip()
        ctx = req.context or {}

        # 1) Safe read-only actions
        if action in {"read", "scan", "analyze", "list"}:
            return PolicyDecision(
                decision=PolicyDecisionType.ALLOW,
                allowed=True,
                requires_approval=False,
                requires_two_factor=False,
                reason="read-only action allowed",
                meta={"action": action, "target": target},
            )

        # 2) Block obvious dangerous targets
        for pattern in self._blocked_target_patterns:
            if target and re.search(pattern, target, re.IGNORECASE):
                return PolicyDecision(
                    decision=PolicyDecisionType.DENY,
                    allowed=False,
                    requires_approval=False,
                    requires_two_factor=False,
                    reason=f"blocked by target pattern: {pattern}",
                    meta={"action": action, "target": target, "pattern": pattern},
                )

        # 3) Context-based auto-allow for low-risk code edits (must run before enterprise checks)
        if ctx.get("type") in {"bugfix", "hotfix", "typo"} and target.endswith(self._code_ext):
            return PolicyDecision(
                decision=PolicyDecisionType.ALLOW,
                allowed=True,
                requires_approval=False,
                requires_two_factor=False,
                reason="context auto-allow: bugfix/hotfix/typo",
                meta={"action": action, "target": target, "ctx_type": ctx.get("type")},
            )

        # 4) Enterprise guardrails for file access
        if target and action in {"write", "modify", "create", "delete", "execute"}:
            # Map action -> AccessLevel
            access_map = {
                "write": AccessLevel.WRITE,
                "modify": AccessLevel.WRITE,
                "create": AccessLevel.WRITE,
                "delete": AccessLevel.DELETE,
                "execute": AccessLevel.EXECUTE,
            }
            access_level = access_map.get(action)
            if access_level is None:
                return PolicyDecision(
                    decision=PolicyDecisionType.DENY,
                    allowed=False,
                    requires_approval=False,
                    requires_two_factor=False,
                    reason=f"unknown write action: {action}",
                    meta={"action": action, "target": target},
                )

            if not req.token:
                return PolicyDecision(
                    decision=PolicyDecisionType.PENDING_APPROVAL,
                    allowed=False,
                    requires_approval=True,
                    requires_two_factor=False,
                    reason="missing enterprise token",
                    meta={"action": action, "target": target},
                )

            res = self._enterprise.authorize_file_access(req.token, target, access_level)

            if res.get("allowed"):
                return PolicyDecision(
                    decision=PolicyDecisionType.ALLOW,
                    allowed=True,
                    requires_approval=bool(res.get("requires_approval")),
                    requires_two_factor=bool(res.get("requires_two_factor")),
                    reason=res.get("reason") or "access granted",
                    meta={"action": action, "target": target, "rule_description": res.get("rule_description")},
                )

            return PolicyDecision(
                decision=PolicyDecisionType.DENY,
                allowed=False,
                requires_approval=bool(res.get("requires_approval")),
                # Enterprise guardrails may set requires_two_factor=True even when access denied.
                requires_two_factor=bool(res.get("requires_two_factor")),
                reason=res.get("reason") or "access denied",
                meta={"action": action, "target": target, "rule_description": res.get("rule_description")},
            )

        # 4) Context-based auto-allow for low-risk code edits (will be tightened later)
        # NOTE: Must happen BEFORE enterprise-token checks for target requiring write/modify.
        # Also, treat *.py/js/ts targets as code modifications even if action is "modify".
        if ctx.get("type") in {"bugfix", "hotfix", "typo"} and target.endswith(self._code_ext):
            return PolicyDecision(
                decision=PolicyDecisionType.ALLOW,
                allowed=True,
                requires_approval=False,
                requires_two_factor=False,
                reason="context auto-allow: bugfix/hotfix/typo",
                meta={"action": action, "target": target, "ctx_type": ctx.get("type")},
            )

        # 5) For other modifications: require approval by default
        if action in {"write", "modify", "create", "delete"}:
            # If we can evaluate enterprise guardrails, use them.
            if target and action in {"write", "modify", "create", "delete", "execute"}:
                access_map = {
                    "write": AccessLevel.WRITE,
                    "modify": AccessLevel.WRITE,
                    "create": AccessLevel.WRITE,
                    "delete": AccessLevel.DELETE,
                    "execute": AccessLevel.EXECUTE,
                }
                access_level = access_map.get(action)

                if access_level is not None and req.token:
                    res = self._enterprise.authorize_file_access(req.token, target, access_level)
                    if res.get("allowed"):
                        return PolicyDecision(
                            decision=PolicyDecisionType.ALLOW,
                            allowed=True,
                            requires_approval=bool(res.get("requires_approval")),
                            requires_two_factor=bool(res.get("requires_two_factor")),
                            reason=res.get("reason") or "access granted",
                            meta={"action": action, "target": target, "rule_description": res.get("rule_description")},
                        )
                    return PolicyDecision(
                        decision=PolicyDecisionType.DENY,
                        allowed=False,
                        requires_approval=bool(res.get("requires_approval")),
                        requires_two_factor=bool(res.get("requires_two_factor")),
                        reason=res.get("reason") or "access denied",
                        meta={"action": action, "target": target, "rule_description": res.get("rule_description")},
                    )

                # token missing -> pending approval (but doesn't allow operation)
                if not req.token:
                    return PolicyDecision(
                        decision=PolicyDecisionType.PENDING_APPROVAL,
                        allowed=False,
                        requires_approval=True,
                        requires_two_factor=False,
                        reason="missing enterprise token",
                        meta={"action": action, "target": target},
                    )

            return PolicyDecision(
                decision=PolicyDecisionType.PENDING_APPROVAL,
                allowed=False,
                requires_approval=True,
                requires_two_factor=False,
                reason="modification requires approval",
                meta={"action": action, "target": target, "ctx_type": ctx.get("type")},
            )

        return PolicyDecision(
            decision=PolicyDecisionType.DENY,
            allowed=False,
            requires_approval=False,
            requires_two_factor=False,
            reason="default deny",
            meta={"action": action, "target": target},
        )
