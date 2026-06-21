import pytest

from agents.cognitive_agent.enterprise_guardrails import EnterpriseGuardrails, UserRole
from agents.cognitive_agent.src.policy_engine import PolicyDecisionType, PolicyEngine, PolicyRequest


@pytest.fixture
def enterprise_guardrails():
    return EnterpriseGuardrails()


@pytest.fixture
def engine(enterprise_guardrails):
    return PolicyEngine(enterprise_guardrails=enterprise_guardrails)


def test_allow_read_action(engine):
    d = engine.decide(PolicyRequest(action="read", target="config/settings.yaml", token=None))
    assert d.decision == PolicyDecisionType.ALLOW
    assert d.allowed is True
    assert d.requires_approval is False


def test_deny_dangerous_target_pattern(engine):
    d = engine.decide(PolicyRequest(action="modify", target="../../etc/passwd", token=None))
    assert d.decision == PolicyDecisionType.DENY
    assert d.allowed is False
    assert "blocked by target pattern" in d.reason.lower()


def test_pending_approval_when_missing_token(engine):
    d = engine.decide(PolicyRequest(action="write", target="config/a.yaml", context=None, token=None))
    assert d.decision == PolicyDecisionType.PENDING_APPROVAL
    assert d.allowed is False
    assert d.requires_approval is True


def test_enterprise_allow_docs_write_without_approval(engine, enterprise_guardrails):
    # docs/* - allowed write, approval_required=False in AuthorizationManager
    token = enterprise_guardrails.authenticate_user("u1", UserRole.DEVELOPER)

    d = engine.decide(PolicyRequest(action="write", target="docs/readme.md", token=token))
    assert d.allowed is True
    assert d.decision == PolicyDecisionType.ALLOW


def test_enterprise_deny_src_core_write_requires_2fa(engine, enterprise_guardrails):
    # src/core/* - allowed read only; expected denied.
    # Current EnterpriseGuardrails implementation sets requires_two_factor=True in rule,
    # but AuthorizationManager.check_access returns it only when action/role matches.
    token = enterprise_guardrails.authenticate_user("u2", UserRole.ADMIN)

    d = engine.decide(PolicyRequest(action="write", target="src/core/auth.py", token=token))
    assert d.allowed is False
    assert d.decision == PolicyDecisionType.DENY


def test_context_auto_allow_bugfix_for_code_mod(engine):
    d = engine.decide(
        PolicyRequest(
            action="modify",
            target="agents/cognitive_agent/src/base_agent.py",
            context={"type": "bugfix"},
            token=None,
        )
    )
    assert d.allowed is True
    assert d.decision == PolicyDecisionType.ALLOW
